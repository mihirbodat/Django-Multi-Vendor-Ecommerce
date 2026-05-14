from django.shortcuts import render , redirect
from .models import *
from django.contrib import messages

def buyer_check(request):
    if not request.user.is_authenticated:
        return redirect('loginuser')
    
    if hasattr(request.user , 'sellerprofile'):
        return redirect('seller_dashboard')
    
    return None

def seller_check(request):
    if not request.user.is_authenticated:
        return redirect('loginuser') 
    if not hasattr(request.user , 'sellerprofile'):
        return redirect('loginuser')
    if not request.user.sellerprofile.is_approved:
        messages.error(request , 'Admin approval pending!')
        return redirect('seller_dashboard')
    return None

def add_to_cart(request , id):
    check = buyer_check(request)
    if check:
        return check
    
    product = Product.objects.get(id=id)
    
    cart , created = Cart.objects.get_or_create(user=request.user)

    cart_item , created = CartItem.objects.get_or_create( cart = cart,product = product)

    if not created:
        cart_item.quantity +=1
        cart_item.save()

    next = request.GET.get('next')       # cart -> is default value.

    if next == 'buy_now':
        return redirect('buy_now' , id=cart_item.id)
    
    return redirect('cart')
    

def cart(request):
    check = buyer_check(request)
    if check:
        return check

    cart , created= Cart.objects.get_or_create(user = request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        item.subtotal = item.product.product_price*item.quantity

    total = sum(item.subtotal for item in cart_items)

    return render(request , 'cart.html' , {'cart':cart , 'cart_items': cart_items , 'total':total} )


def update_quantity(request , id , action):
    check = buyer_check(request)
    if check:
        return check

    cart_item = CartItem.objects.get(id=id)

    if action == 'increase':
        cart_item.quantity +=1
        cart_item.save()

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()                  # if quantity 1 it becomes 0 ,it means delete cart_item.
    
    next = request.GET.get('next')   
    return redirect(next)


def remove_item(request , id):
    check = buyer_check(request)
    if check:
        return check

    cart_item = CartItem.objects.get(id=id)

    cart_item.delete()
    next = request.GET.get('next')
    return redirect(next)

def checkout(request):
    check = buyer_check(request)
    if check:
        return check
    
    try:
        cart = Cart.objects.get(user = request.user)
    except Cart.DoesNotExist:                             # If the user does not have a cart it, they cannot access the checkout page.
        return redirect('cart')
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('cart')

    for item in cart_items:
        item.subtotal = item.product.product_price*item.quantity

    total = sum(item.subtotal for item in cart_items)

    return render(request , 'checkout.html' , {'cart_items':cart_items , 'total':total})

def buy_now(request , id):
    check = buyer_check(request)
    if check:
        return check
    
    try:
        cart_item = CartItem.objects.get(id=id)
    except CartItem.DoesNotExist:
        return redirect('cart')

    cart_item.subtotal = cart_item.product.product_price*cart_item.quantity

    return render(request , 'checkout.html' , {'cart_items':[cart_item] , 'total':cart_item.subtotal})


def place_order(request):
    check= buyer_check(request)
    if check:
        return check
    
    item_ids = request.POST.getlist('item_ids')
    cart_items = CartItem.objects.filter(id__in=item_ids)
    
    order = Order.objects.create(user=request.user,
                                 total_price=request.POST['total'])
    
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            seller=item.product.seller,
            quantity=item.quantity,
            price=item.product.product_price
            )
        
    cart_items.delete()
    return redirect('order_confirmation' , order.id)

def order_confirmation(request , id):
    check= buyer_check(request)
    if check:
        return check
    
    try:
        order = Order.objects.get(id=id , user = request.user)
    except Order.DoesNotExist:
        return redirect('buyer_products')

    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_confirmation.html' , {'order':order , 
                                                        'order_items':order_items})

def my_orders(request):
    check = buyer_check(request)
    if check:
        return check
    
    orders = Order.objects.filter(user = request.user)
    
    for order in orders:
        order.items = OrderItem.objects.filter(order=order)

    return render(request , 'my_orders.html' , {'orders':orders})


def seller_orders(request):
    check = seller_check(request)
    if check:
        return check

    order_items = OrderItem.objects.filter(seller=request.user.sellerprofile)

    for item in order_items:
        item.subtotal = item.price*item.quantity

    return render(request , 'seller_orders.html' , {'order_items':order_items})

def update_status(request , id):
    check = seller_check(request)
    if check:
        return check
    
    order_item = OrderItem.objects.get(id=id)

    order_item.status = request.POST['status']
    order_item.save()
    return redirect('seller_orders')