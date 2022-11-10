# Generated by Django 4.0.4 on 2022-10-13 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Adminview', '0007_remove_gitinstance_last_build_alter_gitinstance_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElnConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='Eln connection!')),
                ('active', models.BooleanField()),
                ('token', models.CharField(blank=True, default=None, max_length=255, null=True)),
            ],
        ),
    ]
