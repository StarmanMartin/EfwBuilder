from django.contrib.auth import authenticate, login, logout

from sdc_tools.django_extension.response import send_success, send_redirect, send_error, sdc_link_factory

from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render
from django.utils.translation import gettext as _f



from sdc_user.form import LoginForm



def get_next(request, default=None, next_next_default:str=None) -> dict[str,any]:
    next_val = request.POST.get('next', request.GET.get('next', default))
    if next_val is None:
        return {'is_next': False, 'next': next_val}
    if request.method.lower().startswith('get'):
        get_values = request.GET.copy()
        if '_method' in get_values:
            del get_values['_method']
        if 'VERSION' in get_values:
            del get_values['VERSION']
        if 'next_next' in get_values:
            del get_values['next_next']
        next_next = request.GET.get('next_next', next_next_default)
        if next_next is None and 'next' in get_values:
            del get_values['next']
        elif next_next is None :
            get_values['next'] = next_next_default
        next_val = sdc_link_factory(next_val, get_values)

    return {'is_next': True, 'next': next_val}

class LoginView(SDCView):
    template_name='sdc_user/sdc/login_view.html'

    form = LoginForm


    def post(self, request, *args, **kwargs):
        form = self.form(request=request, data=request.POST)
        context = get_next(request, 'main-view')
        context['form'] = form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None: # and user.is_email_confirmed:
                login(request, user)
                if not context['is_next']:
                    return send_success(self.template_name, context=context, request=request,
                                        header=_f('Login success'),
                                        pk=user.pk,
                                        msg="%s: %s" % (_f('Login succeeded'), user.email))
                else:
                    return send_redirect(url=context['next'], header=_f('Login success'),
                                         pk=user.pk,
                                         msg="%s: %s" % (_f('Login succeeded'), user.email))

            elif user is not None: # and not user.is_email_confirmed:
                user.send_confirm_email(request)
                return send_error(self.template_name, context=context, request=request, status=403,
                                  header=_f('Login failed'),
                                  msg=_f('Your email is not confirmed. We will send you a new link.'), )

        return send_error(self.template_name, context=context, request=request, status=403, header=_f('Login failed'),
                          msg=_f('Sorry, password or e-mail is not correct'), )

    def get_content(self, request, *args, **kwargs):
        context = get_next(request)
        context['form'] = self.form()
        return render(request, self.template_name, context)

class UserManager(SDCView):
    template_name='sdc_user/sdc/user_manager.html'

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)


class UserLogout(SDCView):
    template_name='sdc_user/sdc/user_logout.html'

    def post(self, request, *args, **kwargs):
        uname = request.user.email
        logout(request)
        next = get_next(request, 'start-view')
        if next['is_next']:
            return send_redirect(url=next['next'], header=_f('Logout success'),
                             msg="%s: %s" % (_f('You are successfully logout:'), uname))

        return send_success()

    def get_content(self, request, *args, **kwargs):
        context = get_next(request)
        return render(request, self.template_name, context=context)