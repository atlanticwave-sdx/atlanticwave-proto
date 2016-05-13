from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def detail(request, jsonconfig_id):
    return HttpResponse("You're looking at question %s." % question_id)
