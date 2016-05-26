from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

import json

from .models  import *
from config_parser.config_parser import *

# Create your views here.

def index(request):
    latest_config_requests_list = JSONConfig.objects.order_by('-submit_time')[:5]
    output = ', '.join([q.configuration_text for q in latest_config_requests_list])
    return HttpResponse(output)

def detail(request, jsonconfig_id):
    jsonconfig = get_object_or_404(JSONConfig, pk=jsonconfig_id)
    request_details = request.META.get('HTTP_ACCEPT')
    print "Detail! Request: %s" % request_details

    if "application/json" in request_details:
        return JsonResponse(jsonconfig.to_json())

    return render(request, 'uploadapp/detail.html', {'jsonconfig': jsonconfig})

def new_config(request):
    return render(request, 'uploadapp/new.html')



def settext(request, jsonconfig_id):
    jsonconfig = get_object_or_404(JSONConfig, pk=jsonconfig_id)
    try:
        text_value = request.POST['configuration_text']
        print "Text Value %s: %s" % (1, text_value)
        # Validation goes here:
        json_value = json.loads(text_value)
        config_parser = ConfigurationParser()
        config_parser.parse_configuration(json_value)

    except ConfigurationParserTypeError as e:
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
            'error_message': str(e),
        })

    except ConfigurationParserValueError as e:
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
            'error_message': str(e),
        })

    except (KeyError, JSONConfig.DoesNotExist) as e:
        # FIXME: what to do here for text field?
        # Redisplay the question voting form.
        print "Text Value %s: %s" % (3, text_value)
        print str(type(e)) + " " + str(e)
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
        })
        
    else:
        print "Text Value %s: %s" % (2, text_value)
        jsonconfig.configuration_text = text_value
        jsonconfig.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('uploadapp:detail', args=(jsonconfig.id,)))

def new_config_save(request):
    try:
        text_value = request.POST['configuration_text']
        user_name = request.POST['user_name']
        time = timezone.now()
        print "Text Value %s: %s" % (1, text_value)
        print "User Name %s" % user_name
        # Validation goes here:
        json_value = json.loads(text_value)
        config_parser = ConfigurationParser()
        config_parser.parse_configuration(json_value)

    except ConfigurationParserTypeError as e:
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
            'error_message': str(e),
        })

    except ConfigurationParserValueError as e:
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
            'error_message': str(e),
        })

    except (KeyError, JSONConfig.DoesNotExist) as e:
        # FIXME: what to do here for text field?
        # Redisplay the question voting form.
        print "Text Value %s: %s" % (3, text_value)
        print str(type(e)) + " " + str(e)
        return render(request, 'uploadapp/detail.html', {
            'jsonconfig': jsonconfig,
        })
        
    else:
        jsonconfig = JSONConfig(configuration_text=text_value,
                                submit_time=time,
                                user_name=user_name)
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
