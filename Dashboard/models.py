import os
import shutil
import subprocess
import urllib.parse
import uuid

from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from sdc_tools.django_extension.forms import AbstractSearchForm
from distutils.dir_util import copy_tree
from Adminview.models import GitInstance

from django.template import Template, Context

UserModel = get_user_model()

from django.conf import settings

TYPE_CHOISES = (
    ('file', _('File')),
    ('folder', _('Folder')),
    ('zip', _('ZIP'))
)

SYSTEM_CHOISES = (
    ('win_i386', _('Windows i386')),
    ('win_64', _('Windows 64 Bit')),
    ('ubuntu_64', _('Ubuntu 64 Bit'))
)

BACKUP_CHOISES = (
    ('user_backup', _('(A) only if it can be assigned to an ELN user,')),
    ('all_backup', _('(B) in any case')),
    ('no_backup', _('(C) no backup'))
)

TRANSFER_CHOISES = (
    ('webdav', _('WebDAV')),
    ('sftp', _('SFTP')),
)


class Instance(models.Model):
    name = models.CharField(help_text=_('Unique name of the EFW instance. This name cannot be changed!'), max_length=50,
                            unique=True)
    user = models.CharField(help_text=_("WebDAV or STFP User"), max_length=50, default="")
    password = models.CharField(help_text=_("WebDAV or STFP Password"), max_length=100)
    transfer = models.CharField(_('Transfer protocol'),
                               help_text=_("You can either use the WebDAV protocol or the SFTP protocol"),
                               max_length=255, choices=TRANSFER_CHOISES, default=TRANSFER_CHOISES[0][0])
    src = models.CharField(help_text=_(
        "Source directory to monitor. Note: If you use only single \\ in the path, the build will fail. Therefore, make sure that you always use \\\\."),
                           max_length=255)
    dst = models.CharField(help_text=_("""WebDAV or SFTP destination URL. If the destination is on the lsdf, the URL should be as follows:<br>
        <span style="margin-left: 20px; font-weight: 800;">SFTP</span>: os-login.lsdf.kit.edu/[OE]/[inst]/projects/[PROJECT_PATH]/<br>
        <span style="margin-left: 20px; font-weight: 800;">WebDAV</span>: https://os-webdav.lsdf.kit.edu/[OE]/[inst]/projects/[PROJECT_PATH]/<br>

                    <span style="margin-left: 30px;">[OE]-Organisationseinheit, z.B. kit.</span><br>
                    <span style="margin-left: 30px;">[inst]-Institut-Name, z.B. ioc, scc, ikp, imk-asf etc.</span><br>
                    <span style="margin-left: 30px;">[USERNAME]-User-Name z.B. xy1234, bs_abcd etc.</span><br>
                    <span style="margin-left: 30px;">[PROJECT_PATH]-Path (directory) within the LSDF</span>"""), max_length=255)
    efw_type = models.CharField(_('Type'), help_text=_(
        "Type must be 'file', 'folder' or 'zip'. The 'file' option means that each file is handled individually, the 'folder' option means that entire folders are transmitted only when all files in them are ready. The option 'zip' sends a folder zipped, only when all files in a folder are ready."),
                                max_length=255, choices=TYPE_CHOISES)
    duration = models.IntegerField(
        help_text=_("Duration in seconds, i.e., how long a file must not be changed before sent. (default 300 sec.)"),
        default=300)
    # cert = models.CharField(help_text=_("Path to server TLS certificate. Only needed if the server has a self signed certificate."), max_length=255, blank=True, null=True)
    architecture = models.CharField(_('System architecture'),
                                    help_text=_("Your computer architecture : either 64 bit or 32 bit (i386) "),
                                    max_length=255, choices=SYSTEM_CHOISES, default=SYSTEM_CHOISES[0][0])

    backup = models.CharField(_('Backup type'),
                                    help_text=_("There are three different backup settings. Either, (A) a backup of the data is created only if it can be assigned to an ELN user, (B) a backup of the data is created in any case or (C) a backup is not created in any case."),
                                    max_length=255, choices=BACKUP_CHOISES, default=BACKUP_CHOISES[0][0])

    last_update = models.DateTimeField(default=timezone.now)
    last_build = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        build_path = self.get_path()
        shutil.rmtree(build_path)
        super(Instance, self).delete(using, keep_parents)


    def get_path(self):
        file_paths = os.path.join('./projects/builds/', self.name)
        os.makedirs(file_paths, exist_ok=True)
        return file_paths

    def _get_build_config(self):
        return Context({"src": self.src,
                        "dst": self.dst,
                        "user": self.user,
                        "password": self.password,
                        "duration": self.duration,
                        "tType": self.transfer,
                        "name": self.name,
                        "crt": "None",
                        "type": self.efw_type})

    def only_exe(self):
        return self.architecture != 'win_i386' or self.transfer != 'sftp'

    def build(self):
        git = GitInstance.objects.get(is_active=True)
        if git.last_reload is None:
            git.git_reload()
        __, repo_path = git.get_path()

        tp = self.get_path()
        tp_bin = os.path.abspath(os.path.join(tp, 'bin'))
        tp_src = os.path.abspath(os.path.join(tp, 'src'))

        if self.architecture != 'ubuntu_64':
            filename = 'efw.exe'
        else:
            filename = 'efw'

        if self.last_build is None or self.last_build <= git.last_reload or self.last_update > self.last_build:
            shutil.rmtree(tp, ignore_errors=True)
            os.makedirs(tp_src, exist_ok=True)
            copy_tree(repo_path, tp_src)

            for root, dirs, files in os.walk(tp_src, topdown=False):
                for name in files:
                    f = open(os.path.join(root, name), "r")
                    try:
                        text = f.read()
                        t = Template(text)
                        f.close()
                        text = t.render(self._get_build_config())
                        f = open(os.path.join(root, name), "w")
                        f.write(text)
                        f.close()
                    except:
                        raise Exception(_("Compiling failed"))
            os.makedirs(tp_bin, exist_ok=True)
            my_env = os.environ.copy()
            my_env["GOROOT"] = settings.GOROOT
            my_env["GOPATH"] = settings.GOPATH
            if self.architecture != 'ubuntu_64':
                my_env["GOOS"] = settings.GOOS

            if self.architecture == 'win_i386':
                my_env['GOARCH'] = '386'
                go_tool = "go1.10"
            else:
                go_tool = os.path.join(settings.GOROOT, "bin/go")
                p = subprocess.Popen([go_tool, "mod", "download"], env=my_env, cwd=tp_src)
                p_status = p.wait()
                print(p, p_status)
                if p_status != 0:
                    raise Exception(_("Download mod failed"))

            p = subprocess.Popen(
                [go_tool, "build", "-o", os.path.join(tp_bin, filename)], env=my_env,
                cwd=tp_src)
            p_status = p.wait()
            print(p, p_status)
            if p_status != 0:
                raise Exception(_("Compiling failed"))

            shutil.rmtree(tp_src, ignore_errors=True)
            self.last_build = timezone.now()
            self.save()
        return os.path.join(tp_bin, filename)


class InstanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(InstanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True

    def clean_name(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.name
        else:
            return self.cleaned_data['name']

    def save(self, commit=True):
        self.instance.last_update = timezone.now()
        super(InstanceForm, self).save(commit)

    class Meta:
        model = Instance
        fields = ['name', 'transfer', 'user', 'password', 'src', 'dst', 'efw_type', 'duration', 'architecture', 'backup']



class LocalInstanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(LocalInstanceForm, self).__init__(*args, **kwargs)
        self._hosturl = settings.WEBDAV_HOST
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True

    def clean_name(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.name
        else:
            return self.cleaned_data['name']

    def save(self, commit=True):
        self.instance.user = str(uuid.uuid4())
        self.instance.password = str(uuid.uuid4())
        name = urllib.parse.quote(self.instance.name)
        self.instance.dst = self._hosturl + reverse('webdav', kwargs={'name': name, 'path': ''})
        self.instance.last_update = timezone.now()
        super(LocalInstanceForm, self).save(commit)

    class Meta:
        model = Instance
        fields = ['name', 'src', 'efw_type', 'duration', 'architecture', 'backup']

class InstanceSearchForm(AbstractSearchForm):
    CHOICES = (
        ('name', _('Name')), ('user', _('User')), ('efw_type', _('Type')), ('src', _('Source')),
        ('dst', _('Destination')),
        ('architecture', _('Architecture')))
    PLACEHOLDER = _('Name, Type, Source, Destination')
    DEFAULT_CHOICES = CHOICES[0][0]
    SEARCH_FIELDS = ('name', 'user', 'efw_type', 'src', 'dst', 'architecture')

    def generate_filte(self):
        pass

