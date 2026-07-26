from django.db import models
from django.conf import settings
from items.models import LostItem, FoundItem

class ClaimRequest(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('more_info_required', 'More Info Required'),
        ('waiting_for_finder_response', 'Waiting for Finder Response'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name='claims')
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE, related_name='claims')
    message = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS, default='pending')
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_claims'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin <-> finder side-channel, used when the admin needs the finder to add
    # more identifying detail before a decision can be made. Never exposed to
    # the claimant.
    finder_request_message = models.TextField(blank=True)
    finder_response_note = models.TextField(blank=True)
    finder_responded_at = models.DateTimeField(null=True, blank=True)
    has_new_finder_response = models.BooleanField(default=False)

    def __str__(self):
        return f"Claim by {self.claimant.username} - {self.status}"
