from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import ClaimRequest
from .serializers import (
    ClaimRequestSerializer,
    ClaimReviewSerializer,
    ClaimResubmitSerializer,
    ClaimFinderRequestSerializer,
    ClaimFinderResponseSerializer,
)

class ClaimViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return ClaimRequest.objects.all().order_by('-created_at')
        return ClaimRequest.objects.filter(claimant=user).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError

        lost_item = serializer.validated_data['lost_item']
        found_item = serializer.validated_data['found_item']

        if found_item.found_by == self.request.user:
            raise ValidationError({'found_item': 'You cannot claim an item you reported as found.'})

        # Only the person who actually reported the lost item can use it as proof.
        if lost_item.reported_by != self.request.user:
            raise ValidationError({'lost_item': 'You can only claim an item using a lost report that you submitted yourself.'})

        # The lost report used as "proof" must actually correspond to the found item
        # being claimed (e.g. you can't use a lost "pen" report to claim a found "book").
        lost_name = lost_item.name.strip().lower()
        found_name = found_item.name.strip().lower()
        if lost_name != found_name and lost_name not in found_name and found_name not in lost_name:
            raise ValidationError({'lost_item': 'This lost item does not match the found item you are trying to claim.'})

        serializer.save(claimant=self.request.user)

    def update(self, request, *args, **kwargs):
        # Claims are never edited directly — proof of ownership can only change via
        # the resubmit action (and only while status is more_info_required), and
        # status/admin_note can only change via the review action. This closes off
        # a claimant (or anyone) editing another user's claim through a plain PATCH.
        return Response(
            {'detail': 'Claims cannot be edited directly. Use the resubmit or review actions.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    @transaction.atomic
    def review(self, request, pk=None):
        claim = self.get_object()
        if not request.user.is_admin_user():
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)
        if claim.status not in ('pending', 'more_info_required', 'waiting_for_finder_response'):
            return Response({'detail': 'This claim has already been finalized.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClaimReviewSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        reviewed = serializer.save(reviewed_by=request.user, has_new_finder_response=False)

        if reviewed.status == 'approved':
            reviewed.found_item.is_claimed = True
            reviewed.found_item.save()
            reviewed.lost_item.is_resolved = True
            reviewed.lost_item.save()

        return Response(ClaimRequestSerializer(reviewed, context={'request': request}).data)

    @action(detail=True, methods=['patch'])
    def resubmit(self, request, pk=None):
        claim = self.get_object()
        if claim.claimant != request.user:
            return Response({'detail': 'You can only resubmit your own claim.'}, status=status.HTTP_403_FORBIDDEN)
        if claim.status != 'more_info_required':
            return Response({'detail': 'This claim is not awaiting more information.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClaimResubmitSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # updated_at bumps automatically (auto_now=True); status goes back to
        # pending so the claim reappears in the admin's review queue.
        updated = serializer.save(status='pending')

        return Response(ClaimRequestSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='request-finder-info')
    def request_finder_info(self, request, pk=None):
        """Admin -> finder: ask the person who found the item for more identifying
        detail before deciding on a claim. Never visible to the claimant."""
        claim = self.get_object()
        if not request.user.is_admin_user():
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)
        if claim.status in ('approved', 'rejected'):
            return Response({'detail': 'This claim has already been finalized.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClaimFinderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claim.finder_request_message = serializer.validated_data['message']
        claim.status = 'waiting_for_finder_response'
        claim.has_new_finder_response = False
        claim.save()

        return Response(ClaimRequestSerializer(claim, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='finder-respond')
    def finder_respond(self, request, pk=None):
        """Finder -> admin: reply to a request for more information. Looked up
        directly (bypassing get_queryset, which only returns the claimant's own
        claims for non-admins) since the finder is usually not the claimant."""
        claim = get_object_or_404(ClaimRequest, pk=pk)
        if claim.found_item.found_by != request.user:
            return Response({'detail': 'Only the finder can respond to this request.'}, status=status.HTTP_403_FORBIDDEN)
        if claim.status != 'waiting_for_finder_response':
            return Response({'detail': 'This claim is not awaiting a response from you.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClaimFinderResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claim.finder_response_note = serializer.validated_data.get('verification_notes', '')
        claim.finder_responded_at = timezone.now()
        claim.has_new_finder_response = True
        claim.status = 'pending'
        claim.save()

        return Response(ClaimRequestSerializer(claim, context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='finder-requests')
    def finder_requests(self, request):
        """Claims where the current user is the finder and an admin is waiting
        on them for more information — surfaced on the home page."""
        qs = ClaimRequest.objects.filter(
            found_item__found_by=request.user,
            status='waiting_for_finder_response',
        ).order_by('-created_at')
        return Response(ClaimRequestSerializer(qs, many=True, context={'request': request}).data)
