from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^order/$', views.order, name='order'),
    url(r'^addition/(?P<operation>[A-Za-z0-9]*)/?$', views.addition, name='addition'),
]
