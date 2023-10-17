from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):

    GENDER=(
        ('Male','Male'),
        ('Female','Female'),
    )

    user=models.OneToOneField(User, null=True,on_delete=models.CASCADE)
    firstname=models.CharField(max_length=30)
    lastname=models.CharField(max_length=30)
    email=models.EmailField(max_length=254)
    contact_no=models.CharField(max_length=12)
    gender=models.CharField(max_length=10,choices=GENDER)
    city=models.CharField(max_length=30,null=True)
    state=models.CharField(max_length=30,null=True)
    country=models.CharField(max_length=30,null=True)
    profile_pic=models.ImageField(null=True, blank=True)
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.firstname

class Tag(models.Model):
    name=models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    
    FUEL_TYPE=(
        ('Petrol','Petrol'),
        ('Diesel','Diesel'),
        ('Electirc','Electirc'),
        ('Hybrid','Hybrid'),
    )

    STATUS=(
        ('Available','Available'),
        ('Not_Available','Not_Available'),
    )

    owner=models.ForeignKey(Customer,on_delete=models.CASCADE)
    company=models.CharField(max_length=30)
    model=models.CharField(max_length=30)
    fuel_type=models.CharField(max_length=10,choices=FUEL_TYPE)
    seats=models.SmallIntegerField()
    about=models.CharField(max_length=256,null=True)
    price=models.IntegerField()
    tags=models.ManyToManyField(Tag)
    city=models.CharField(max_length=30)
    state=models.CharField(max_length=30)
    image=models.ImageField()
    status=models.CharField(max_length=30,choices=STATUS,default='Available')
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model

class Request_rent(models.Model):

    STATUS=(
        ('Accepted','Accepted'),
        ('Pending','Pending'),
        ('Rejected','Rejected'),
    )


    seeker=models.ForeignKey(Customer,on_delete=models.CASCADE)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()
    number_of_days=models.IntegerField(null=True)
    total= models.IntegerField(null=True)
    status=models.CharField(max_length=30,choices=STATUS,default='Pending')



