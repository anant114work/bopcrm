# Generated migration for integration models

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0025_merge_20251114_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page_id', models.CharField(max_length=100)),
                ('access_token', models.TextField()),
                ('app_id', models.CharField(blank=True, max_length=100)),
                ('app_secret', models.CharField(blank=True, max_length=200)),
                ('user_access_token', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GoogleSheetsConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sheet_url', models.URLField()),
                ('sheet_name', models.CharField(default='Sheet1', max_length=100)),
                ('service_account_json', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]