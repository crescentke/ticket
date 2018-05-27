from django.conf.urls import url

from museum.views import Index, Dashboard, CreateEvent, EditEvent, EventTickets, Museums, CreateMuseum, EditMuseum, \
    MuseumTickets, CreateMuseumTickets, EditMuseumTicket, Events, ClientMuseum, ticket_order, ClientPayment, \
    ClientCardPayment, TicketDetail, AdminTickets, AdminTicketDetail, kk_payment, VerifyQR

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^u/museum/(?P<slug>[\w\-]+)/$', ClientMuseum.as_view(), name='client-museum'),
    url(r'^dashboard/$', Dashboard.as_view(), name='dashboard'),
    url(r'^museums/$', Museums.as_view(), name='museums'),
    url(r'^transactions/kopokopo/$', kk_payment, name='kopokopo'),
    url(r'^transactions/test/kopokopo/$', kk_payment, name='test-kopokopo'),
    url(r'^events/$', Events.as_view(), name='events'),
    url(r'^events/tickets/directory/(?P<slug>[\w\-]+)/$', TicketDetail.as_view(), name='ticket-detail'),
    url(r'^events/tickets/verify/(?P<slug>[\w\-]+)/$', VerifyQR.as_view(), name='ticket-verify'),
    url(r'^update-order/$', ticket_order, name='update-order'),
    url(r'^create/museum/$', CreateMuseum.as_view(), name='create-museum'),
    url(r'^payment/order/(?P<order_code>[\w\-]+)/$', ClientPayment.as_view(), name='payment-order'),
    url(r'^payment/order/card/(?P<order_code>[\w\-]+)/$', ClientCardPayment.as_view(), name='payment-order-card'),
    url(r'^create/museum/(?P<pk>[0-9]+)/tickets/$', CreateMuseumTickets.as_view(), name='create-museum-ticket'),
    url(r'^create/event/$', CreateEvent.as_view(), name='create-event'),
    url(r'^edit/museum/(?P<pk>[0-9]+)/$', EditMuseum.as_view(), name='edit-museum'),
    url(r'^edit/museum/(?P<pk>[0-9]+)/tickets/(?P<tk>[0-9]+)/$', EditMuseumTicket.as_view(), name='edit-museum-ticket'),
    url(r'^edit/event/(?P<pk>[0-9]+)/$', EditEvent.as_view(), name='edit-event'),
    url(r'^edit/event/(?P<pk>[0-9]+)/tickets/$', EventTickets.as_view(), name='event-tickets'),
    url(r'^edit/museum/(?P<pk>[0-9]+)/tickets/$', MuseumTickets.as_view(), name='museum-tickets'),

    url(r'^tickets/$', AdminTickets.as_view(), name='tickets'),
    url(r'^tickets/directory/(?P<slug>[\w\-]+)/$', AdminTicketDetail.as_view(), name='admin-ticket-detail'),
]
