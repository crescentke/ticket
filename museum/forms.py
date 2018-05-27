from django import forms
from django.contrib.auth.models import User

from museum.models import Event, EventCategory, EventPrivacy, EventType, Ticket, Museum, MuseumTicket, TicketDelivery


class MuseumForm(forms.ModelForm):
    name = forms.CharField(max_length=128, label='Museum Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Museum Name'}))
    address = forms.CharField(max_length=128, label='Museum Address',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Museum Address'}))
    background = forms.CharField(label='Museum Background',
                                 widget=forms.Textarea(
                                     attrs={'class': 'wysihtml5 form-control', 'rows': 9,
                                            'placeholder': 'Museum Details or Historical Background'}))
    services = forms.CharField(label='Museum Services/Facilities',
                               widget=forms.Textarea(
                                   attrs={'class': 'wysihtml5 form-control', 'rows': 9,
                                          'placeholder': 'Services or Facilities in the museum'}))
    cover = forms.ImageField(label='Museum Cover', widget=forms.FileInput(attrs={'class': 'form-control'}),
                             required=False)

    class Meta:
        model = Museum
        fields = ('name', 'address', 'cover', 'background', 'services')


class EventForm(forms.ModelForm):
    name = forms.CharField(max_length=128, label='Event Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}))
    start_date = forms.CharField(max_length=128, label='Start Date',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Date'}))
    end_date = forms.CharField(max_length=128, label='End Date',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'End Date'}))
    category = forms.ModelChoiceField(queryset=EventCategory.objects.all(), label='Event Category',
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    privacy = forms.ModelChoiceField(queryset=EventPrivacy.objects.all(), label='Event Privacy',
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    type = forms.ModelChoiceField(queryset=EventType.objects.all(), label='Event Type',
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    venue = forms.CharField(max_length=128, label='Event Venue',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Venue'}))
    description = forms.CharField(max_length=128, label='Event Description',
                                  widget=forms.Textarea(
                                      attrs={'class': 'wysihtml5  form-control', 'placeholder': 'Event Description'}))
    cover = forms.FileField(max_length=128, label='Event Cover',
                            widget=forms.FileInput(attrs={'class': 'form-control'}))
    user = forms.ModelChoiceField(User.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Event
        fields = (
            'user', 'category', 'privacy', 'type', 'name', 'venue', 'start_date', 'end_date', 'cover', 'description')


class TicketForm(forms.ModelForm):
    name = forms.CharField(label='Ticket Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Name'}))
    event = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.HiddenInput())
    price = forms.IntegerField(label='Ticket Price',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Price'}))
    valid_from = forms.CharField(max_length=128, label='Valid From',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valid From'}))
    valid_to = forms.CharField(max_length=128, label='Valid To',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valid To'}))
    available = forms.BooleanField(label='Check below if the tickets are available for purchase',
                                   widget=forms.CheckboxInput(
                                       attrs={'class': '', 'placeholder': 'Available'}), required=False)

    class Meta:
        model = Ticket
        fields = ('name', 'event', 'price', 'valid_from', 'valid_to', 'available')


class MuseumTicketForm(forms.ModelForm):
    name = forms.CharField(label='Ticket Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Name'}))
    museum = forms.ModelChoiceField(queryset=Museum.objects.all(), widget=forms.HiddenInput())
    price = forms.IntegerField(label='Ticket Price',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Price'}))
    valid_from = forms.CharField(max_length=128, label='Valid From',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valid From'}))
    valid_to = forms.CharField(max_length=128, label='Valid To',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valid To'}))
    available = forms.BooleanField(label='Check below if the tickets are available for purchase',
                                   widget=forms.CheckboxInput(
                                       attrs={'class': '', 'placeholder': 'Available'}), required=False)
    cover = forms.ImageField(label='Ticket Cover', widget=forms.FileInput(attrs={'class': 'form-control'}),
                             required=False)
    summary = forms.CharField(label='Museum Services/Facilities',
                              widget=forms.Textarea(
                                  attrs={'class': 'wysihtml5 form-control', 'rows': 9,
                                         'placeholder': 'Services or Facilities in the museum'}))

    class Meta:
        model = MuseumTicket
        fields = ('name', 'museum', 'cover', 'price', 'valid_from', 'valid_to', 'available', 'summary')


class TicketDeliveryForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email address'}))
    phone = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07'}))
    order_code = forms.CharField(widget=forms.HiddenInput())
    payment_mode = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = TicketDelivery
        fields = ('order_code', 'first_name', 'last_name', 'phone', 'email',)


class TicketBookForm(forms.Form):
    qty = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'QTY', 'value': 0, 'min': 0}))


class PaymentConfirmForm(forms.Form):
    phone = forms.CharField(max_length=13, min_length=13,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2547'}))
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LCR4HCBJS2, LCR4HCBJS3'}))


class PaymentCardForm(forms.Form):
    card_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'card name'}))
    card_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'card number'}))
    card_expiry = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'card expiry date'}))
