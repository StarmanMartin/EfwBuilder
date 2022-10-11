# Portions (c) 2014, Alexander Klimenko <alex@erix.ru>
# All rights reserved.
#
# Copyright (c) 2011, SmartFile <btimby@smartfile.com>
# All rights reserved.
#
# This file is part of DjangoDav.
#
# DjangoDav is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DjangoDav is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DjangoDav.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import os
import mimetypes
from sys import getfilesystemencoding
import os
import datetime
import shutil

from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.http import http_date


from WebDAV.base.resources import BaseDavResource
from WebDAV.responses import ResponseException
from WebDAV.utils import url_join, zip_folder
from urllib.parse import quote

fs_encoding = getfilesystemencoding()

class BaseFSDavResource(BaseDavResource):
    """Implements an interface to the file system. This can be subclassed to provide
    a virtual file system (like say in MySQL). This default implementation simply uses
    python's os library to do most of the work."""

    root = os.path.join(os.getcwd(), 'data_webdav')

    def make_root(self):
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def get_abs_path(self):
        """Return the absolute path of the resource. Used internally to interface with
        an actual file system. If you override all other methods, this one will not
        be used."""
        return os.path.join(self.root, *self.path)

    @property
    def depth(self):
        return len(self.path)

    @property
    def getcontentlength(self):
        """Return the size of the resource in bytes."""
        return os.path.getsize(self.get_abs_path())

    def get_created(self):
        """Return the create time as datetime object."""
        return datetime.datetime.fromtimestamp(os.stat(self.get_abs_path()).st_ctime)

    def get_modified(self):
        """Return the modified time as datetime object."""
        return datetime.datetime.fromtimestamp(os.stat(self.get_abs_path()).st_mtime)

    @property
    def is_collection(self):
        """Return True if this resource is a directory (collection in WebDAV parlance)."""
        return os.path.isdir(self.get_abs_path())

    @property
    def is_object(self):
        """Return True if this resource is a file (resource in WebDAV parlance)."""
        return os.path.isfile(self.get_abs_path())

    @property
    def exists(self):
        """Return True if this resource exists."""
        return os.path.exists(self.get_abs_path())

    def get_icon(self):
        """Returns icon TODO"""
        return 'bi-file-earmark-text'

    def get_filename(self):
        """Returns icon TODO"""
        return self.path[-1]

    def get_children(self):
        """Return an iterator of all direct children of this resource."""
        if os.path.isdir(self.get_abs_path()):
            for child in os.listdir(self.get_abs_path()):

                is_unicode = isinstance(child, str)
                if not is_unicode:
                    child = bytes(child).decode(fs_encoding)
                yield self.clone(path = url_join(*(self.path + [child])))

    def write(self, content):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def delete(self):
        """Delete the resource, recursive is implied."""
        if self.is_collection:
            for child in self.get_children():
                child.delete()
            os.rmdir(self.get_abs_path())
        elif self.is_object:
            os.remove(self.get_abs_path())

    def create_collection(self):
        """Create a directory in the location of this resource."""
        os.mkdir(self.get_abs_path())

    def copy_object(self, destination, depth=0):
        shutil.copy(self.get_abs_path(), destination.get_abs_path())

    def move_object(self, destination):
        os.rename(self.get_abs_path(), destination.get_abs_path())


class ReadFSDavResource(BaseFSDavResource):
    def read(self):
        with open(self.get_abs_path(), 'rb') as f:
            return f.read()


class WriteFSDavResource(BaseFSDavResource):
    def write(self, request):
        with open(self.get_abs_path(), 'wb') as dst:
            shutil.copyfileobj(request, dst)


class DummyFSDAVResource(ReadFSDavResource, WriteFSDavResource, BaseFSDavResource):
    pass


class SendFileFSDavResource(BaseFSDavResource):
    quote = False

    def read(self):
        if self.is_collection:
            (text, filename) = zip_folder(self)
        else:
            with open(self.get_abs_path(), 'rb') as f:
                text = f.read()
                filename = self.get_filename()
        response = HttpResponse(text)
        full_path = self.get_abs_path().encode('utf-8')

        response['X-SendFile'] = quote(full_path)
        response['Content-Type'] = mimetypes.guess_type(self.displayname)
        response['Content-Length'] = len(text)
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
        response['Last-Modified'] = http_date(self.get_modified().timestamp())
        #response['ETag'] = self.getetag
        return response

