from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0040_bookingsourcecategory_callkaroagent_agent_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='leads.project')),
                ('team_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.teammember')),
            ],
            options={
                'unique_together': {('project', 'team_member')},
            },
        ),
    ]
