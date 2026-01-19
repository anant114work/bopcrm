from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0042_alter_email_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='AICallingAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('agent_id', models.CharField(max_length=200, unique=True)),
                ('system_prompt', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_agents', to='leads.project')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
