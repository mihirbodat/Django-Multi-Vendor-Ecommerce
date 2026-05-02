from django.shortcuts import render , redirect
from django.contrib import messages
from .models import *

def add_product(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')

    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    
    if not request.user.sellerprofile.is_approved:
        messages.error(request , 'Admin approval pending!')
        return redirect('seller_dashboard')
    
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
        return redirect('product_list')
    
    categories = Category.objects.all()

    return render(request , 'add_product.html',{'categories' : categories})

def seller_product_list(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')
    
    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    
    if not request.user.sellerprofile.is_approved:
        messages.error(request , 'Admin approval pending!')
        return redirect('seller_dashboard')

    products = Product.objects.filter(seller = request.user.sellerprofile)
    return render(request , 'seller_products.html' , {'products':products})

def edit_product(request , id):
    product = Product.objects.get(id=id)
    categories = Category.objects.all()
    return render(request , 'edit_product' , {'product':product , 'categories' : categories})

def update_product(request , id):
    product = Product.objects.get(id=id)

    product.product_name = request.POST['name']
    product.product_description = request.POST['description']
    product.product_price = request.POST['price']
    product.product_stock = request.POST['stock']
    product.category = Category.objects.get(id=request.POST['category'])

    if request.FILES.get('image'):
        product.product_image = request.FILES.get('image')

    product.save()
    return redirect('seller_product_list')

def search_product(request):
    name = request.GET.get('product_name' , '')
    if name:
        products = Product.objects.filter(product_name__icontains=name)
    else:
        products = Product.objects.filter(seller = request.user.sellerprofile)
    return render(request , 'seller_products.html' , {'products':products})

def delete_product(request , id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('seller_product_list')

def buyer_product_list(request):
    products = Product.objects.all()
    return render(request , 'buyer_products.html' , {'products':products})
 
        