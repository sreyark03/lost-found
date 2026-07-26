from rest_framework import serializers
from .models import ClaimRequest
from items.serializers import LostItemSerializer, FoundItemSerializer

REVIEW_STATUSES = ('approved', 'rejected', 'more_info_required')


class ClaimRequestSerializer(serializers.ModelSerializer):
    claimant = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    lost_item_name = serializers.CharField(source='lost_item.name', read_only=True)
    found_item_name = serializers.CharField(source='found_item.name', read_only=True)

    # Full nested detail for the admin verification page (and the claimant's own
    # lost item). FoundItemSerializer itself hides the description unless the
    # viewer is the finder or an admin, so this stays safe for public claimants too.
    lost_item_detail = LostItemSerializer(source='lost_item', read_only=True)
    found_item_detail = FoundItemSerializer(source='found_item', read_only=True)

    # Finder contact info stays hidden until the claim is approved, regardless
    # of the current status (pending / more_info_required / rejected / etc).
    finder_username = serializers.SerializerMethodField()
    finder_email = serializers.SerializerMethodField()

    # Admin-only finder verification block — full identity + contact details,
    # used solely on the Claim Verification page. Never populated for anyone
    # other than an admin, regardless of claim status.
    finder_info = serializers.SerializerMethodField()

    class Meta:
        model = ClaimRequest
        fields = '__all__'
        read_only_fields = [
            'claimant', 'status', 'admin_note',
            'reviewed_by', 'created_at', 'updated_at',
            'finder_request_message', 'finder_response_note',
            'finder_responded_at', 'has_new_finder_response',
        ]

    def _is_admin(self):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        return bool(user) and user.is_authenticated and user.is_admin_user()

    def get_finder_username(self, obj):
        if obj.status == 'approved':
            return obj.found_item.found_by.username
        return None

    def get_finder_email(self, obj):
        if obj.status == 'approved':
            return obj.found_item.found_by.email
        return None

    def get_finder_info(self, obj):
        if not self._is_admin():
            return None
        finder = obj.found_item.found_by
        full_name = finder.get_full_name().strip()
        return {
            'username': finder.username,
            'full_name': full_name or None,
            'email': finder.email or None,
            'phone_number': finder.phone_number or None,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        is_admin = bool(user) and user.is_authenticated and user.is_admin_user()
        is_finder = bool(user) and user.is_authenticated and instance.found_item.found_by_id == getattr(user, 'id', None)
        is_this_claimant = bool(user) and user.is_authenticated and instance.claimant_id == getattr(user, 'id', None)

        # The found item's full details (photo, description, exact location, who
        # found it) are hidden from the public by FoundItemSerializer itself.
        # But once someone has actually submitted this specific claim, they're
        # allowed to see what they're claiming — to visually confirm it's really
        # theirs — without that exposure extending to anyone who hasn't claimed
        # it. This is scoped to exactly this claim/found-item pair.
        if is_this_claimant and not (is_admin or is_finder) and data.get('found_item_detail') is not None:
            found_item = instance.found_item
            request_for_url = self.context.get('request')
            image_url = None
            if found_item.image:
                image_url = request_for_url.build_absolute_uri(found_item.image.url) if request_for_url else found_item.image.url
            data['found_item_detail'] = {
                **data['found_item_detail'],
                'description': found_item.description,
                'location': found_item.location,
                'image_url': image_url,
                'found_by': found_item.found_by.username,
            }

        # The admin<->finder verification side-channel is never shown to the
        # claimant (or anyone else) — only to the admin and the finder themselves.
        if not (is_admin or is_finder):
            data.pop('finder_request_message', None)
            data.pop('finder_response_note', None)
            data.pop('finder_responded_at', None)
            data.pop('has_new_finder_response', None)
        return data


class ClaimReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimRequest
        fields = ['status', 'admin_note']

    def validate_status(self, value):
        if value not in REVIEW_STATUSES:
            raise serializers.ValidationError(
                'Status must be one of: approved, rejected, more_info_required.'
            )
        return value


class ClaimResubmitSerializer(serializers.ModelSerializer):
    """Used only by ClaimViewSet.resubmit — lets the claimant update their
    proof of ownership after the admin requests more information."""
    class Meta:
        model = ClaimRequest
        fields = ['message']
        extra_kwargs = {'message': {'required': True, 'allow_blank': False}}


class ClaimFinderRequestSerializer(serializers.Serializer):
    """Used only by ClaimViewSet.request_finder_info — the admin's message to
    the finder asking for more identifying detail."""
    message = serializers.CharField(allow_blank=False)


class ClaimFinderResponseSerializer(serializers.Serializer):
    """Used only by ClaimViewSet.finder_respond — the finder's additional
    verification notes (the found item's own description/image are updated
    separately, directly through the found-items endpoint)."""
    verification_notes = serializers.CharField(allow_blank=True, required=False)
