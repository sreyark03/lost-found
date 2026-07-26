from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0002_claim_more_info_required_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimrequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('more_info_required', 'More Info Required'),
                    ('waiting_for_finder_response', 'Waiting for Finder Response'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='pending',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='claimrequest',
            name='finder_request_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='claimrequest',
            name='finder_response_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='claimrequest',
            name='finder_responded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='claimrequest',
            name='has_new_finder_response',
            field=models.BooleanField(default=False),
        ),
    ]
