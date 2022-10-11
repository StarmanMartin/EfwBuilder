import base64
import re

from Dashboard.models import Instance
from WebDAV.resources import WriteFSDavResource, SendFileFSDavResource
from WebDAV.utils import rfc1123_date


from sys import version_info as python_version
from lxml import etree

from django.utils.timezone import now
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from urllib.parse import unquote
from WebDAV.responses import ResponseException, HttpResponseCreated, \
    HttpResponseNoContent, \
    HttpResponseConflict, HttpResponseMediatypeNotSupported, HttpResponse, DavAcl

from django import VERSION as django_version, get_version

PATTERN_IF_DELIMITER = re.compile(r'(<([^>]+)>)|(\(([^\)]+)\))')

WEBDAV_NS = "DAV:"
WEBDAV_NSMAP = {'D': WEBDAV_NS}

class DavDownloadView(View):
    resource_class = SendFileFSDavResource

    def get(self, request, path):
        return SendFileFSDavResource(path).read()


class DavView(View):
    resource_class = WriteFSDavResource
    acl_class = DavAcl
    template_name = 'djangodav/index.html'
    http_method_names = ['options', 'put', 'mkcol']
    server_header = 'Django/%s Python/%s' % (
        get_version(django_version),
        get_version(python_version)
    )
    xml_pretty_print = False
    xml_encoding = 'utf-8'

    def header_auth_view(self, request, name):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        try:
            instance = Instance.objects.get(name=name)
            username = decoded_credentials[0]
            password = decoded_credentials[1]
            if(instance.user == username and password == instance.password):
                self.instance = instance
                self.auth = True
                return True
        except:
            pass
        self.instance = None
        self.auth = False
        return False

    def no_access(self):
        return HttpResponseForbidden()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, name, path, *args, **kwargs):
        name = unquote(name)
        self.header_auth_view(request, name=name)
        if path:
            self.path = path
            self.base_url = request.META['PATH_INFO'][:-len(self.path)]
        else:
            self.path = "/"
            self.base_url = request.META['PATH_INFO']

        meta = request.META.get
        self.xbody = kwargs['xbody'] = None
        if (request.method.lower() != 'put'
                and "/xml" in meta('CONTENT_TYPE', '')
                and meta('CONTENT_LENGTH', 0) != ''
                and int(meta('CONTENT_LENGTH', 0)) > 0):
            self.xbody = kwargs['xbody'] = etree.XPathDocumentEvaluator(
                etree.parse(request, etree.XMLParser(ns_clean=True)),
                namespaces=WEBDAV_NSMAP
            )

        if request.method.upper() in self._allowed_methods():
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        try:
            resp = handler(request, self.path, *args, **kwargs)
        except ResponseException as e:
            resp = e.response
        if not 'Allow' in resp:
            methods = self._allowed_methods()
            if methods:
                resp['Allow'] = ", ".join(methods)
        if not 'Date' in resp:
            resp['Date'] = rfc1123_date(now())
        if self.server_header:
            resp['Server'] = self.server_header
        return resp

    def options(self, request, *args, **kwargs):
        if not self.has_access(self.resource, 'read'):
            return self.no_access()
        response = self.build_xml_response()
        response['DAV'] = '1,2'
        response['Content-Length'] = '0'
        if self.path in ('/', '*'):
            return response
        response['Allow'] = ", ".join(self._allowed_methods())
        if self.resource.exists and self.resource.is_object:
            response['Allow-Ranges'] = 'bytes'
        return response

    def _allowed_methods(self):
        allowed = [
            'HEAD', 'OPTIONS', 'PUT', 'MKCOL'
        ]

        return allowed

    def get_access(self, resource):
        """Return permission as DavAcl object. A DavACL should have the following attributes:
        read, write, delete, create, relocate, list. By default we implement a read-only
        system."""
        return self.acl_class(write=self.auth, read=self.auth, full=False)

    def has_access(self, resource, method):
        return getattr(self.get_access(resource), method)

    def get_resource_kwargs(self, **kwargs):
        return kwargs

    @cached_property
    def resource(self):
        r = self.get_resource(path=self.path, root_extension=self.instance.name)
        r.make_root()
        return r

    def get_resource(self, **kwargs):
        return self.resource_class(**self.get_resource_kwargs(**kwargs))

    def get_depth(self, default='1'):
        depth = str(self.request.META.get('HTTP_DEPTH', default)).lower()
        if not depth in ('0', '1', 'infinity'):
            raise ResponseException(HttpResponseBadRequest('Invalid depth header value %s' % depth))
        if depth == 'infinity':
            depth = -1
        else:
            depth = int(depth)
        return depth

    def put(self, request, path, *args, **kwargs):
        parent = self.resource.get_parent()
        if not parent.exists:
            return HttpResponseConflict("Resource doesn't exists")
        if self.resource.is_collection:
            return HttpResponseNotAllowed(list(set(self._allowed_methods()) - {'MKCOL', 'PUT'}))
        if not self.resource.exists and not self.has_access(parent, 'write'):
            return self.no_access()
        if self.resource.exists and not self.has_access(self.resource, 'write'):
            return self.no_access()
        created = not self.resource.exists
        self.resource.write(request)
        if created:
            self.__dict__['resource'] = self.get_resource(path=self.resource.get_path())
            return HttpResponseCreated()
        else:
            return HttpResponseNoContent()

    def mkcol(self, request, path, *args, **kwargs):
        if self.resource.exists:
            return HttpResponseNotAllowed(list(set(self._allowed_methods()) - {'MKCOL', 'PUT'}))
        if not self.resource.get_parent().exists:
            return HttpResponseConflict()
        length = request.META.get('CONTENT_LENGTH', 0)
        if length and int(length) != 0:
            return HttpResponseMediatypeNotSupported()
        if not self.has_access(self.resource, 'write'):
            return self.no_access()
        self.resource.create_collection()
        self.__dict__['resource'] = self.get_resource(path=self.resource.get_path())
        return HttpResponseCreated()

    def build_xml_response(self, tree=None, response_class=HttpResponse, **kwargs):
        if tree is not None:
            content = etree.tostring(
                tree,
                xml_declaration=True,
                pretty_print=self.xml_pretty_print,
                encoding=self.xml_encoding
            )
        else:
            content = b''
        return response_class(
            content,
            content_type='text/xml; charset="%s"' % self.xml_encoding,
            **kwargs
        )