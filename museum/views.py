import random
import string
from datetime import datetime

import qrcode
import requests
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Index
from django.template.loader import get_template
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView
from django_pesapal.views import PaymentRequestMixin

from museum.forms import EventForm, TicketForm, MuseumForm, MuseumTicketForm, TicketBookForm, \
    TicketDeliveryForm, PaymentConfirmForm, PaymentCardForm
from museum.models import Event, Ticket, Museum, MuseumTicket, TicketOrder, TicketDelivery, Payment, BookedTicket
from ticket.settings import EMAIL_HOST_USER


def random_code(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Index(View):
    template_name = 'base.html'

    museums = Museum.objects.all()
    museum_tickets = MuseumTicket.objects.all()

    context = {
        'museums': museums,
        'tickets': museum_tickets
    }

    def get(self, request):
        if request.GET.get('q') is not None:
            q = request.GET.get('q')
            self.context['tickets'] = self.museum_tickets.filter(Q(name__icontains=q))
        return render(request, self.template_name, self.context)


class ClientMuseum(View):
    template_name = 'client/museum.html'

    context = {}

    def get(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, slug=kwargs['slug'])

        ticket_del_form = TicketDeliveryForm()
        ticket_qty_form = TicketBookForm()
        self.context['museum'] = museum
        self.context['ticket_del_form'] = ticket_del_form
        self.context['ticket_qty_form'] = ticket_qty_form
        self.context['tickets'] = MuseumTicket.objects.filter(museum=museum.id)
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        ticket_del_form = TicketDeliveryForm(request.POST)
        print(request.POST.get('order_code'))
        # print(ticket_del_form.is_valid())
        # print(ticket_del_form.errors)
        if ticket_del_form.is_valid():
            save_order = ticket_del_form.save(commit=False)
            order_items = TicketOrder.objects.filter(order_code=request.POST.get('order_code'))
            total_cost = 0
            for order_item in order_items:
                total_cost += order_item.ticket.price
            save_order.total_cost = total_cost
            save_order.save()

            # if request.POST.get('payment_mode') is '0':
            #     return redirect('payment-order', order_code=request.POST.get('order_code'))
            # else:
            #     return redirect('payment-order-card', order_code=request.POST.get('order_code'))

            return redirect('payment-order', order_code=request.POST.get('order_code'))

        else:
            messages.error(request, ticket_del_form.errors)
            return render(request, self.template_name, self.context)


class ClientPayment(View):
    template_name = 'client/process_payment.html'

    context = {}

    def get(self, request, *args, **kwargs):
        order_data = get_object_or_404(TicketDelivery, order_code=kwargs['order_code'])
        ticket_order_data = TicketOrder.objects.filter(order_code=kwargs['order_code'])
        for to in ticket_order_data:
            museum = to.ticket.museum

        self.context['museum'] = museum
        self.context['order_data'] = order_data
        self.context['confirm_form'] = PaymentConfirmForm()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        # Get order details
        order_list = TicketOrder.objects.filter(order_code=kwargs['order_code'])
        if order_list.count() == 1:
            order_data = get_object_or_404(TicketOrder, order_code=kwargs['order_code'])
            amount = order_data.qty * order_data.ticket.price
            this_order_code = order_data.order_code

        elif order_list.count() > 1:
            amount = 0
            this_order_code = 0

            for ol in order_list:
                amount += ol.qty * ol.ticket.price
                this_order_code = ol.order_code
        else:
            messages.error(request, 'Order not found')
            return redirect('payment-order', order_code=kwargs['order_code'])

        # Get transaction details
        confirm_form = PaymentConfirmForm(request.POST)

        if confirm_form.is_valid():
            amount_paid = 0
            raw_codes = request.POST.get('code')
            raw_codes_clean = raw_codes.split(',')
            new_codes = ''
            for raw_code in raw_codes_clean:
                code_count = raw_codes.count(raw_code)
                if code_count is 1:
                    new_codes += '%s,' % raw_code
                elif code_count > 1:
                    if new_codes.count(raw_code) is 0:
                        new_codes += '%s,' % raw_code
                print(new_codes)

            codes = new_codes.split(',')[:-1]
            print(codes)
            for code in codes:
                current_transaction = Payment.objects.filter(transaction_reference=code,
                                                             sender_phone=request.POST.get('phone'), completed=False)
                if current_transaction.count() > 0:
                    current_transaction = Payment.objects.get(transaction_reference=code,
                                                              sender_phone=request.POST.get('phone'),
                                                              completed=False)
                    amount_paid += int(current_transaction.amount)
                else:
                    messages.error(request, 'Transaction code: %s is invalid.' % code)
                print(code.strip())

            if amount_paid >= amount:

                ticket_slug = slugify(random_code(12))
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data('/events/tickets/verify/%s' % ticket_slug)
                qr.make(fit=True)

                product_qrcode = qr.make_image()
                product_qrcode.save('media/qrcodes/%s.png' % ticket_slug)

                if order_list.count() == 1:
                    booked_ticket = BookedTicket()
                    booked_ticket.order_code = this_order_code
                    booked_ticket.ticket = order_data.ticket
                    booked_ticket.qr_code = 'qrcodes/%s.png' % ticket_slug
                    booked_ticket.slug = ticket_slug
                    booked_ticket.save()
                elif order_list.count() > 1:
                    for oli in order_list:
                        booked_ticket = BookedTicket()
                        booked_ticket.order_code = this_order_code
                        booked_ticket.ticket = oli.ticket
                        booked_ticket.qr_code = 'qrcodes/%s.png' % ticket_slug
                        booked_ticket.slug = ticket_slug
                        booked_ticket.save()

                messages.success(request, "Fully paid %s" % amount)
                image_data = open('media/qrcodes/%s.png' % ticket_slug, "rb").read()

                # Send ticket to email
                ticket_delivery = get_object_or_404(TicketDelivery, order_code=this_order_code)

                subject = "%s Museum Ticket" % order_data.ticket.museum.name
                to = [ticket_delivery.email]
                from_email = EMAIL_HOST_USER

                booked_tickets = BookedTicket.objects.filter(order_code=this_order_code)
                context = {
                    'order_data': order_data,
                    'ticket_delivery': ticket_delivery,
                    'booked_tickets': booked_tickets
                }
                message = get_template('email/ticket_email.html').render(context)
                msg = EmailMessage(subject, message, to=to, from_email=from_email)
                msg.content_subtype = 'html'
                msg.send()

                return redirect('ticket-detail', slug=this_order_code)
                # return HttpResponse(image_data, content_type="image/png")

            else:
                messages.error(request, "Pay the remaining balance of %s" % str(amount - amount_paid))
                self.context['confirm_form'] = confirm_form
                return render(request, self.template_name, self.context)

        else:
            messages.error(request, confirm_form.errors)
            self.context['confirm_form'] = confirm_form
            return render(request, self.template_name, self.context)


class TicketDetail(View):
    template_name = 'client/ticket.html'

    context = {}

    def get(self, request, *args, **kwargs):
        order_list = TicketOrder.objects.filter(order_code=kwargs['slug'])
        if order_list.count() == 1:
            order_data = get_object_or_404(TicketOrder, order_code=kwargs['slug'])

        elif order_list.count() > 1:
            amount = 0
            this_order_code = 0

            for ol in order_list:
                amount += ol.qty * ol.ticket.price
                this_order_code = ol.id

            order_data = get_object_or_404(TicketOrder, id=this_order_code)

        booked_tickets = BookedTicket.objects.filter(order_code=order_data.order_code)

        self.context['order_data'] = order_data
        self.context['booked_tickets'] = booked_tickets
        return render(request, self.template_name, self.context)


class ClientCardPayment(View, PaymentRequestMixin):
    template_name = 'client/payment.html'

    context = {}

    def get_pesapal_payment_iframe(self, order):
        '''
        Authenticates with pesapal to get the payment iframe src
        '''
        order_info = {
            'first_name': order.first_name,
            'last_name': order.last_name,
            'amount': order.total_cost,
            'description': 'Payment for Museum ticket Order No: %s' % order.order_code,
            'reference': order.order_code,  # some object id
            'email': order.email,
        }

        iframe_src_url = self.get_payment_url(**order_info)
        return iframe_src_url

    def get(self, request, *args, **kwargs):
        order_data = get_object_or_404(TicketDelivery, order_code=kwargs['order_code'])
        ticket_order_data = TicketOrder.objects.filter(order_code=kwargs['order_code'])
        for to in ticket_order_data:
            museum = to.ticket.museum

        self.context['card_payment'] = PaymentCardForm()
        self.context['museum'] = museum
        self.context['order_data'] = order_data
        self.context['payment_iframe'] = self.get_pesapal_payment_iframe(order_data)
        return render(request, self.template_name, self.context)


@csrf_exempt
def kk_payment(request):
    if request.method == "POST":
        transaction_reference = request.POST.get("transaction_reference")
        transaction_timestamp = request.POST.get("transaction_timestamp")
        transaction_type = request.POST.get("transaction_type")
        sender_phone = request.POST.get("sender_phone")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        amount = request.POST.get("amount")

        kk_transaction = Payment(
            transaction_reference=transaction_reference,
            transaction_timestamp=transaction_timestamp,
            transaction_type=transaction_type,
            sender_phone=sender_phone,
            first_name=first_name,
            last_name=last_name,
            amount=amount
        )

        # Save transaction
        kk_transaction.save()

        return HttpResponse('%s %s %s %s %s %s %s' % (
            transaction_reference, transaction_timestamp, transaction_type, sender_phone, first_name, last_name,
            amount))
    else:
        return HttpResponse("Not allowed %s" % request.method)


def test_pay(request):
    payload = {
        'transaction_reference': 'MEL4IZBS1Q',
        'transaction_timestamp': '2018-05-21T13:25:09Z',
        'transaction_type': 'buygoods',
        'sender_phone': '+254704230735',
        'first_name': 'CRESCENT',
        'last_name': 'MUSYOKI',
        'amount': '1.0',
    }
    r = requests.post("http://127.0.0.1:8000/transactions/kopokopo/", data=payload)
    return HttpResponse(r.text)


def ticket_order(request):
    if request.method == 'GET':
        ticket_id = request.GET['ticket_id']
        qty = request.GET['qty']

        ticket_fetched = MuseumTicket.objects.get(id=ticket_id)

        # Set order code
        if request.session.get('order_code', False):
            order_code = request.session['order_code']
        else:
            order_code = random_code()
            request.session['order_code'] = order_code

        # Check if order item exists
        avail_item = TicketOrder.objects.filter(ticket=ticket_fetched, order_code=order_code)
        if avail_item:
            avail_item_obj = TicketOrder.objects.get(ticket=ticket_fetched, order_code=order_code)
            avail_item_obj.qty = qty
            avail_item_obj.save()
        else:
            ticket_ordered = TicketOrder()
            ticket_ordered.ticket = ticket_fetched
            ticket_ordered.qty = qty
            ticket_ordered.order_code = order_code
            ticket_ordered.save()

        return HttpResponse(order_code)


class Dashboard(View):
    template_name = 'dashboard/dashboard.html'
    context = {
        'title': 'Dashboard',
        'dashboard_active': True
    }

    def get(self, request):
        self.context['museums'] = Museum.objects.all().count()
        self.context['events'] = Event.objects.filter(user=request.user)
        return render(request, self.template_name, self.context)


class Museums(View):
    template_name = 'dashboard/museum/museums.html'
    context = {
        'title': 'Museums',
        'museum_active': True
    }

    def get(self, request):
        self.context['museums'] = Museum.objects.all()
        return render(request, self.template_name, self.context)


class CreateMuseum(View):
    template_name = 'dashboard/museum/create_museum.html'
    success_url = '/museums/'
    context = {
        'title': 'Create Museum',
        'museum_active': True
    }

    def get(self, request):
        form = MuseumForm()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = MuseumForm(request.POST, request.FILES or None)
        if form.is_valid():
            mt = form.save(commit=False)
            mt.slug = slugify(random_code())
            mt.save()
            messages.success(request, 'Museum created')
            return redirect(self.success_url)
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class EditMuseum(View):
    template_name = 'dashboard/museum/edit_museum.html'
    context = {
        'museum_active': True,
        'details_selected': True
    }

    def get(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        self.context['museum'] = museum
        self.context['title'] = museum.name
        self.context['form'] = MuseumForm(initial={
            'name': museum.name,
            'address': museum.address,
            'background': museum.background,
            'services': museum.services
        })
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        form = MuseumForm(request.POST, request.FILES or None, instance=museum)
        if form.is_valid():
            form.save()
            messages.success(request, 'Museum updated')
            return redirect('edit-museum', pk=kwargs['pk'])
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class MuseumTickets(View):
    template_name = 'dashboard/museum/tickets.html'
    context = {'tickets_selected': True}

    def get(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        tickets = MuseumTicket.objects.filter(museum=kwargs['pk'], status=True)
        self.context['museum'] = museum
        self.context['title'] = museum.name
        self.context['tickets'] = tickets
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket saved')
            return redirect('museum-tickets', pk=kwargs['pk'])
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class CreateMuseumTickets(View):
    template_name = 'dashboard/museum/create_ticket.html'
    context = {'tickets_selected': True}

    def get(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        self.context['museum'] = museum
        self.context['title'] = museum.name
        self.context['form'] = MuseumTicketForm(initial={'museum': museum})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = MuseumTicketForm(request.POST, request.FILES or None)
        if form.is_valid():
            mt = form.save(commit=False)
            mt.slug = slugify(random_code())
            mt.save()
            messages.success(request, 'Ticket saved')
            return redirect('museum-tickets', pk=kwargs['pk'])
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class EditMuseumTicket(View):
    template_name = 'dashboard/museum/edit_ticket.html'
    context = {
        'museum_active': True
    }

    def get(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        ticket = get_object_or_404(MuseumTicket, id=kwargs['tk'])
        self.context['museum'] = museum
        self.context['title'] = museum.name
        self.context['form'] = MuseumTicketForm(instance=ticket)
        self.context['ticket'] = ticket
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        museum = get_object_or_404(Museum, id=kwargs['pk'])
        ticket = get_object_or_404(MuseumTicket, id=kwargs['tk'])
        form = MuseumTicketForm(request.POST, request.FILES or None, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated')
            return redirect('edit-museum-ticket', pk=kwargs['pk'], tk=kwargs['tk'])
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class Events(View):
    template_name = 'dashboard/event/events.html'
    context = {
        'title': 'Events',
        'event_active': True
    }

    def get(self, request):
        self.context['events'] = Event.objects.all()
        return render(request, self.template_name, self.context)


class CreateEvent(View):
    template_name = 'dashboard/event/create_event.html'
    success_url = '/events/'
    context = {
        'title': 'Create Event'
    }

    def get(self, request):
        form = EventForm(initial={'user': request.user})
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = EventForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created')
            return redirect(self.success_url)
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class EditEvent(View):
    template_name = 'dashboard/event/edit_event.html'
    success_url = '/edit/event/'
    context = {'details_selected': True}

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs['pk'])
        self.context['event'] = event
        self.context['title'] = event.name
        self.context['form'] = EventForm(initial={
            'name': event.name,
            'venue': event.venue,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'category': event.category,
            'type': event.type,
            'privacy': event.privacy,
            'cover': event.cover,
            'description': event.description
        })
        return render(request, self.template_name, self.context)


class EventTickets(View):
    template_name = 'dashboard/event/event_tickets.html'
    context = {'tickets_selected': True}

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs['pk'])
        tickets = Ticket.objects.filter(event=kwargs['pk'])
        self.context['event'] = event
        self.context['title'] = event.name
        self.context['tickets'] = tickets
        self.context['form'] = TicketForm(initial={'event': event})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket saved')
            return redirect('event-tickets', pk=kwargs['pk'])
        else:
            self.context['form'] = form
            messages.error(request, form.errors)
            return render(request, self.template_name, self.context)


class AdminTickets(View):
    template_name = 'dashboard/ticket/tickets.html'
    context = {
        'title': 'Tickets',
        'ticket_active': True
    }

    def get(self, request):
        self.context['tickets'] = BookedTicket.objects.all()
        return render(request, self.template_name, self.context)


class AdminTicketDetail(View):
    template_name = 'dashboard/ticket/detail.html'

    context = {'title': 'Tickets',
               'ticket_active': True}

    def get(self, request, *args, **kwargs):
        ticket_data = get_object_or_404(BookedTicket, slug=kwargs['slug'])

        self.context['ticket_data'] = ticket_data
        return render(request, self.template_name, self.context)


class VerifyQR(View):

    def get(self, request, *args, **kwargs):
        ticket_data = get_object_or_404(BookedTicket, slug=kwargs['slug'])

        today = datetime.now()

        if ticket_data.ticket.valid_from >= today and ticket_data.ticket.valid_to <= today:
            released = True
            msg = 'Ticket is valid'
        else:
            released = False
            msg = 'Ticket is invalid'

        print(today)

        return JsonResponse({
            'name': ticket_data.ticket.name,
            'poster': ticket_data.ticket.cover.url,
            'duration': msg,
            'price': ticket_data.ticket.price,
            'director': ticket_data.ticket.museum.name,
            'genre': 'Something',
            'rating': '3.4',
            'released': released
        }, safe=False)
