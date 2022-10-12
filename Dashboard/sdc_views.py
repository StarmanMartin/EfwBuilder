import json

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponse
from django.http.response import HttpResponseServerError

from WebDAV.resources import ReadFSDavResource
from sdc_tools.django_extension.views import SDCView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from sdc_tools.django_extension import search
from django.utils.translation import gettext as _f
from django.utils.translation import gettext_lazy as _
from sdc_tools.django_extension.response import send_error, send_success, send_redirect
from Dashboard.models import InstanceSearchForm, Instance, InstanceForm, UmlSearchForm, UmlDiagram, UmlDiagramForm, \
    UmlElement, UmlSegment, UmlLayer, UmlField, LocalInstanceForm


class MainView(LoginRequiredMixin, SDCView):
    template_name = 'Dashboard/sdc/main_view.html'
    raise_exception = True

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EfwNew(LoginRequiredMixin, SDCView):
    raise_exception = True
    template_name='Dashboard/sdc/efw_new.html'

    def post_api(self, request, type, *args, **kwargs):
        if type == 'instance':
            form = InstanceForm(data=request.POST)
        elif type == 'local':
            form = LocalInstanceForm(data=request.POST)
        else:
            form = None

        if form is not None and form.is_valid():
            form.save()
            return send_redirect(back=True, header=_f('Success!!'),
                                msg=_f('New Instance is saved!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form, 'form_type': type},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, type, *args, **kwargs):
        context = {'form_type': type}
        if type == 'instance':
            context['form'] = InstanceForm()
        elif type == 'local':
            context['form'] = LocalInstanceForm()

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
                                msg=_f('Instance is saved!'))

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
        try:
            file_location = instance.build()
            with open(file_location, 'rb') as f:
                file_data = f.read()


            # sending response
            response = HttpResponse(file_data, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="efw.exe"'

        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound('<h1>File not exist</h1>')
        except:
            response = HttpResponseServerError('<h1>%s</h1>' % _('There was en compilation error. Maybe you have used \\ in the src instead of \\\\.'))

        return response

class UmlEditor(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/uml_editor.html'

    def post_api(self, request, dia_pk, *args, **kwargs):
        try:
            uml = UmlDiagram.objects.get(pk=dia_pk)
        except:
            return send_error(header=_f('No Diagram!'))
        data_str = request.POST.get('json', None)
        if data_str is None:
            return send_error(header=_f('Empty payload!'))
        data = json.loads(data_str)

        try:
            with transaction.atomic():
                uml.elements.all().delete()
                token_list = {}
                for elem in data.get('elements', []):
                    umlElement = UmlElement.create_from_json(uml, elem)
                    token_list[umlElement.token] = umlElement
                    seg_order = 0
                    for segments in elem['segments']:
                        seg_order += 10
                        umlSegment = UmlSegment.create_from_json(umlElement, segments, seg_order)
                        layer_order = 0
                        for layer in segments['layers']:
                            seg_order += 10
                            umlLayer = UmlLayer.create_from_json(umlSegment, layer, layer_order)
                            field_order = 0
                            for field in layer['fields']:
                                field_order += 10
                                layer_order = UmlField.create_from_json(umlLayer, field, field_order)

                for rels in data.get('relations', []):
                    token_list[rels[0]].extends.add(token_list[rels[1]])

        except ValidationError as e:
            return send_error(request=request, msg='\n'.join(e.messages), header=_f('Error while saving!'))
        except Exception as e:
            return send_error(request=request, header=_f('Unknown error while saving!'))
        return send_success(request=request, header=_f('Successfully saved!'))

    def get_content(self, request, dia_pk, *args, **kwargs):
        uml = UmlDiagram.objects.get(pk=dia_pk)
        return render(request, self.template_name, {'uml': uml})

class UmlInfo(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/uml_info.html'

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)

class UmlCreate(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/uml_create.html'

    def post_api(self, request, *args, **kwargs):
        form = UmlDiagramForm(data=request.POST)

        if form.is_valid():
            form.save()
            return send_redirect(back=True, header=_f('Success!!'),
                                msg=_f('New UML is saved!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, *args, **kwargs):
        context = {'form': UmlDiagramForm()}
        return render(request, self.template_name, context)

class UmlChange(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/uml_change.html'

    def post_api(self, request, dia_pk, *args, **kwargs):
        instance = UmlDiagram.objects.get(pk=dia_pk)
        form = UmlDiagramForm(instance=instance, data=request.POST)

        if form.is_valid():
            form.save()
            return send_success(header=_f('Success!!'),
                                msg=_f('UML is saved!'))

        return send_error(self.template_name, status=403, request=request, context={'form': form, 'pk': dia_pk},
                          header=_f('Upps!!'),
                          msg=_f('Please check your details.'))

    def get_content(self, request, dia_pk, *args, **kwargs):
        instance = UmlDiagram.objects.get(pk=dia_pk)
        context = {'form': UmlDiagramForm(instance=instance), 'pk': dia_pk}
        return render(request, self.template_name, context)

class UmlList(LoginRequiredMixin, SDCView):
    template_name='Dashboard/sdc/uml_list.html'
    search_form = UmlSearchForm
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
        return search.handle_search_form(UmlDiagram.objects, form, filter_dict=form.generate_filte(),
                                         range=self.range_size)

class FileTree(SDCView):
    template_name='Dashboard/sdc/file_tree.html'

    def get_content(self, request, *args, **kwargs):
        context = {'root': ReadFSDavResource("/")}
        return render(request, self.template_name, context)

class BasicInfo(SDCView):
    template_name='Dashboard/sdc/basic_info.html'

    def get_content(self, request, *args, **kwargs):
        return render(request, self.template_name)