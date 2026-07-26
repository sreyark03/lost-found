from rest_framework import serializers
from .models import LostItem, FoundItem


class LostItemSerializer(serializers.ModelSerializer):
    reported_by = serializers.StringRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    # Required on every new report even though the model allows blank (for
    # migration safety on old rows) — public visibility depends on this field
    # existing, so new reports shouldn't be allowed to skip it.
    general_location = serializers.CharField(required=True, allow_blank=False, max_length=100)

    class Meta:
        model = LostItem
        fields = '__all__'
        read_only_fields = ['reported_by', 'is_resolved', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        is_owner = bool(user) and user.is_authenticated and instance.reported_by_id == getattr(user, 'id', None)
        is_admin = bool(user) and user.is_authenticated and user.is_admin_user()
        # Public users only get name, photo, general location, and date lost.
        # The full description, exact location, and who reported it are only
        # for the report owner and admins — this stops the details from being
        # used to fabricate a convincing but fake ownership claim.
        if not (is_owner or is_admin):
            data.pop('description', None)
            data.pop('location', None)
            data.pop('reported_by', None)
        return data


class FoundItemSerializer(serializers.ModelSerializer):
    found_by = serializers.StringRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    general_location = serializers.CharField(required=True, allow_blank=False, max_length=100)

    class Meta:
        model = FoundItem
        fields = '__all__'
        read_only_fields = ['found_by', 'is_claimed', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        is_owner = bool(user) and user.is_authenticated and instance.found_by_id == getattr(user, 'id', None)
        is_admin = bool(user) and user.is_authenticated and user.is_admin_user()
        # Public users (and other students) only get name, general location,
        # and date found. The photo, full description, exact location, and who
        # reported it are only for the finder and admins by default — this is
        # the strictest of the two, since the found item's details are the
        # actual "proof" a real owner would need to have already known before
        # ever seeing them here.
        #
        # A claimant who has submitted a claim on this exact found item gets
        # these fields back too, but that unlock lives in ClaimRequestSerializer
        # (scoped to that one relationship) — this serializer stays unaware of
        # claims entirely, so the standalone /found-items/ listing never leaks
        # them just because *some* claim exists somewhere.
        if not (is_owner or is_admin):
            data.pop('description', None)
            data.pop('location', None)
            data.pop('image', None)
            data.pop('image_url', None)
            data.pop('found_by', None)
        return data
