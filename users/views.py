from django.shortcuts import render , redirect
from .models import *
from products.models import *
from orders.models import * 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from  django.core.paginator import Paginator

# Create your views here.

def buyer_check(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')
    
    if hasattr(request.user , 'sellerprofile'):
        return redirect('seller_dashboard')
    
    return None


def home(request):
    products = Product.objects.all()

    for product in products:
        product.total_reviews = Review.objects.filter(product=product , is_approved=True).count()
        if product.total_reviews > 0:
            product.avg_rating = sum(review.rating for review in 
                        Review.objects.filter(product=product,is_approved=True)) / product.total_reviews
            product.avg_rating = round(product.avg_rating , 1)
        else:
            product.avg_rating = 0

        if request.user.is_authenticated :
            product.created = Wishlist.objects.filter(user=request.user ,product=product).exists()

    paginator = Paginator(products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request , 'home.html' , {
                            'page_obj':page_obj , 
                            'categories':categories})

def registeruser(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        role = request.POST['role']

        if User.objects.filter(username = username).exists():
            messages.error(request , 'Username already taken!')
            return render(request , 'registeruser.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request , 'Email already registered!')
            return render(request , 'registeruser.html')
        
        if password != confirm_password :
            messages.error(request , 'Passwords do not match!')
            return render(request , 'registeruser.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        if role == 'seller':
            shop_name = request.POST['shop_name']
            SellerProfile.objects.create(seller_user=user ,shop_name=shop_name ,is_approved=False)
        messages.success(request,'User Registered successfully')
        return redirect('loginuser')
    return render(request , 'registeruser.html')


def loginuser(request):
    if request.user.is_authenticated:
        return redirect('home')
    
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
    return redirect('home')

def seller_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')
    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    
    seller = request.user.sellerprofile

    total_products = Product.objects.filter(seller=seller).count()
    total_orders = OrderItem.objects.filter(seller=seller).count()
    revenue = sum(item.price*item.quantity for item in OrderItem.objects.filter(seller=seller , status='Delivered'))
    recent_orders = OrderItem.objects.filter(seller=seller).order_by('-id')[:5]

    for item in recent_orders:
        item.earnings = item.price * item.quantity

    return render(request , 'seller_dashboard.html',
                   {'total_products':total_products,
                    'total_orders':total_orders,
                    'revenue':revenue,
                    'recent_orders':recent_orders})


def buyer_search_product(request):
    
    search = request.GET.get('product_name', '')
    category_id = request.GET.get('category' , '')
    min_price = request.GET.get('min-price' , '')
    max_price = request.GET.get('max-price' , '')

    if search:
        products = (Product.objects.filter(
                product_name__icontains = search    
            ) | Product.objects.filter(                     # | = merge both results
                category__category_name__icontains = search
            )).distinct()                              # .distinct() = remove duplicates from result
    else:
        products = Product.objects.all()

    if category_id:
        products = products.filter(category__id=category_id)

    if min_price and max_price:
        if int(min_price) > int(max_price):
            messages.error(request , 'Min price cannot be greater than max price!')
            return redirect('home')

    if min_price:
        products = products.filter(product_price__gte=min_price)

    if max_price:
        products = products.filter(product_price__lte=max_price)

    paginator = Paginator(products , 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request , 'home.html' ,
                {'page_obj':page_obj , 'search':search ,
                 'categories':categories , 'category_id':category_id,
                 'min_price':min_price , 'max_price':max_price})

def review(request , ItemId):
    check = buyer_check(request)
    if check:
        return check
    
    try:
        order_item = OrderItem.objects.get(id=ItemId)
    except OrderItem.DoesNotExist:
        messages.error(request , 'Product does not exist!')
        return redirect('my_orders')
    
    if not order_item.status == "Delivered":
        messages.error(request , 'You can only submit a review after the product has been delivered!')
        return redirect('my_orders')
    
    if Review.objects.filter(buyer = request.user , order_item = order_item).exists() :
        messages.error(request , 'You have already reviewed this product!')
        return redirect('my_orders')
    
    if request.method == 'POST':
        rating = request.POST['rating']
        message = request.POST['description']
        images = request.FILES.getlist('image',None)

        review = Review.objects.create(buyer=request.user , product=order_item.product,
                                       order_item=order_item, rating = rating,
                                       message=message , is_approved = False)
        
        if images:
            for image in images:
                ReviewImage.objects.create(review=review , image=image)
        messages.success(request,'Thank you so much. Your review has been saved.')
        return redirect('my_orders')
        
    return render(request , 'review.html' , {'order_item':order_item})

def add_to_wishlist(request , id):
    check = buyer_check(request)
    if check:
        return check
    
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        messages.error(request , 'Product not found!')
        return redirect('home')

    wishlist , created = Wishlist.objects.get_or_create(user=request.user , product=product)
    
    if created:
        messages.success(request , 'Added to your Wishlist')
    else:
        wishlist.delete()
        messages.success(request , 'Removed from your Wishlist')

    next = request.GET.get('next')
    return redirect(next)


def wishlist(request):
    check = buyer_check(request)
    if check:
        return check
    
    wishlists = Wishlist.objects.filter(user = request.user)

    wishlists.total = wishlists.count()

    return render(request , 'wishlist.html' , {'wishlists': wishlists})