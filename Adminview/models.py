import glob
import json
import os
import shutil
import subprocess

import requests
from django.conf import settings
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ModelForm, CharField, PasswordInput
from django.utils.translation import gettext_lazy as _
from sdc_tools.django_extension.forms import AbstractSearchForm

UserModel = get_user_model()


TYPE_CHOISES = (
    ('file', _('File')),
    ('folder', _('Folder')),
    ('zip', _('ZIP'))
)

SYSTEM_CHOISES = (
    ('win_i386', _('Windows i386')),
    ('win_64', _('Windows 64 Bit'))
)


class GitInstance(models.Model):
    name = models.CharField(help_text=_('Unique name of the git repo. This name cannot be changed!'),unique=True, max_length=50)
    url = models.CharField(help_text=_('URL to the git repo.'), max_length=255)
    branch = models.CharField(_('Commit Or Branch'), help_text=_('Enter the branch name or commit ID.'), max_length=255, default='main')
    is_active = models.BooleanField(default=False)
    last_reload = models.DateTimeField(null=True, blank=True)

    def get_path(self):
        file_paths = os.path.join('./projects/git_repos/', self.name)
        new_repo = glob.glob(os.path.join(file_paths, '*'))
        if len(new_repo) > 0:
            new_repo = os.path.abspath(new_repo[0])
        else:
            new_repo = None

        return (file_paths, new_repo)


    def set_active(self):
        GitInstance.objects.filter(is_active=True).update(is_active=False)
        self.is_active = True
        self.save()

    def git_reload(self):
        file_paths, x = self.get_path()
        shutil.rmtree(os.path.join(file_paths), ignore_errors=True)
        os.makedirs(file_paths, exist_ok=True)
        abs_path = os.path.abspath(file_paths)
        p = subprocess.Popen(['git', 'clone', self.url], cwd=abs_path)
        p_status = p.wait()
        if p_status != 0:
            raise Exception(_("Url cannot be cloned: %s") % self.url)
        x, abs_path = self.get_path()
        p = subprocess.Popen(['git', 'checkout', self.branch], cwd=abs_path)
        p_status = p.wait()
        if p_status != 0:
            raise Exception(_("Branch or ID cannot be checked out: %s") % self.branch)
        files = glob.glob(os.path.join(file_paths, '*', '.git'))
        for f in files:
            shutil.rmtree(f)
        files = glob.glob(os.path.join(file_paths, '*', 'bin'))
        for f in files:
            shutil.rmtree(f)

        self.last_reload = timezone.now()
        self.save()


class GitInstanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(GitInstanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True


    def clean_name(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.name
        else:
            return self.cleaned_data['name']


    class Meta:
        model = GitInstance
        fields = ['name', 'url', 'branch']

    def generate_filte(self):
        pass


class GitInstanceSearchForm(AbstractSearchForm):
    CHOICES = (('name', _('Name')), ('efw_type', _('Type')), ('src', _('Source')), ('dst', _('Destination')), ('architecture', _('Architecture')))
    PLACEHOLDER = _('Name, Type, Source, Destination')
    DEFAULT_CHOICES = CHOICES[0][0]
    SEARCH_FIELDS = ('name', 'efw_type', 'src', 'dst', 'architecture')

    def generate_filte(self):
        pass

class ElnConnection(models.Model):
    url = models.URLField(_('Eln connection!'))
    active = models.BooleanField()
    token = models.CharField(default=None, null=True, blank=True, max_length=255)
    device= models.IntegerField(default=0)

    @classmethod
    def get_active(cls):
        instance = ElnConnection.objects.get(active=True)
        return instance

    @classmethod
    def activate_connection(cls, user, password):
        (instance, c) = ElnConnection.objects.get_or_create(active=True)
        if c:
            instance.url = settings.ELN_URL

        error_in_process = True

        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'username': user, 'password': password}

        session = requests.Session()
        res = session.post('%s/api/v1/public/token' % instance.url, headers=headers,
                           data=payload)

        if res.status_code == 201:
            instance.token = json.loads(res.content.decode())['token']

            payload = {"abbr": settings.ELN_DEVICE_NAME}
            headers = {"Authorization": "Bearer %s" % instance.token}

            res = session.get('%s/api/v1/admin/group_device' % instance.url, headers=headers,
                               data=payload)
            if res.status_code == 404:
                payload = {'first_name': "file_transfer_proxi",
                           'last_name': "created_by_%s" % user,
                           'rootType': "Device",
                           "name_abbreviation": settings.ELN_DEVICE_NAME}

                res = session.post('%s/api/v1/admin/group_device/create' % instance.url, headers=headers,
                                   data=payload)

            if res.status_code == 201 or res.status_code == 200:
                instance.device = json.loads(res.content.decode()).get('id')
                instance.save()
                error_in_process = False

        if error_in_process:
            instance.delete()
        session.close()

        return not error_in_process


class ElnConnectionForm(ModelForm):
    user = CharField(help_text=_('Enter admin login info.'))
    password = CharField(widget=PasswordInput())
    class Meta:
        fields = ('url', 'user', 'password',)
        model = ElnConnection