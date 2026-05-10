from django.shortcuts import render , redirect
from .models import *
from products.models import *
from orders.models import * 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout

# Create your views here.

def home(request):
    return render(request , 'home.html')

def registeruser(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username = username).exists():
            messages.error(request , 'Username already taken!')
            return render(request , 'registeruser.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request , 'Email already registered!')
            return render(request , 'registeruser.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        if role == 'seller':
            shop_name = request.POST['shop_name']
            SellerProfile.objects.create(seller_user=user ,shop_name=shop_name ,is_approved=False)
        messages.success(request,'User Registered successfully')
        return redirect('loginuser')
    return render(request , 'registeruser.html')


def loginuser(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request , username=username , password=password)

        if user is not None:
            if user.is_staff:
                messages.error(request , 'Please login on admin panel: /admin')
                return redirect('loginuser')

            login(request , user)  # create session_key

            if hasattr(user , 'sellerprofile'):          #check relations
                return redirect('seller_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, '⚠️ Invalid username or password.')
            return redirect('loginuser')
    return render(request , 'login.html')

def logoutuser(request):
    logout(request)
    return redirect('loginuser')

def seller_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')
    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    
    seller = request.user.sellerprofile

    total_products = Product.objects.filter(seller=seller).count()
    total_orders = OrderItem.objects.filter(seller=seller).count()
    revenue = sum(item.price*item.quantity for item in OrderItem.objects.filter(seller=seller))
    recent_orders = OrderItem.objects.filter(seller=seller).order_by('-id')[:5]

    for item in recent_orders:
        item.earnings = item.price * item.quantity

    return render(request , 'seller_dashboard.html',
                   {'total_products':total_products,
                    'total_orders':total_orders,
                    'revenue':revenue,
                    'recent_orders':recent_orders})