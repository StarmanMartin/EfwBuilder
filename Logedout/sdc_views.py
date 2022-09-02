from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render



class StartView(SDCView):
    template_name='Logedout/sdc/start_view.html'

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)