import re
from django.contrib.auth import logout
from django.shortcuts import render,redirect,redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
import requests
from .forms import Customerform
from django.contrib.auth.hashers import make_password
from .models import ContactMessage, Customer, LoyaltyProgram, LoyaltyRecord, Services,Booking
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Services, Booking
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import date, datetime, time, timedelta


 

@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    return render(request, 'base.html')   

@login_required(login_url='login')
def about(request):
    return render(request,'about.html')

 
 
 
 

def signupPage(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'auth/login1.html')
        
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return render(request, 'auth/login1.html')

        if not re.search(r'[A-Za-z]', password1) or not re.search(r'\d', password1):
            messages.error(request, "Password must contain at least one letter and one number")
            return render(request, 'auth/login1.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'auth/login1.html')

        # Create user
        user = User.objects.create_user(
            username=email,
            first_name=name,
            email=email,
            password=password1
        )
        user.save()

         
        Customer.objects.create(
            user=user,
            name=name,
            email=email,
            password=password1   
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'auth/login1.html')


def loginP(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password1')

        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            messages.error(request, "Account not found")
            return render(request, 'auth/login2.html')

        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request, user)
            return redirect('userauth:home')
        else:
            messages.error(request, "Incorrect password")
            return render(request, 'auth/login2.html')

    return render(request, 'auth/login2.html')

@login_required(login_url='login')
def custom_logout(request):
    logout(request)
    return redirect('login')    

@login_required(login_url='login')
def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]

        # Save to database
        ContactMessage.objects.create(name=name, email=email, message=message)

        # Optional: send email
        send_mail(
            f"New Contact Message from {name}",
            message,
            email,
            ["your-email@gmail.com"],
            fail_silently=False,
        )
        return redirect("userauth:contact")

    return render(request, "contact.html")


def customer_register(request):
    if request.method == 'POST':
        form = Customerform(request.POST)
        if form.is_valid():
            # Hash the password before saving
            password = form.cleaned_data.get('password')
            hashed_password = make_password(password)
            form.cleaned_data['password'] = hashed_password   

            # Save the form to the database
            form.save()

            return redirect('userauth:home')   
    else:
        form = Customerform()

    return render(request, 'auth/register.html', {'form': form})
 
class categoryView(View):
    def get(self, request, category):
        services = Services.objects.filter(category=category)
        categories = Services.objects.values_list('category', flat=True).distinct()
        all_services = list(Services.objects.values('id', 'name', 'category'))

        # Create available time slots from 9AM to 10PM for today
        available_time_slots = []
        date_obj = datetime.today().date()
        start_time = time(9, 0)
        end_time = time(22, 0)
        current_time = datetime.combine(date_obj, start_time)

        while current_time.time() <= end_time:
            
            count = Booking.objects.filter(date=date_obj, time=current_time.time()).count()
            if count < 3:
                raw_time = current_time.strftime("%H:%M")
                display_time = current_time.strftime("%I:%M %p").lstrip('0')
                available_time_slots.append((raw_time, display_time))
            current_time += timedelta(hours=1)

        if not available_time_slots:
            messages.warning(request, "All time slots for today are fully booked. Please try another day.")

        initial_data = {
            'name': request.user.get_full_name() if request.user.is_authenticated else '',
            'email': request.user.email if request.user.is_authenticated else '',
        }
        today= datetime.today().date()
        return render(request, 'category.html', {
            'service': services,
            'categories': categories,
            'all_services': all_services,
            'initial_data': initial_data,
            'available_time_slots': available_time_slots,
            'today':today  
        })

    

# Booking
def booking_create(request):
    if request.method == "POST":
        booking_time = request.POST['time']
        booking_date = request.POST['date']

        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
        booking_time_obj = datetime.strptime(booking_time, "%H:%M").time()
    
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
        if booking_date_obj < date.today():
            messages.error(request, "Sorry, Booking date cannot be in the past.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Time cannot be in the past for today's booking
        if booking_date_obj == date.today() and booking_time_obj < datetime.now().time():
            messages.error(request, "Cannot select a past time for today's booking.")
            return redirect(request.META.get('HTTP_REFERER', '/'))


        # Enforce time range
        booking_hour = int(booking_time.split(':')[0])
        if not (9 <= booking_hour <= 22):
            messages.error(request, "Booking time must be between 9 AM and 10 PM.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Prevent overbooking: max 3 bookings per time slot per day
        existing_bookings = Booking.objects.filter(date=booking_date, time=booking_time).count()
        if existing_bookings >= 3:
            messages.error(request, "Selected time slot is full. Please choose another time.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Create booking instance
        booking = Booking(
            name=request.POST['name'],
            email=request.POST['email'],
            phone_number=request.POST['phone_number'],
            date=booking_date,
            time=booking_time,
        )

        customer = None
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
                booking.customer = customer
            except Customer.DoesNotExist:
                pass

        booking.save()

        # Set services (triggers signals)
        service_id = request.POST.get('services')
        additional_service_ids = request.POST.getlist('additional_services[]')

        if service_id:
            booking.services.add(service_id)

        if additional_service_ids:
            booking.additional_services.set(additional_service_ids)

        messages.success(request, "Your Service has successfully Booked")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('/')



@login_required
def customer_dashboard(request):
    try:
        customer = request.user.customer
        bookings = Booking.objects.filter(customer=customer)
        loyalty_record = LoyaltyRecord.objects.filter(customer=customer).first()

        if loyalty_record:
            services_taken = loyalty_record.service_taken
            services_for_reward = getattr(loyalty_record.loyalty, 'services_for_reward', 5)
            rewards = services_taken // services_for_reward
            points = services_taken
        else:
            services_taken = 0
            rewards = 0
            points = 0

    except Customer.DoesNotExist:
        customer = None
        bookings = []
        services_taken = 0
        rewards = 0
        points = 0

    return render(request, 'customer_dashboard.html', {
        'customer': customer,
        'bookings': bookings,
        'loyalty_points': points,
        'rewards': rewards,
    })


@login_required
def booking_page(request):
    available_time_slots = []
    selected_date = request.GET.get('date') 
    date_obj = None

    if selected_date:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        date_obj = datetime.today().date()

    start_time = time(9, 0)
    end_time = time(22, 0)
    current_time = datetime.combine(date_obj, start_time)

    while current_time.time() <= end_time:
        slot_time = current_time.time().strftime("%H:%M")
        count = Booking.objects.filter(date=date_obj, time=current_time.time()).count()
        if count < 3:
            available_time_slots.append(slot_time)
        current_time += timedelta(hours=1)

    # You can also pass initial_data for autofill
    initial_data = {
        'name': request.user.get_full_name(),
        'email': request.user.email,
    }
    today = datetime.today().date()
    return render(request, "booking_page.html", {
        'available_time_slots': available_time_slots,
        'initial_data': initial_data,
        'today':today
    })