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
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from datetime import date
from django.contrib.auth.models import User,auth
import datetime
from dateutil import parser
from django.contrib.auth import update_session_auth_hash



# Create your views here.

@unauthenticated_user
def register(request):

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        to_email = request.POST.get('email')

        if User.objects.filter(email=to_email).exists():
                 messages.info(request,'An user with this email already exists!')
                 return  render(request, 'RentingApp/register.html',{'form': form})
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('RentingApp/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
           
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            
        
            # user= form.save()
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
            # return redirect('login')

            return HttpResponse('Please confirm your email address to complete the registration')


    return render(request, 'RentingApp/register.html', {'form': form})

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
    customer=request.user.customer
    vehicles=[]
    for i in vehicle:
        if i.owner!=customer:
            vehicles.append(i)
    
    context={'vehicle':vehicles}
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
    # form=AddvehicleForm()
    if request.method=='POST':
        # print(form['owner'])
        customer_object = request.user.customer
        company=request.POST.get('company')
        model=request.POST.get('model')
        fuel_type=request.POST.get('fuel')
        seats=request.POST.get('capacity')
        about=request.POST.get('addinfo')
        price=request.POST.get('price')
        # tag=form.cleaned_data.get('tags')
        city=request.POST.get('city')
        state=request.POST.get('state')
        image=request.FILES.get('img')
        date_created=datetime.datetime.now()
        status='Available'
        Vehicle.objects.create(owner = customer_object,company=company,model=model,fuel_type=fuel_type,
                        seats=seats,about=about,price=price,city=city,state=state,image=image,
                        date_created=date_created,status=status)
        return redirect('home')

    # context={'form':form}
    return render(request,'RentingApp/addvehicle.html')

@login_required(login_url='login')
def productview(request,pk):
    # form=RequestForm()
    vehicle=Vehicle.objects.get(id=pk)
    context={'vehicle':vehicle,'owner':vehicle.owner,'user':request.user.customer}

    if request.method=='POST':
        # form=RequestForm(request.POST)
        start_date=request.POST.get('start_date')
        # start_date_obj=
        end_date=request.POST.get('end_date')
        
        temp1 = parser.parse(start_date)
        temp2 = parser.parse(end_date)
        start_date_obj = temp1.date()
        end_date_obj = temp2.date()
        customer_object=request.user.customer
        # start_date=form.cleaned_data.get('start_date')
        # end_date=form.cleaned_data.get('end_date')
        number_of_days=abs(start_date_obj-end_date_obj).days
        if (start_date_obj > end_date_obj or start_date_obj < date.today() or end_date_obj < date.today()):
            messages.info(request,'Invalid Duration')
            return render(request,'RentingApp/productview.html',context)
        
        requests=Request_rent.objects.all()

        for i in requests:
            if i.status=="Accepted" and i.vehicle==vehicle:
                if ((start_date_obj <= i.end_date) and (start_date_obj >= i.start_date)) or ((end_date_obj <= i.end_date) and (end_date_obj >= i.start_date)) or ((end_date_obj >= i.end_date) and (start_date_obj <= i.start_date)):
                    messages.info(request,'Sorry, This Vehicle is not available for this time period')
                    return render(request,'RentingApp/productview.html',context)
        total=(vehicle.price)*(number_of_days+1)
        status='Pending'
        Request_rent.objects.create(seeker = customer_object,vehicle=vehicle,start_date=start_date_obj,
                                    end_date=end_date_obj,number_of_days=number_of_days,total=total,
                                    status=status)
        return redirect('home')
            
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
    requests1=requests.filter(seeker=customer)
    requests2=requests.filter(owner=customer)
    context={'requests1':requests1,'requests2':requests2}
    return render(request,'RentingApp/requestpage.html',context)

@login_required(login_url='login')
def reject_request(request , id):
    requests_ac = Request_rent.objects.get(id=id)
    requests_ac.status='Rejected'
    subject = 'Your Request Has Been Rejected'
    message = 'Your request to rent the vehicle has been Rejected!'
    from_email = 'djk251508194@gmail.com'  # Replace with your email
    recipient = requests_ac.seeker.email
    context = {
        'customer_name': requests_ac.seeker.firstname,
        'request_id': requests_ac.id,
        'vehicle_name': requests_ac.vehicle.model,
        'start_date': requests_ac.start_date,
        'end_date': requests_ac.end_date,
        'owner_name': requests_ac.vehicle.owner.firstname,
        'owner_contact': requests_ac.vehicle.owner.email,
    }
    html_message = render_to_string('RentingApp/reject_email.html', context)
    send_mail(subject, message, from_email, [recipient], html_message=html_message)
    requests_ac.save()
    return redirect(requestpage)

@login_required(login_url='login')
def delete_request(request , id):
    requests = Request_rent.objects.get(id=id)
    requests.delete()
    return redirect(requestpage)

@login_required(login_url='login')
def accept_request(request , id):
    requests = Request_rent.objects.get(id=id)
    requests.status='Accepted'
    requests = Request_rent.objects.get(id=id)
    requests.status='Accepted'
    subject = 'Your Request Has Been Accepted'
    message = 'Your request to rent the vehicle has been accepted!'
    from_email = 'djk251508194@gmail.com'  
    recipient = requests.seeker.email
    context = {
    'customer_name': requests.seeker.firstname,
    'request_id': requests.id,
    'vehicle_model': requests.vehicle.model,
    'start_date': requests.start_date,
    'end_date': requests.end_date,
    'owner_name': requests.vehicle.owner.firstname,
    'owner_email': requests.vehicle.owner.email,
    }
    html_message = render_to_string('RentingApp/accept_email.html', context)
    send_mail(subject, message, from_email, [recipient], html_message=html_message)
    requests.save()
    vehicle_id=requests.vehicle

    for i in Request_rent.objects.filter(vehicle=vehicle_id , status='Pending') :
        if ((i.start_date <= requests.end_date) and (i.start_date >= requests.start_date)) or ((i.end_date <= requests.end_date) and (i.end_date >= requests.start_date)) or ((requests.start_date >= i.start_date) and (i.end_date >= requests.end_date)):
            i.status = 'Rejected'
            subject = 'Your Request Has Been Rejected'
            message = 'Your request to rent the vehicle has been Rejected!'
            from_email = 'djk251508194@gmail.com'  # Replace with your email
            recipient = i.seeker.email
            context = {
                'customer_name': i.seeker.firstname,
                'request_id': i.id,
                'vehicle_name': i.vehicle.model,
                'start_date': i.start_date,
                'end_date': i.end_date,
                'owner_name': i.vehicle.owner.firstname,
                'owner_contact': i.vehicle.owner.email,
            }
            html_message = render_to_string('RentingApp/reject_email.html', context)
            send_mail(subject, message, from_email, [recipient], html_message=html_message)
            i.save()
    return redirect(requestpage)

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

@login_required(login_url='login')
def search_vehicle(request):
    
    if request.method=='POST':
        searched=request.POST['searched']
        # searched = request.POST.get('searched', False)
        vehicle=Vehicle.objects.filter((Q(model__contains=searched) | Q(company__contains=searched) | Q(city__contains=searched)))
        vehicle=vehicle.filter(status='Available')
        customer=request.user.customer
        vehicles=[]
        for i in vehicle:
            if i.owner!=customer:
                vehicles.append(i)
    
        context={'searched':searched,'vehicles':vehicles}
        return render(request,'RentingApp/search.html',context)
    else:
        context={}
        return render(request,'RentingApp/search.html',context)

@login_required(login_url='login')
def search_vehicle_filter(request):
    
    if request.method=='POST':
        searched=request.POST.get('searched_v')
        petrol=request.POST.get('petrol')
        diesel=request.POST.get('diesel')
        electric=request.POST.get('Electric')
        hybrid=request.POST.get('Hybrid')
        num1=request.POST.get('num1')
        num2=request.POST.get('num2')
        seats=request.POST.get('seat')
        print(petrol,' ',diesel,' ',electric,' ',hybrid)
        print(type(num1),' ',num2)
        print(seats)
        vehicle=Vehicle.objects.filter(Q(model__contains=searched) | Q(company__contains=searched) | Q(city__contains=searched))
        vehicle=vehicle.filter(status='Available')
        

        vehicles1=[]
        if (num1!='') & (num2!=''):
            vehicle1=vehicle.filter(price__gte=int(num1),price__lte=int(num2))
        elif num1!='':
            vehicle1=vehicle.filter(price__gte=int(num1))
        elif num2!='':
            vehicle1=vehicle.filter(price__lte=int(num2))
        else:
            vehicle1=vehicle

        for i in vehicle1:
            vehicles1.append(i)

        flag=0
        vehicle2=[]
        if (petrol is None) & (diesel is None) & (electric is None) & (hybrid is None):
            flag=1
            for i in vehicle:
                vehicle2.append(i)
        else:
            for i in vehicle:

                if (petrol is not None):
                    if i.fuel_type=='Petrol':
                        vehicle2.append(i)

                if diesel is not None:
                    if i.fuel_type=='Diesel':
                        vehicle2.append(i)

                if electric is not None:
                    if i.fuel_type=='Electric':
                        vehicle2.append(i)
            
                if hybrid is not None:
                    if i.fuel_type=='Hybrid':
                        vehicle2.append(i)
        
        vehicle3=[]

        if (seats!=''):
            for i in vehicle:
                if i.seats==int(seats):
                    vehicle3.append(i)
        else:
            for i in vehicle:
                vehicle3.append(i)   

        finvehicle=[]
        for i in vehicles1:
            for j in vehicle2:
                for k in vehicle3:
                    if ((i==j) & (j==k)):
                        finvehicle.append(i)

        # print(vehicles)
        customer=request.user.customer
        vehicles=[]
        for i in finvehicle:
            if i.owner!=customer:
                vehicles.append(i)
        context={'searched':searched,'vehicles':vehicles}
        return render(request,'RentingApp/search.html',context)
    else:
        context={}
        return render(request,'RentingApp/search.html',context)


@login_required(login_url='login')
def Profile(request):
    #customer = Customer.objects.get(customer_object=customer_object)
    customer=request.user.customer
    return render(request,'RentingApp/Profile.html',{'customer':customer})

@login_required(login_url='login')
def myvehicle(request):
    customer = request.user.customer
    vehicle=Vehicle.objects.filter(owner=customer)
    context={'vehicle':vehicle}
    return render(request,'RentingApp/myvehicle.html',context)

@login_required(login_url='login')
def myvehicleview(request , pk):
    vehicle=Vehicle.objects.get(id=pk)      
    context={'vehicle':vehicle}
    return render(request,'RentingApp/myvehicleview.html',context)

@login_required(login_url='login')
def profilepath(request,pk):
    customer = Customer.objects.get(id=pk)

    
    context={'customer':customer}
    return render(request, 'RentingApp/profilepath.html', context)

@login_required(login_url='login')
def edit_profile(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('Profile')

    context = {'form': form}
    return render(request, 'RentingApp/edit_profile.html', context)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'RentingApp/password_reset.html'
    email_template_name = 'RentingApp/password_reset_email.html'
   # subject_template_name = 'RentingApp/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
       
        #return redirect('home')
        return render(request,'RentingApp/thanks.html')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required(login_url='login')
def edit_vehicle(request , pk):
    # vehicle = Vehicle.objects.filter(id = pk)
    # form = AddvehicleForm(instance=vehicle)
    vehicle2=Vehicle.objects.get(id=pk)

    if request.method == 'POST':
        # form = AddvehicleForm(request.POST, request.FILES, instance=vehicle)
        # customer_object = request.user.customer
        vehicle2.company=request.POST.get('company')
        vehicle2.model=request.POST.get('model')
        vehicle2.fuel_type=request.POST.get('fuel')
        vehicle2.seats=request.POST.get('capacity')
        vehicle2.about=request.POST.get('addinfo')
        vehicle2.price=request.POST.get('price')
        # tag=form.cleaned_data.get('tags')
        vehicle2.city=request.POST.get('city')
        vehicle2.state=request.POST.get('state')
        image=request.FILES.get('img')
        # date_created=datetime.datetime.now()
        # status='Available'
        # print(image)
        if image is not None:
            vehicle2.image=image
        
        vehicle2.save()
            
        
        messages.success(request, 'Vehicle updated successfully!')
        vehicle2=Vehicle.objects.get(id=pk)
        context={'vehicle':vehicle2}
        return render(request,'RentingApp/myvehicleview.html',context)

    context = {'vehicle': vehicle2}
    return render(request, 'RentingApp/edit_vehicle.html', context)

@login_required(login_url='login')
def delete_vehicle(request,pk):
    vehicle=Vehicle.objects.get(id=pk)
    vehicle.delete()
    return redirect('myvehicle')
