# Generated migration for Auto WhatsApp Campaign

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0034_merge_0028_form_source_mapping_0033_add_delay_minutes'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoWhatsAppCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('delay_minutes', models.IntegerField(default=0, help_text='Delay in minutes before sending (0 = immediate)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auto_whatsapp_campaigns', to='leads.project')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.whatsapptemplate')),
            ],
            options={
                'verbose_name': 'Auto WhatsApp Campaign',
                'verbose_name_plural': 'Auto WhatsApp Campaigns',
                'ordering': ['-created_at'],
            },
        ),
    ]
