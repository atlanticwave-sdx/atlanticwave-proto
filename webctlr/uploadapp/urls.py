from django.conf.urls import url

from . import views

app_name = 'uploadapp'
urlpatterns = [
#    url(r'^$', views.index, name='index'),
#    url(r'^specifics/(?P<jsonconfig_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^set/(?P<jsonconfig_id>[0-9]+)/$', views.set_text, name='vote'),

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<jsonconfig_id>[0-9]+)/settext/$', views.settext, name='settext'),
#    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
#    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),


]
