from django.db import models
from django.conf import settings

class LostItem(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lost_items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    lost_date = models.DateField()
    # general_location is coarse and always public (e.g. "Library", "Canteen").
    # location is the specific/exact spot — private to the owner and admins, so
    # it can't be used to fabricate a convincing fake claim.
    general_location = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='lost/', blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lost: {self.name}"


class FoundItem(models.Model):
    found_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='found_items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    found_date = models.DateField()
    # general_location is coarse and always public (e.g. "Library", "Canteen").
    # location is the specific/exact spot — private, same reasoning as LostItem.
    general_location = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='found/', blank=True, null=True)
    is_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Found: {self.name}"