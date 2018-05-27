from django.contrib import admin

from museum.models import EventCategory, EventPrivacy, EventType, Event, Ticket, Museum, MuseumTicket, TicketOrder, \
    TicketDelivery, Payment, BookedTicket


class CustomTicketOrder(admin.ModelAdmin):
    list_display = ('ticket', 'qty', 'order_code',)


class CustomTicketDelivery(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'order_code', 'total_cost', 'paid',)


admin.site.register(EventCategory)
admin.site.register(EventPrivacy)
admin.site.register(EventType)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Museum)
admin.site.register(MuseumTicket)
admin.site.register(TicketOrder, CustomTicketOrder)
admin.site.register(TicketDelivery, CustomTicketDelivery)
admin.site.register(Payment)
admin.site.register(BookedTicket)
