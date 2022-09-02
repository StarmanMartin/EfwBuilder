from django.http import Http404
from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render

from Utils.form import RegisteredForm
from sdc_tools.django_extension.search import handle_search_form

def admin_user_test(request):
    return True

class Fof(SDCView):
    template_name='Utils/sdc/fof.html'

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)

class Error(SDCView):
    template_name='Utils/sdc/error.html'

    def get_content(self, request, code, *args, **kwargs):
        return render(request, self.template_name, {'code': int(code)})

class SearchSelectInput(SDCView):
    template_name='Utils/sdc/search_select_input.html'

    raise_exception = True
    range_size = 10

    def get_form_model(self, model: str, request):
        if model not in RegisteredForm:
            raise Http404

        search_form = RegisteredForm[model]
        if request is not None:
            form = search_form['form'](request.POST)
        else:
            form = search_form['form']([])
        return (form, search_form['model'], search_form.get('sdc_link', None))

    def test_func(self):
        request = self.request
        return admin_user_test(request)

    def search(self, request, model, value, *args, **kwargs):
        return self.get_content(request, model, None, *args, **kwargs)

    def get_content(self, request, model, value, *args, **kwargs):
        context = self.get_context(model, value, request)
        return render(request, self.template_name, context=context)

    def get_context(self, model, value, request=None):
        (form, ModelObj, cc) = self.get_form_model(model, request)
        form.is_valid()
        ctx = handle_search_form(ModelObj.objects, form, filter_dict=form.generate_filte(),
                                         range=self.range_size)
        ctx['model_name'] = model
        ctx['cc'] = cc
        if value is None or value == '':
            ctx['selected'] = []
        else:
            ctx['selected'] = ModelObj.objects.filter(pk__in=value.split(','))
        return ctx