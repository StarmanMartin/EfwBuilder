import json

import requests
from django.contrib.auth import get_user_model

from WebDAV.resources import BaseFSDavResource
from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _f
from Adminview.models import GitInstanceSearchForm, GitInstance, GitInstanceForm, ElnConnectionForm, ElnConnection
from sdc_tools.django_extension.response import send_error, send_success, send_redirect
from sdc_tools.django_extension import search

from Adminview.sub_views import admin_user_test
from Adminview.sub_views.user_view import AdminUser, AdminEditUser, AdminPasswordChange, AdminCreateUser

UserModel = get_user_model()


def get_user(request, pk):
    pk = int(pk)
    if pk == request.user.pk:
        return request.user
    elif pk == -1:
        return None
    try:
        return UserModel.objects.get(pk=pk, is_superuser=False)
    except:
        return None


class AdminMainView(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    raise_exception = True
    template_name = 'Adminview/sdc/admin_main_view.html'

    def test_func(self):
        request = self.request
        return True

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)


class GitList(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    raise_exception = True
    template_name = 'Adminview/sdc/git_list.html'
    element_template_name = 'Adminview/elements/git_row.html'
    search_form = GitInstanceSearchForm
    range_size = 10

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, *args, **kwargs):

        request_type = request.POST.get("_action", None)
        try:
            user = GitInstance.objects.get(pk=request.POST.get("pk", -1))
        except:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)

        if request_type == "activate":
            user.set_active()  #
            msg = _f("Git is activated!") if user.is_active else _f("Git is Deactivated!")
        elif request_type == "reload":
            try:
                user.git_reload()  #
            except Exception as e:
                return send_error(header=_f('Action failed!'),
                                  msg=str(e),
                                  request=request,
                                  status=400)
            msg = _f("Git repo reloaded!")
        else:
            return send_error(header=_f('Action failed!'),
                              msg=_f('Function not available!'),
                              request=request,
                              status=400)

        return send_success(self.element_template_name, {'elem': user},
                            request=request,
                            header=_f("Edit success!"),
                            msg=msg,
                            pk=user.pk,
                            _action=request_type)

    def search(self, request, *args, **kwargs):
        return self.get_content(request, *args, **kwargs)

    def get_content(self, request, *args, **kwargs):
        context = self.get_context(request)
        return render(request, self.template_name, context=context)

    def get_context(self, request=None):
        if request is not None:
            form = self.search_form(request.POST)
        else:
            form = self.search_form([])
        form.is_valid()
        return search.handle_search_form(GitInstance.objects, form, filter_dict=form.generate_filte(),
                                         range=self.range_size)


class GitNew(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    template_name = 'Adminview/sdc/git_new.html'
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, *args, **kwargs):
        form = GitInstanceForm(data=request.POST)

        if form.is_valid():
            form.save()
            return send_redirect(back=True, header=_f('Successfully saved!!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, *args, **kwargs):
        context = {'form': GitInstanceForm()}
        return render(request, self.template_name, context)


class GitEdit(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    template_name = 'Adminview/sdc/git_edit.html'
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, git_pk, *args, **kwargs):
        try:
            user = GitInstance.objects.get(pk=git_pk)
        except:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)

        form = GitInstanceForm(instance=user, data=request.POST)
        context = {'form': form}
        if form.is_valid():
            form.save()

            return send_success(request=request, context=context,
                                header=_f('Successfully saved'))

        return send_error(self.template_name, status=403, request=request, context=context,
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, git_pk, *args, **kwargs):
        try:
            user = GitInstance.objects.get(pk=git_pk)
        except:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=404)
        form = GitInstanceForm(instance=user)
        context = {'form': form}
        return render(request, self.template_name, context)


class ElnFile(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request):
        instance = ElnConnection.get_active()
        session = requests.Session()
        bDav = BaseFSDavResource("Local24/src/MST-1-test.txt")
        headers = {"Authorization": "Bearer %s" % instance.token}
        f = open(bDav.get_abs_path(), "rb")
        # res = session.post('%s/api/v1/attachments/upload_dataset_attachments' % instance.url, headers=headers, files=payload)
        res = session.get('%s/api/v1/fileservicer/all_files' % instance.url, headers=headers)
        json.loads(res.content)
        session.close()
        f.close()

        return send_success(request=request, header=_f('Successfully sent'))


class ElnManager(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    template_name = 'Adminview/sdc/eln_manager.html'
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request):
        instance = ElnConnection.get_active()
        form = ElnConnectionForm(request.POST, instance=instance)
        context = {'form': form, 'instance': instance}
        if form.is_valid():
            ElnConnection.activate_connection(form.cleaned_data['user'], form.cleaned_data['password'])

            return send_success(request=request, context=context,
                                    header=_f('Successfully Connected'))

        return send_error(self.template_name, status=403, request=request, context=context,
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, *args, **kwargs):
        instance = ElnConnection.get_active()
        context = {
            'form': ElnConnectionForm(instance=instance),
            'instance': instance,
        }
        return render(request, self.template_name, context=context)
