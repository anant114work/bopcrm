from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0041_projectteammember'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
