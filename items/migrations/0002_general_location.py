from django.db import migrations, models


def backfill_general_location(apps, schema_editor):
    LostItem = apps.get_model('items', 'LostItem')
    FoundItem = apps.get_model('items', 'FoundItem')
    # Existing rows have no way to auto-split "general" from "exact" location,
    # so we copy the current value across as a reasonable starting point —
    # owners/admins can edit it to be coarser later if they want.
    for item in LostItem.objects.exclude(location=''):
        item.general_location = item.location
        item.save(update_fields=['general_location'])
    for item in FoundItem.objects.exclude(location=''):
        item.general_location = item.location
        item.save(update_fields=['general_location'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lostitem',
            name='general_location',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='founditem',
            name='general_location',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.RunPython(backfill_general_location, noop_reverse),
    ]
