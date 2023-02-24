
from . tokens import generate_token
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from authproject import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
# Create your views here.


def home(request):
    return render(request, "authentication/index.html")


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        emailid = request.POST['emailid']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist!")
            return redirect('home')

        if User.objects.filter(email=emailid):
            messages.error(request, "Email already registered!")
            return redirect('home')

        if len(username) > 15:
            messages.error(request, "Username must be under 15 characters")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match")

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric")
            return redirect('home')

        myuser = User.objects.create_user(username, emailid, pass1)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.is_active = False
        myuser.save()

        #Email message###############

        subject = "Welcome to our website -Django Login"

        message = "Annyeong 👋"+myuser.first_name + \
            "\nHappy to see here!! \nThanks for registering at our website.\n\n Thanking You\n Deepti Sharma"

        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email, settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        # msg=EmailMessage(subject,message,from_email,to_list)
        # msg.send()

        #####################################
        current_site = get_current_site(request)
        email_subject = "confirm your email @Django Login"
        message2 = render_to_string('emailconfirm.html', {'name': myuser.first_name, 'domain': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(myuser.pk)), 'token': generate_token.make_token(myuser)
        })

        email=EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently=True
        email.send()

        messages.success(
            request, "Your account has been successfully created !! Confirmation mail has been sent to your email account")
        return redirect('signin')

    return render(request, "authentication/signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, "authentication/index.html", {"firstname": "firstname"})
        else:
            messages.error(request, "Wrong credentials")
            return redirect('home')
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully")
    return redirect('home')
def activate(request,uidb64,token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active =True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'failed.html')