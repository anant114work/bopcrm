# Generated migration for adding agent_id to BulkCallCampaign

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0036_bulk_call_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkcallcampaign',
            name='agent_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]