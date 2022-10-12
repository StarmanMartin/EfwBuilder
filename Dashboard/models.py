import os
import shutil
import subprocess
import urllib.parse
import uuid

from django.core.exceptions import ValidationError
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
    ('win_64', _('Windows 64 Bit'))
)


class Instance(models.Model):
    name = models.CharField(help_text=_('Unique name of the EFW instance. This name cannot be changed!'), max_length=50,
                            unique=True)
    user = models.CharField(help_text=_("WebDAV User"), max_length=50, default="")
    password = models.CharField(help_text=_("WebDAV Password"), max_length=100)
    src = models.CharField(help_text=_(
        "Source directory to monitor. Note: If you use only single \\ in the path, the build will fail. Therefore, make sure that you always use \\\\."),
                           max_length=255)
    dst = models.CharField(help_text=_("""WebDAV destination URL. If the destination is on the lsdf, the URL should be as follows:
        https://os-webdav.lsdf.kit.edu/[OE]/[inst]/projects/[PROJECTNAME]/<br>
                    [OE]-Organisationseinheit, z.B. kit.<br>
                    [inst]-Institut-Name, z.B. ioc, scc, ikp, imk-asf etc.<br>
                    [USERNAME]-User-Name z.B. xy1234, bs_abcd etc.<br>
                    [PROJRCTNAME]-Projekt-Name"""), max_length=255)
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
    last_update = models.DateTimeField(default=timezone.now)
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
        __, repo_path = git.get_path()

        tp = self.get_path()
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
                        raise Exception(_("Compiling failed"))
            os.makedirs(tp_bin, exist_ok=True)
            my_env = os.environ.copy()
            my_env["GOOS"] = settings.GOOS
            my_env["GOROOT"] = settings.GOROOT
            my_env["GOPATH"] = settings.GOPATH
            if self.architecture == 'win_i386':
                my_env['GOARCH'] = '386'

            p = subprocess.Popen(
                [os.path.join(settings.GOROOT, "bin/go"), "build", "-o", os.path.join(tp_bin, 'efw.exe')], env=my_env,
                cwd=tp_src)
            p_status = p.wait()
            if p_status != 0:
                raise Exception(_("Compiling failed"))

            shutil.rmtree(tp_src, ignore_errors=True)
            self.last_build = timezone.now()
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
        self.instance.last_update = timezone.now()
        super(InstanceForm, self).save(commit)

    class Meta:
        model = Instance
        fields = ['name', 'user', 'password', 'src', 'dst', 'efw_type', 'duration', 'architecture']


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
        fields = ['name', 'src', 'efw_type', 'duration', 'architecture']


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


class UmlSearchForm(AbstractSearchForm):
    CHOICES = (('name', _('Name')), ('elements__label', _('Element label')))
    PLACEHOLDER = _('Name, Element label')
    DEFAULT_CHOICES = CHOICES[0][0]
    SEARCH_FIELDS = ('name', 'elements__label')

    def generate_filte(self):
        pass


class UmlDiagram(models.Model):
    name = models.CharField(max_length=255)


def clean_vale(data, name, type='str'):
    val = data.get(name, None)
    if val is None:
        raise ValidationError(_('%s must be set!') % name)
    if type == 'str':
        if len(val) == 0:
            raise ValidationError(_('%s must be set!') % name)
        return str(val)
    if type == 'int':
        return int(val)
    return val


class UmlElement(models.Model):
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    token = models.CharField(max_length=255, default=uuid.uuid4)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    diagram = models.ForeignKey(UmlDiagram, on_delete=models.CASCADE, related_name='elements')
    extends = models.ManyToManyField("self", symmetrical=False, related_name='extended_by')

    def gat_all_related(self):
        return ','.join(self.extends.values_list('token', flat=True))

    @classmethod
    def create_from_json(cls, parent, data):
        return cls.objects.create(
            key=clean_vale(data, 'key'),
            label=clean_vale(data, 'label'),
            token=clean_vale(data, 'token'),
            y=clean_vale(data, 'y', 'int'),
            x=clean_vale(data, 'x', 'int'),
            diagram=parent
        )


class UmlSegment(models.Model):
    order = models.IntegerField()
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    element = models.ForeignKey(UmlElement, on_delete=models.CASCADE, related_name='segments')

    @classmethod
    def create_from_json(cls, parent, data, order):
        return cls.objects.create(
            order=order,
            key=clean_vale(data, 'key'),
            label=clean_vale(data, 'label'),
            element=parent
        )


class UmlLayer(models.Model):
    order = models.IntegerField()
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    segment = models.ForeignKey(UmlSegment, on_delete=models.CASCADE, related_name='layers')

    def get_layers(self):
        return self.fields.filter(is_table_field=False)

    @classmethod
    def create_from_json(cls, parent, data, order):
        return cls.objects.create(
            order=order,
            key=clean_vale(data, 'key'),
            label=clean_vale(data, 'label'),
            segment=parent
        )


class UmlField(models.Model):
    order = models.IntegerField()
    is_table_field = models.BooleanField()
    field = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='text')
    label = models.CharField(max_length=255)
    layer = models.ForeignKey(UmlLayer, on_delete=models.CASCADE, related_name='fields')
    sub_field_from = models.ForeignKey("self", blank=True, null=True, related_name="sub_fields",
                                       on_delete=models.CASCADE)

    @classmethod
    def create_from_json(cls, parent, data, order):
        field = cls.objects.create(
            order=order,
            is_table_field=False,
            field=clean_vale(data, 'field'),
            type=str(clean_vale(data, 'type')).lower(),
            label=clean_vale(data, 'label'),
            layer=parent
        )

        if field.type == 'table':
            order = 0
            for sub in data.get('sub_fields', []):
                order += 10
                cls.objects.create(
                    order=order,
                    is_table_field=True,
                    field=clean_vale(sub, 'field'),
                    type=str(clean_vale(sub, 'type')).lower(),
                    label=clean_vale(sub, 'label'),
                    layer=parent,
                    sub_field_from=field
                )
        return field


class UmlDiagramForm(ModelForm):
    class Meta:
        model = UmlDiagram
        fields = ['name']
