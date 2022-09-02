import os
import shutil
import subprocess
from datetime import datetime

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
    ('win_64', _('Windows 64 Bit'))
)


class Instance(models.Model):
    name = models.CharField(help_text=_('Unique name of the EFW instance. This name cannot be changed!'), max_length=50)
    user = models.CharField(help_text=_("WebDAV User"),max_length=50, default="")
    password = models.CharField(help_text=_("WebDAV Password"), max_length=100)
    src = models.CharField(help_text=_("Source directory to be watched."), max_length=255)
    dst = models.CharField(help_text=_("""WebDAV destination URL. If the destination is on the lsdf, the URL should be as follows:
        https://os-webdav.lsdf.kit.edu/[OE]/[inst]/projects/[PROJECTNAME]/<br>
                    [OE]-Organisationseinheit, z.B. kit.<br>
                    [inst]-Institut-Name, z.B. ioc, scc, ikp, imk-asf etc.<br>
                    [USERNAME]-User-Name z.B. xy1234, bs_abcd etc.<br>
                    [PROJRCTNAME]-Projekt-Name"""),max_length=255)
    efw_type = models.CharField(_('Type'), help_text=_("Type must be 'file', 'folder' or 'zip'. The 'file' option means that each file is handled individually, the 'folder' option means that entire folders are transmitted only when all files in them are ready. The option 'zip' sends a folder zipped, only when all files in a folder are ready."), max_length=255, choices=TYPE_CHOISES)
    duration = models.IntegerField(help_text=_("Duration in seconds, i.e., how long a file must not be changed before sent. (default 300 sec.)"), default=300)
    # cert = models.CharField(help_text=_("Path to server TLS certificate. Only needed if the server has a self signed certificate."), max_length=255, blank=True, null=True)
    architecture = models.CharField(_('System architecture'), help_text=_("Your computer architecture : either 64 bit or 32 bit (i386) "), max_length=255, choices=SYSTEM_CHOISES, default=SYSTEM_CHOISES[0][0])
    last_update = models.DateTimeField(default=datetime.now)
    last_build = models.DateTimeField(null=True, blank=True)

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
                     "crt": "None",
                     "type": self.efw_type})

    def build(self):
        git = GitInstance.objects.get(is_active=True)
        if git.last_reload is None:
            git.git_reload()
        _, repo_path = git.get_path()

        tp =  self.get_path()
        tp_bin = os.path.abspath(os.path.join(tp, 'bin'))
        tp_src = os.path.abspath(os.path.join(tp, 'src'))

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
                        pass
            os.makedirs(tp_bin, exist_ok=True)
            my_env = os.environ.copy()
            my_env["GOOS"] = settings.GOOS
            my_env["GOROOT"] = settings.GOROOT
            my_env["GOPATH"] = settings.GOPATH
            if self.architecture == 'win_i386':
                my_env['GOARCH'] = '386'

            p = subprocess.Popen([os.path.join(settings.GOROOT, "bin/go"), "build", "-o", os.path.join(tp_bin, 'efw.exe') ], env=my_env, cwd=tp_src)
            p_status = p.wait()
            if p_status != 0:
                raise Exception(_("Compiling failed"))

            shutil.rmtree(tp_src, ignore_errors=True)
            self.last_build = datetime.now()
            self.save()
        return os.path.join(tp_bin, 'efw.exe')



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
        self.instance.last_update = datetime.now()
        super(InstanceForm, self).save(commit)

    class Meta:
        model = Instance
        fields = ['name', 'user', 'password', 'src', 'dst', 'efw_type', 'duration', 'architecture']


class InstanceSearchForm(AbstractSearchForm):
    CHOICES = (('name', _('Name')), ('user', _('User')), ('efw_type', _('Type')), ('src', _('Source')), ('dst', _('Destination')), ('architecture', _('Architecture')))
    PLACEHOLDER = _('Name, Type, Source, Destination')
    DEFAULT_CHOICES = CHOICES[0][0]
    SEARCH_FIELDS = ('name', 'user', 'efw_type', 'src', 'dst', 'architecture')

    def generate_filte(self):
        pass