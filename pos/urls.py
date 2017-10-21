from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='order')),
    url(r'^order/$', views.order, name='order'),
    url(r'^addition/(?P<operation>[A-Za-z0-9\.\+\(\)\-\_ ]*)/?$', views.addition, name='addition'),
    url(r'^order/rem/pio/$', views.remove_from_order,
        name='rem_from_order'),
    url(r'^order(?P<order_id>[0-9]+)/rem/pio(?P<pio_id>[0-9]*)/$',
        views.remove_from_order, name='rem_from_order'),
    url(r'^cash/(?P<amount>[0-9\.]*)/?$', views.cash, name='cash')
]
