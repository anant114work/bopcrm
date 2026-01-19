# Generated migration for AI Agent models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0046_alter_teammember_email_delete_aicallingagent'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('agent_id', models.CharField(help_text='Call Karo AI agent ID', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_agents', to='leads.project')),
            ],
            options={
                'ordering': ['project__name', 'name'],
            },
        ),
        migrations.CreateModel(
            name='AICallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('initiated', 'Initiated'), ('connected', 'Connected'), ('failed', 'Failed'), ('no_answer', 'No Answer')], default='initiated', max_length=20)),
                ('call_id', models.CharField(blank=True, max_length=100)),
                ('initiated_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.aiagent')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_call_logs', to='leads.lead')),
            ],
            options={
                'ordering': ['-initiated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='aicalllog',
            index=models.Index(fields=['lead', 'status'], name='leads_aical_lead_id_b8c9e5_idx'),
        ),
        migrations.AddIndex(
            model_name='aicalllog',
            index=models.Index(fields=['phone_number', 'initiated_at'], name='leads_aical_phone_n_a7f2d1_idx'),
        ),
    ]
