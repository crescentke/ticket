from django.contrib.auth.models import User
from django.db import models


class EventCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class EventPrivacy(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class EventType(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Museum(models.Model):
    name = models.CharField(max_length=128, unique=True)
    address = models.CharField(max_length=128)
    status = models.BooleanField(default=True)
    background = models.TextField()
    services = models.TextField()
    cover = models.ImageField(upload_to='museum')
    slug = models.SlugField()

    def __str__(self):
        return self.name


class MuseumTicket(models.Model):
    name = models.CharField(max_length=128)
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE)
    price = models.IntegerField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    available = models.BooleanField(default=True)
    summary = models.TextField()
    status = models.BooleanField(default=True)
    cover = models.ImageField(upload_to='tickets')
    slug = models.SlugField()

    def __str__(self):
        return self.name


class TicketOrder(models.Model):
    ticket = models.ForeignKey(MuseumTicket, on_delete=models.CASCADE)
    qty = models.IntegerField()
    order_code = models.CharField(max_length=128)

    def __str__(self):
        return self.ticket.name


class TicketDelivery(models.Model):
    order_code = models.CharField(unique=True, max_length=128)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    total_cost = models.IntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.order_code


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    privacy = models.ForeignKey(EventPrivacy, on_delete=models.CASCADE)
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    venue = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    cover = models.ImageField(upload_to='media')
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    name = models.CharField(max_length=128)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    price = models.IntegerField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    available = models.BooleanField(default=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    transaction_reference = models.CharField(max_length=128)
    transaction_timestamp = models.CharField(max_length=128)
    transaction_type = models.CharField(max_length=50)
    sender_phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    amount = models.CharField(max_length=128)
    completed = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_reference


class BookedTicket(models.Model):
    order_code = models.CharField(max_length=128)
    ticket = models.ForeignKey(MuseumTicket, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qrcodes')
    slug = models.SlugField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.order_code
