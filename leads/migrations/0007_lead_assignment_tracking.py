# Generated migration for lead assignment tracking

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0006_property_zohoconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadAssignmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('sla_deadline', models.DateTimeField()),
                ('is_overdue', models.BooleanField(default=False)),
                ('overdue_at', models.DateTimeField(blank=True, null=True)),
                ('reassigned_at', models.DateTimeField(blank=True, null=True)),
                ('reason', models.CharField(default='initial_assignment', max_length=200)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments_made', to='leads.teammember')),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.teammember')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_history', to='leads.lead')),
            ],
            options={
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='RoundRobinQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_assigned_at', models.DateTimeField(blank=True, null=True)),
                ('assignment_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('team_member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='leads.teammember')),
            ],
            options={
                'ordering': ['last_assigned_at', 'assignment_count'],
            },
        ),
    ]