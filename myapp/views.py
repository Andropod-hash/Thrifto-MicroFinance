
import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, LoginForm, KYCForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import User, KYC, Device
from django.contrib.auth import logout as auth_logout 

@csrf_exempt
def Registerview(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()  
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created successfully.")
            
            return redirect("login")
        else:
            messages.error(request, "There was an error with your registration. Please check your inputs.")

    else:
        form = UserRegisterForm()

    context = {
        "form": form
    }
    return render(request, "sign-up.html", context)

@csrf_exempt
def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def send_2fa_code(user):
    """Send a 2FA code to the user's email."""
    user.two_fa_code = f"{random.randint(100000, 999999)}"  
    user.two_fa_code_expires = timezone.now() + timedelta(minutes=5)  
    user.two_fa_verified = False  
    user.save()

    # Send email with the 2FA code
    send_mail(
        'Your 2FA Code',
        f'Your two-factor authentication code is {user.two_fa_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@csrf_exempt
def login_view(request):
    """Handle user login and 2FA for unrecognized devices."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
               
                request_ip = get_client_ip(request)

                device, created = Device.objects.get_or_create(
                    user=user,
                    device_identifier=request_ip,
                )

                if created or not user.two_fa_verified:
                    send_2fa_code(user)
                    return redirect('two_fa_input', user_id=user.id)

                login(request, user)

                try:
                    user_kyc = KYC.objects.get(user=user)
                    if user_kyc.kyc_confirmed is True:
                        return redirect('dashboard') 
                except KYC.DoesNotExist:
                    return redirect('kyc_register')  

                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = LoginForm()

    return render(request, 'sign-in.html', {'form': form})


@csrf_exempt
def two_fa_input_view(request, user_id):
    """Handle 2FA code input for login."""
    if request.method == 'POST':
        two_fa_code = request.POST.get('two_fa_code')
        
        # Retrieve the user
        user = get_object_or_404(User, id=user_id)

        # Validate the 2FA code
        if user.two_fa_code == two_fa_code and timezone.now() < user.two_fa_code_expires:
            user.two_fa_verified = True  
            user.two_fa_code = ''  
            user.save()
            login(request, user)
            try:
                user_kyc = KYC.objects.get(user=user)
                if user_kyc.kyc_confirmed:
                    return redirect('dashboard')  
                else:
                    return redirect('kyc_register')  
            except KYC.DoesNotExist:
                return redirect('kyc_register')  

        else:
            messages.error(request, 'Invalid or expired 2FA code. Please try again.')

    return render(request, 'two_fa_input.html', {'user_id': user_id})


@csrf_exempt
def logout_view(request):
    """Logs out the user and redirects to the login page."""
    logout(request)  
    messages.success(request, "You have been logged out successfully.") 
    return redirect('login')  

@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def kyc_registration(request):
    user = request.user
    kyc_instance, created = KYC.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = KYCForm(request.POST, instance=kyc_instance)  
        if form.is_valid():
            kyc_instance = form.save(commit=False)
        
            if form.cleaned_data['terms_agreed']:
                kyc_instance.kyc_confirmed = True
            else:
                kyc_instance.kyc_confirmed = False
            
            kyc_instance.save()  
            
            return redirect('dashboard')  
        else:
            kyc_instance.kyc_confirmed = False
            kyc_instance.save()

            print(form.errors)  
            return JsonResponse(form.errors, status=400) 

    # Render the form if GET request
    form = KYCForm(instance=kyc_instance)
    return render(request, 'kyc_register.html', {'form': form})

def logout_view(request):
    """Logs out the user and redirects to the login page."""
    logout(request)  
    messages.success(request, "You have been logged out successfully.")  
    return redirect('login')  

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# @csrf_exempt
# @login_required
# def create_group_view(request):
#     if request.method == 'POST':
#         form = CreateGroupForm(request.POST, request=request)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')  
#     else:
#         form = CreateGroupForm(request=request)

#     return render(request, 'create_group.html', {'form': form})
