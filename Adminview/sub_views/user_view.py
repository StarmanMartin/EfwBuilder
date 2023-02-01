from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render
from sdc_tools.django_extension import search
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from Adminview.search_forms import UserSearchForm
from sdc_tools.django_extension.response import send_error, send_success
from django.utils.translation import gettext as _f

from Adminview.sub_views import admin_user_test
from sdc_user.form import CustomEditForm, CustomUserCreationForm

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



class AdminUser(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    raise_exception = True
    template_name = 'Adminview/sdc/admin_user.html'
    element_template_name = 'Adminview/elements/user_row.html'
    search_form = UserSearchForm
    range_size = 10

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, *args, **kwargs):

        request_type = request.POST.get("_action", None)
        user = get_user(request, request.POST.get("pk", -1))
        if user is None:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)
        if user.is_superuser:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User is Superuser!'),
                              request=request,
                              status=400)
        elif request_type == "activate":
            user.is_active = (not user.is_active)
            user.save()  #
            msg = _f("User is activated!") if user.is_active else _f("User is Deactivated!")
        elif request_type == "set_staff":
            user.is_staff = (not user.is_staff)
            user.save()  #
            msg = _f("User is admin!") if user.is_staff else _f("User is NO admin anymore!")
        else:
            return send_error(header=_f('Action failed!'),
                              msg=_f('Function not available!'),
                              request=request,
                              status=400)

        return send_success(self.element_template_name, {'registered_user': user},
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
        return search.handle_search_form(UserModel.objects, form, filter_dict=form.generate_filte(),
                                         range=self.range_size)


class AdminEditUser(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    raise_exception = True
    template_name = 'Adminview/sdc/admin_edit_user.html'

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, user_pk, *args, **kwargs):
        user = get_user(request, user_pk)
        if user is None:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)

        form = CustomEditForm(instance=user, link='admin-main-view~admin-user', data=request.POST)
        context = {'form': form}
        if form.is_valid():
            email_has_changed = form.prepare_save(request)
            elm = form.save(commit=False)
            elm.save()
            form.save_m2m()
            msg = ''
            if email_has_changed:
                msg = 'Please confirm your new email.'
            return send_success(request=request, context=context,
                                header=_f('Successfully saved'),
                                msg=_f(msg))

        return send_error(self.template_name, status=403, request=request, context=context,
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, user_pk, *args, **kwargs):
        user = get_user(request, user_pk)
        if user is None:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=404)
        form = CustomEditForm(instance=user,
                              link='admin-main-view~admin-user~admin-password-change~&user_pk=%s' % user_pk)
        context = {'form': form}
        return render(request, self.template_name, context)


class AdminPasswordChange(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    template_name = 'Adminview/sdc/admin_password_change.html'
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, user_pk, *args, **kwargs):
        user = get_user(request, user_pk)
        if user is None:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)

        form = SetPasswordForm(user, data=request.POST)
        context = {}
        if form.is_valid():
            form.save()
            return send_success()

        context['form'] = form
        return send_error(self.template_name, status=403, request=request, context={'form': form},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, user_pk, *args, **kwargs):
        user = get_user(request, user_pk)
        if user is None:
            return send_error(header=_f('Action failed!'),
                              msg=_f('User not editable!'),
                              request=request,
                              status=400)

        context = {'form': SetPasswordForm(user)}
        return render(request, self.template_name, context)


class AdminCreateUser(LoginRequiredMixin, UserPassesTestMixin, SDCView):
    template_name = 'Adminview/sdc/admin_create_user.html'
    raise_exception = True

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def post_api(self, request, *args, **kwargs):
        form = CustomUserCreationForm(data=request.POST)

        if form.is_valid():
            form.save()
            return send_success()
        
        return send_error(self.template_name, status=403, request=request, context={'form': form},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, *args, **kwargs):
        context = {'form': CustomUserCreationForm()}
        return render(request, self.template_name, context)
