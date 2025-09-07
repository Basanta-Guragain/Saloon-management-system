from sqlite3 import Date
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    id=models.AutoField(blank=False, null=False,primary_key=True)
    name=models.CharField(max_length=100,blank=False,null=False)
    email=models.EmailField(max_length=100,unique=True)
    password=models.CharField(max_length=50,blank=False,null=False)

    # created_at = models.DateTimeField(auto_now_add=True)   
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"customer_id : {self.id} - customer_name : {self.name}"


 
class Services(models.Model):
    CATEGORY_CHOICE=(
    ('HR','Hairstyle'),
    ('HC','Hair colour'),
    ('HS','Hair Spa'), 
)
    name=models.CharField(max_length=100,blank=False,null=False)
    price=models.FloatField(  ) 
    category=models.CharField(choices=CATEGORY_CHOICE, max_length=2,default='HR')
    service_img=models.ImageField(upload_to='service')

    def __str__(self):
        return self.name

class Booking(models.Model):
    
    name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField(default="no-reply@example.com")
    phone_number = PhoneNumberField(region='NP',max_length=10, null=True, blank=True)
    date = models.DateField(default=Date.today)
    time = models.TimeField(default="09:00")
    services = models.ManyToManyField(Services)
    additional_services = models.ManyToManyField('Services', related_name="additional_bookings", blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)



    def __str__(self):
        service_names = ", ".join([service.name for service in self.services.all()])
        return f"Booking {self.id} - {self.name} for {service_names} on {self.date} at {self.time}"

        # Booking 1 - Basanta for haircut on 2025-02-24 14:30

# class Transaction(models.Model):
#     booking=models.ForeignKey(Booking, on_delete=models.CASCADE)
#     amount=models.IntegerField(null=False,blank=False)
#     status=models.CharField(max_length=50,  null=False, blank=False)

#     def __str__(self):
#         return f"Transcation - {self.id} - {self.amount} - {self.status}"

class LoyaltyProgram(models.Model):
     
    service=models.ForeignKey(Services, on_delete=models.CASCADE)
    frequency=models.IntegerField(null=False, blank=False)
    free_fequency=models.IntegerField(null=False, blank=False)    
    def __str__(self):
        return f"loyalty program for   - frequency : {self.frequency} - free_frequency : {self.free_fequency}"
 

class LoyaltyRecord(models.Model):  # Class names should be PascalCase
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  
    loyalty = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)  
    free_count = models.IntegerField(default=0)
    service_taken = models.IntegerField(default=0)
    status = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return f"LoyaltyRecord: {self.customer.name} - {self.loyalty} | Status: {self.status}"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"   
