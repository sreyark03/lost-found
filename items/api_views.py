from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LostItem, FoundItem
from .serializers import LostItemSerializer, FoundItemSerializer

class LostItemViewSet(viewsets.ModelViewSet):
    serializer_class = LostItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LostItem.objects.filter(is_resolved=False).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        if self.request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Admins cannot report lost items.')
        serializer.save(reported_by=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.reported_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit lost items you reported.')
        serializer.save()

    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        item = self.get_object()
        if item.reported_by != request.user:
            return Response(
                {'detail': 'You can only resolve your own lost item.'},
                status=status.HTTP_403_FORBIDDEN
            )
        item.is_resolved = True
        item.save()
        return Response(LostItemSerializer(item, context={'request': request}).data)


class FoundItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoundItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FoundItem.objects.filter(is_claimed=False).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        if self.request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Admins cannot report found items.')
        serializer.save(found_by=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.found_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit found items you reported.')
        serializer.save()
