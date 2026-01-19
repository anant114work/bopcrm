# Generated migration for call report models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0038_calllog_call_sid_alter_bulkcallrecord_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallReportUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('filename', models.CharField(max_length=255)),
                ('total_records', models.IntegerField(default=0)),
                ('matched_records', models.IntegerField(default=0)),
                ('unmatched_records', models.IntegerField(default=0)),
                ('uploaded_by', models.CharField(default='Admin', max_length=100)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='CallReportRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('agent', models.CharField(blank=True, max_length=100)),
                ('version', models.CharField(blank=True, max_length=10)),
                ('call_date', models.DateField(blank=True, null=True)),
                ('call_time', models.DateTimeField(blank=True, null=True)),
                ('disposition', models.TextField(blank=True)),
                ('call_duration', models.FloatField(blank=True, null=True)),
                ('call_recording', models.URLField(blank=True)),
                ('try_count', models.IntegerField(default=0)),
                ('hangup_reason', models.CharField(blank=True, max_length=100)),
                ('cost', models.FloatField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=100)),
                ('project', models.CharField(blank=True, max_length=200)),
                ('campaign_type', models.CharField(blank=True, max_length=100)),
                ('lead_source', models.CharField(blank=True, max_length=50)),
                ('conversion_status', models.CharField(blank=True, max_length=10)),
                ('disposition_reason', models.TextField(blank=True)),
                ('x_model_used', models.CharField(blank=True, max_length=50)),
                ('variable_name', models.CharField(blank=True, max_length=100)),
                ('is_matched', models.BooleanField(default=False)),
                ('matched_call_log', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.calllog')),
                ('matched_lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leads.lead')),
                ('upload', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='leads.callreportupload')),
            ],
            options={
                'ordering': ['-call_time'],
            },
        ),
    ]