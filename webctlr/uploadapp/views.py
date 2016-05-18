from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from .models  import *

# Create your views here.

def index(request):
    latest_config_requests_list = JSONConfig.objects.order_by('-submit_time')[:5]
    output = ', '.join([q.configuration_text for q in latest_config_requests_list])
    return HttpResponse(output)

def detail(request, jsonconfig_id):
    jsonconfig = get_object_or_404(JSONConfig, pk=jsonconfig_id)
    return render(request, 'uploadapp/detail.html', {'jsonconfig': jsonconfig})

def settext(request, jsonconfig_id):
    jsonconfig = get_object_or_404(JSONConfig, pk=jsonconfig_id)
    try:
        text_value = request.POST['configuration_text']
#        jsonconfig.configuration_text.get(pk=request.POST['configuration_text'])
    except (KeyError, JSONConfig.DoesNotExist):
        # FIXME: what to do here for text field?
        # Redisplay the question voting form.
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
        })
    else:
        jsonconfig.configuration_text = text_value
        jsonconfig.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('uploadapp:detail', args=(jsonconfig.id,)))


class IndexView(generic.ListView):
    template_name = 'uploadapp/index.html'
    context_object_name = 'latest_config_request_list'

    def get_queryset(self):
        """Return the last five submitted configuration request."""
        return JSONConfig.objects.order_by('-submit_time')[:5]


class DetailView(generic.DetailView):
    model = JSONConfig
    template_name = 'uploadapp/detail.html'


class ResultsView(generic.DetailView):
    model = JSONConfig
    template_name = 'uploadapp/results.html'
