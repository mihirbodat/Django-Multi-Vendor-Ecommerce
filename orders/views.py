from django.shortcuts import render , redirect
from .models import *
from django.contrib import messages
from users.models import *
from django.db.models import Case,When,IntegerField

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
    
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        messages.error(request , 'Product does not exist!')
        return redirect('home')

    if product.product_stock <= 0 :
        messages.error(request , 'Currently out of stock!')
        return redirect(request.META.get('HTTP_REFERER' , 'home'))
    
    cart , created = Cart.objects.get_or_create(user=request.user)

    cart_item , created = CartItem.objects.get_or_create( cart = cart,product = product)

    if not created:
        cart_item.quantity +=1
        cart_item.save()

    next = request.GET.get('next')

    if next == 'buy_now':
        return redirect('buy_now' , id=cart_item.id)
    
    messages.success(request , 'Item added to cart!')
    return redirect(request.META.get('HTTP_REFERER' ,'home'))
    

def cart(request):
    check = buyer_check(request)
    if check:
        return check

    cart , created= Cart.objects.get_or_create(user = request.user)
    cart_items = CartItem.objects.filter(cart=cart).order_by('-id')

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
    if next == 'buy_now':
        return redirect('buy_now' , id=id)
    else :
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

    return render(request , 'checkout.html' , {
                            'cart_items':[cart_item] ,
                            'total':cart_item.subtotal ,
                            'buy_now_item_id':id})


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
        return redirect('home')

    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_confirmation.html' , {'order':order , 
                                                        'order_items':order_items})

def my_orders(request):
    check = buyer_check(request)
    if check:
        return check
    
    orders = Order.objects.filter(user = request.user).order_by('-created_at')
    
    for order in orders:
        order.items = OrderItem.objects.filter(order=order)
        for item in order.items :
            item.already_reviewed = Review.objects.filter(
                buyer = request.user , 
                order_item = item
            ).exists()
            item.subtotal = item.price * item.quantity

    return render(request , 'my_orders.html' , {'orders':orders})


def seller_orders(request):
    check = seller_check(request)
    if check:
        return check

    seller = request.user.sellerprofile

    order_items = OrderItem.objects.filter(seller=seller).annotate(
        status_order=Case(
            When(status='Pending' , then=1),
            When(status='Confirmed' , then=2),
            When(status='Shipped' , then=3),
            When(status='Delivered' , then=4),
            When(status='Cancelled' , then=5),
            output_field=IntegerField()
        )
    ).order_by('status_order' , '-id')

    buyer_cancelled = OrderItem.objects.filter(seller=seller ,status = 'Cancelled',
                                            cancelled_by = 'Buyer' ,is_cancel_acknowledged = False)

    for item in order_items:
        item.subtotal = item.price*item.quantity

    return render(request , 'seller_orders.html' ,
                    {'order_items':order_items ,
                     'buyer_cancelled':buyer_cancelled})

def update_status(request , id):
    check = seller_check(request)
    if check:
        return check
    
    order_item = OrderItem.objects.get(id=id)
    old_status = order_item.status
    new_status = request.POST['status']

    product = order_item.product

    if old_status == 'Pending' and new_status == 'Confirmed':

        if product.product_stock < order_item.quantity:
            messages.error(request , f"⚠️ Only {product.product_stock} stock left!")
            messages.error(request , f"The ordered quantity is {order_item.quantity} - it cannot be confirmed!")
            return redirect('seller_orders')

        product.product_stock -= order_item.quantity
        product.save()

    if old_status == 'Pending' and new_status == 'Cancelled':
        order_item.cancelled_by = 'Seller'

    if old_status in ['Confirmed' , 'Shipped'] and new_status == 'Cancelled':
        product.product_stock += order_item.quantity
        order_item.cancelled_by = 'Seller'
        product.save()

    if old_status == 'Confirmed' and new_status == 'Pending':
        product.product_stock += order_item.quantity
        product.save()

    order_item.status = new_status

    order_item.save()
    return redirect('seller_orders') 


def cancel_order(request , id):
    check = buyer_check(request)
    if check:
        return check

    try:
        order_item = OrderItem.objects.get(id=id)
    except OrderItem.DoesNotExist:
        return redirect('my_orders')

    if order_item.order.user != request.user:
        messages.error(request , "This isn't your order!")
        return redirect('my_orders')

    if order_item.status not in ['Pending' , 'Confirmed']:
        messages.error(request , 'Only pending/confirmed orders can be cancelled!')
        return redirect('my_orders')

    if order_item.status == "Confirmed":
        order_item.product.product_stock += order_item.quantity
        order_item.product.save()

    order_item.status = 'Cancelled'
    order_item.cancelled_by = 'Buyer'
    order_item.save()

    messages.success(request , 'The order has been cancelled!')
    return redirect('my_orders')

def acknowledge_cancel(request , id):
    check = seller_check(request)
    if check:
        return check

    try:
        order_item = OrderItem.objects.get(id=id)
    except OrderItem.DoesNotExist:
        return redirect('seller_orders')

    if order_item.seller != request.user.sellerprofile :
        return redirect('seller_orders')

    order_item.is_cancel_acknowledged = True
    order_item.save()

    messages.success(request , 'The cancellation has been acknowledged!')
    return redirect('seller_orders')
    