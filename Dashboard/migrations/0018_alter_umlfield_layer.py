# Generated by Django 4.0.4 on 2022-09-12 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0017_remove_umlfield_sub_field_umlfield_sub_field_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='umlfield',
            name='layer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.umllayer'),
        ),
    ]
