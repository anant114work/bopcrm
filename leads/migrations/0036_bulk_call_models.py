# Generated migration for Bulk Call models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0035_auto_whatsapp_campaign'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkCallCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('file_name', models.CharField(max_length=200)),
                ('total_numbers', models.IntegerField(default=0)),
                ('completed_calls', models.IntegerField(default=0)),
                ('successful_calls', models.IntegerField(default=0)),
                ('failed_calls', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('paused', 'Paused')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BulkCallRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('phone_number', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('calling', 'Calling'), ('connected', 'Connected'), ('failed', 'Failed'), ('no_answer', 'No Answer'), ('busy', 'Busy')], default='pending', max_length=20)),
                ('call_id', models.CharField(blank=True, max_length=100)),
                ('initiated_at', models.DateTimeField(blank=True, null=True)),
                ('connected_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('duration_seconds', models.IntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('api_response', models.JSONField(blank=True, default=dict)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_records', to='leads.bulkcallcampaign')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]