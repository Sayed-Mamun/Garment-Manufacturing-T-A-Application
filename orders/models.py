# orders/models.py
from django.db import models

class Order(models.Model):
    style_number = models.CharField(max_length=100)
    buyer = models.CharField(max_length=255)
    order_quantity = models.IntegerField()
    shipment_date = models.DateField()
    fabric_details = models.TextField(blank=True)
    trim_details = models.TextField(blank=True)

class UploadedPDF(models.Model):
    file = models.FileField(upload_to='order_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
