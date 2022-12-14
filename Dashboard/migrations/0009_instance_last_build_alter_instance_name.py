# Generated by Django 4.0.4 on 2022-08-31 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0008_instance_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='last_build',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(help_text='Unique name of the EFW instance. This name cannot be changed!', max_length=50),
        ),
    ]
