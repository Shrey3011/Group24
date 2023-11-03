from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth  import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import *
from .forms import *
from django.contrib import messages
from .decorators import *

# Create your views here.

@unauthenticated_user
def register(request):

    form=CreateUserForm()

    if request.method=='POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user= form.save()
            username= form.cleaned_data.get('username')
            firstname=form.cleaned_data.get('firstname')
            lastname=form.cleaned_data.get('lastname')

            group=Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                email=user.email,
                firstname=firstname,
                lastname=lastname
            )
            messages.success(request,'Account was created for ' + username)
            return redirect('login')

    context={'form':form}
    return render(request,'RentingApp/register.html',context)

@unauthenticated_user
def login_handler(request):

    context={}
    if request.method=='POST':
        username =request.POST.get('username')
        password =request.POST.get('password')

        user=authenticate(request,username=username,password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
            return render(request,'RentingApp/login.html',context)


    return render(request,'RentingApp/login.html',context)

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    vehicle=Vehicle.objects.all()
    vehicle=vehicle.filter(status='Available')
    context={'vehicle':vehicle}
    return render(request,'RentingApp/home.html',context)

@login_required(login_url='login')
def customer(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)

    if request.method=='POST':
        form=CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return render(request,'RentingApp/customer.html',context)

@login_required(login_url='login')
def addvehicle(request):
    # customer=request.user.customer
    form=AddvehicleForm()
    if request.method=='POST':
        form=AddvehicleForm(request.POST,request.FILES)
        if form.is_valid():
            # print(form['owner'])
            customer_object = request.user.customer
            company=form.cleaned_data.get('company')
            model=form.cleaned_data.get('model')
            fuel_type=form.cleaned_data.get('fuel_type')
            seats=form.cleaned_data.get('seats')
            about=form.cleaned_data.get('about')
            price=form.cleaned_data.get('price')
            # tag=form.cleaned_data.get('tags')
            city=form.cleaned_data.get('city')
            state=form.cleaned_data.get('state')
            image=form.cleaned_data.get('image')
            date_created=form.cleaned_data.get('date_created')
            status='Available'
            Vehicle.objects.create(owner = customer_object,company=company,model=model,fuel_type=fuel_type,
                           seats=seats,about=about,price=price,city=city,state=state,image=image,
                           date_created=date_created,status=status)
            return redirect('home')

    context={'form':form}
    return render(request,'RentingApp/addvehicle.html',context)

@login_required(login_url='login')
def productview(request,pk):
    form=RequestForm()
    vehicle=Vehicle.objects.get(id=pk)

    if request.method=='POST':
        form=RequestForm(request.POST)
        if form.is_valid():
            customer_object=request.user.customer
            start_date=form.cleaned_data.get('start_date')
            end_date=form.cleaned_data.get('end_date')
            number_of_days=abs(start_date-end_date).days
            total=(vehicle.price)*number_of_days
            status='Pending'
            Request_rent.objects.create(seeker = customer_object,vehicle=vehicle,start_date=start_date,
                                        end_date=end_date,number_of_days=number_of_days,total=total,
                                        status=status)
            return redirect('home')
            
    context={'vehicle':vehicle,'form':form}
    return render(request,'RentingApp/productview.html',context)

@login_required(login_url='login')
def history(request):
    customer=request.user.customer
    requests=Request_rent.objects.all()
    requests1=requests.filter(status='Accepted',seeker=customer)
    requests2=None
    context={'requests1':requests1,'requests2':requests2}
    return render(request,'RentingApp/history.html',context)

@login_required(login_url='login')
def requestpage(request):
    customer=request.user.customer
    requests=Request_rent.objects.all()
    requests=requests.filter(seeker=customer)
    context={'requests':requests}
    return render(request,'RentingApp/requestpage.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
           
            update_session_auth_hash(request, user)
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'RentingApp/change_password.html', {'form': form})

