from django.http import HttpResponseNotFound, HttpResponse
from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from sdc_tools.django_extension import search
from django.utils.translation import gettext as _f
from sdc_tools.django_extension.response import send_error, send_success
from Dashboard.models import InstanceSearchForm, Instance, InstanceForm


class MainView(LoginRequiredMixin, SDCView):
    template_name = 'Dashboard/sdc/main_view.html'
    raise_exception = True

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EfwNew(LoginRequiredMixin, SDCView):
    raise_exception = True
    template_name='Dashboard/sdc/efw_new.html'

    def post_api(self, request, *args, **kwargs):
        form = InstanceForm(data=request.POST)

        if form.is_valid():
            form.save()
            return send_success(header=_f('Success!!'),
                                msg=_f('New Instance is saved!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, *args, **kwargs):
        context = {'form': InstanceForm()}
        return render(request, self.template_name, context)


class EfwEdit(LoginRequiredMixin, SDCView):
    raise_exception = True
    template_name='Dashboard/sdc/efw_edit.html'

    def post_api(self, request, efw_pk, *args, **kwargs):
        instance = Instance.objects.get(pk=efw_pk)
        form = InstanceForm(instance=instance, data=request.POST)

        if form.is_valid():
            form.save()
            return send_success(header=_f('Success!!'),
                                msg=_f('New Instance is saved!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form, 'pk': efw_pk},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, efw_pk, *args, **kwargs):
        instance = Instance.objects.get(pk=efw_pk)
        context = {'form': InstanceForm(instance=instance), 'pk': efw_pk}
        return render(request, self.template_name, context)

class EfwList(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/efw_list.html'
    search_form = InstanceSearchForm
    range_size = 10

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
        return search.handle_search_form(Instance.objects, form, filter_dict=form.generate_filte(),
                                         range=self.range_size)




class EfwDownload(LoginRequiredMixin, SDCView):
    raise_exception = True

    def get(self, request, efw_pk, *args, **kwargs):
        instance = Instance.objects.get(pk=efw_pk)
        file_location = instance.build()
        try:
            with open(file_location, 'rb') as f:
                file_data = f.read()


            # sending response
            response = HttpResponse(file_data, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="efw.exe"'

        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')

        return response