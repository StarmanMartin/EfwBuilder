# Generated by Django 4.0.4 on 2022-09-14 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0020_umlelement_token_alter_umlfield_layer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='umlelement',
            name='extends',
            field=models.ManyToManyField(related_name='extended_by', to='Dashboard.umlelement'),
        ),
    ]