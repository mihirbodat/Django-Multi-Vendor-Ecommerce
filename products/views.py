from django.shortcuts import render , redirect
from django.contrib import messages
from .models import *
from users.models import *

def seller_check(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')

    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    
    if not request.user.sellerprofile.is_approved:
        messages.error(request , 'Admin approval pending!')
        return redirect('seller_dashboard')
    return None


def seller_products(request):
    check = seller_check(request)
    if check:
        return check

    products = Product.objects.filter(seller = request.user.sellerprofile)
    return render(request , 'seller_products.html' , {'products':products})


def add_product(request):
    check = seller_check(request)
    if check:
        return check

    if request.method == "POST":
        product_name = request.POST['name']
        product_description = request.POST['description']
        product_price = request.POST['price']
        product_stock = request.POST['stock']
        product_image = request.FILES.get('image',None)

        Product.objects.create(seller = request.user.sellerprofile ,product_name=product_name , 
                                product_description=product_description ,
                                product_price=product_price ,product_stock=product_stock , 
                                category=Category.objects.get(id=request.POST['category']) ,
                                product_image=product_image)
        return redirect('seller_products')
    
    categories = Category.objects.all()

    return render(request , 'add_product.html',{'categories' : categories})


def edit_product(request , id):
    check = seller_check(request)
    if check:
        return check
    
    product = Product.objects.get(id=id)

    if product.seller != request.user.sellerprofile:
        messages.error(request , 'This is not your product.')
        return redirect('seller_products')

    categories = Category.objects.all()
    return render(request , 'edit_product.html' , {'product':product , 'categories' : categories})


def update_product(request , id):
    check = seller_check(request)
    if check:
        return check

    product = Product.objects.get(id=id)

    product.product_name = request.POST['name']
    product.product_description = request.POST['description']
    product.product_price = request.POST['price']
    product.product_stock = request.POST['stock']
    product.category = Category.objects.get(id=request.POST['category'])

    if request.FILES.get('image'):
        product.product_image = request.FILES.get('image')

    product.save()
    return redirect('seller_products')


def seller_search_product(request):
    check = seller_check(request)
    if check:
        return check

    search = request.GET.get('product_name' , '')
    if search:
        products = Product.objects.filter(product_name__icontains=search)
    else:
        products = Product.objects.filter(seller = request.user.sellerprofile)
    return render(request , 'seller_products.html' , {'products':products})


def delete_product(request , id):
    check = seller_check(request)
    if check:
        return check

    product = Product.objects.get(id=id)

    if product.seller != request.user.sellerprofile:
        messages.error(request , 'This is not your product.')
        return redirect('seller_products')

    product.delete()
    return redirect('seller_products')


def product_detail(request , id):
    product = Product.objects.get(id=id)

    reviews = Review.objects.filter(product=product , is_approved=True)
    images = ReviewImage.objects.filter(review__in=reviews)

    total_reviews = reviews.count()

    if total_reviews > 0:
        avg_rating = sum(review.rating for review in reviews) / total_reviews
        avg_rating = round(avg_rating , 1)
    else:
        avg_rating = 0

    if request.user.is_authenticated:
        product.created = Wishlist.objects.filter(user=request.user , product=product).exists()

    return render(request , 'product_detail.html' , {'product':product,
                            'reviews':reviews , 'images':images,
                            'total_reviews':total_reviews , 'avg_rating':avg_rating})
    