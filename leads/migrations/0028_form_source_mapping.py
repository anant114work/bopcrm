# Generated migration for FormSourceMapping model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0027_add_sync_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormSourceMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_name', models.CharField(help_text='Exact form name or keyword from Meta/source', max_length=200, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_mappings', to='leads.project')),
            ],
            options={
                'verbose_name': 'Form Source Mapping',
                'verbose_name_plural': 'Form Source Mappings',
                'ordering': ['form_name'],
            },
        ),
    ]
