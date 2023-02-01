from django.db import migrations


def save_git_default(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    GitInstance = apps.get_model('Adminview', 'GitInstance')
    actives = GitInstance.objects.filter(is_active=True)
    if len(actives) == 0:
        GitInstance.objects.get_active(name='Main EFW', url="https://github.com/ComPlat/ELN_file_watcher.git",
                                       branch="server_build", is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ('Adminview', '0002_gitinstance_branch'),
    ]

    operations = [
        migrations.RunPython(save_git_default),
    ]
