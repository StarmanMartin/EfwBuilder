# Generated by Django 4.0.4 on 2022-09-12 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0014_umlelement_x_umlelement_y'),
    ]

    operations = [
        migrations.RenameField(
            model_name='umlfield',
            old_name='segment',
            new_name='layer',
        ),
    ]