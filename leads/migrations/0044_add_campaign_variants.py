# Generated migration for campaign variants

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0043_aicallingagent'),
    ]

    operations = [
        migrations.AddField(
            model_name='dripcampaign',
            name='variant_group',
            field=models.CharField(blank=True, help_text='Group ID for campaign variants (e.g., \'spjday\')', max_length=100),
        ),
        migrations.AddField(
            model_name='dripcampaign',
            name='is_active_variant',
            field=models.BooleanField(default=True, help_text='Whether this variant is currently active for new subscribers'),
        ),
    ]
