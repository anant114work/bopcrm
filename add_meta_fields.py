from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='meta_lead_id',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='source',
            field=models.CharField(max_length=50, default='Meta'),
        ),
        migrations.AddField(
            model_name='lead',
            name='campaign_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='adset_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='ad_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='form_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='campaign_spend',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='lead',
            name='adset_spend',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='lead',
            name='ad_spend',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
    ]