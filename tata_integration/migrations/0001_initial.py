from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('leads', '0007_leadstage_lead_stage_teammember_leadnote_and_more'),
    ]
    
    operations = [
        migrations.CreateModel(
            name='TataCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_id', models.CharField(max_length=100, unique=True)),
                ('uuid', models.CharField(max_length=100)),
                ('customer_number', models.CharField(max_length=20)),
                ('agent_number', models.CharField(blank=True, max_length=20, null=True)),
                ('agent_name', models.CharField(blank=True, max_length=100, null=True)),
                ('direction', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('start_stamp', models.DateTimeField()),
                ('end_stamp', models.DateTimeField(blank=True, null=True)),
                ('duration', models.IntegerField(default=0)),
                ('recording_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leads.lead')),
            ],
        ),
        migrations.CreateModel(
            name='CallNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('agent_disposition', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tata_integration.tatacall')),
            ],
        ),
    ]