from django import forms
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext_lazy as _
from sdc_tools.django_extension.forms import AbstractSearchForm


class SearchSelectField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(SearchSelectField, self).__init__(*args, **kwargs)
        self.widget = SearchSelectInput()

    def set_form_value(self, fv):
        self.widget.set_form_value(fv)


    def validate(self, value):
        super(SearchSelectField, self).validate(value)
        return


class SearchSelectInput(forms.widgets.Input):
    template_name = 'Utils/widgets/search_elect.html'
    input_type = 'text'
    form_value = ''

    def set_form_value(self, fv):
        self.form_value = fv

    def get_context(self, name, value, attrs):
        context = super(SearchSelectInput, self).get_context(name, value, attrs)
        context['widget']['form_value'] =  self.form_value
        return context

    def value_from_datadict(self, data, files, name):
        val = data.get(name, "")
        if val == "":
            val = []
        else:
            val = val.split(',')
        return val




RegisteredForm = {

}
