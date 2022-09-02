# Generated by Django 4.0.4 on 2022-08-31 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Adminview', '0006_alter_gitinstance_last_build_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gitinstance',
            name='last_build',
        ),
        migrations.AlterField(
            model_name='gitinstance',
            name='name',
            field=models.CharField(help_text='Unique name of the git repo. This name cannot be changed!', max_length=50, unique=True),
        ),
    ]
