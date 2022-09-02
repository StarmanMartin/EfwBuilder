from sdc_tools.django_extension.forms import AbstractSearchForm

from django.utils.translation import gettext_lazy as _

class UserSearchForm(AbstractSearchForm):
    CHOICES = (('username', _('Abbr.')), ('email', _('Email')), ('first_name', _('First name')), ('last_name', _('Last name')))
    PLACEHOLDER = _('Abbr., Email, First name, Last name')
    DEFAULT_CHOICES = CHOICES[0][0]
    SEARCH_FIELDS = ('email', 'username', 'first_name', 'first_name', 'last_name')

    def generate_filte(self):
        pass