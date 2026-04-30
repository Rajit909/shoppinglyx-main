from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerRegisterationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobile = Product.objects.filter(category='M')
        laptop = Product.objects.filter(category='L')
        footwear = Product.objects.filter(category='FW')
        accessories = Product.objects.filter(category='AS')
        appliances = Product.objects.filter(category='AL')

        return render(request, 'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobile':mobile,'laptop':laptop,'footwear':footwear,'accessories':accessories,'appliances':appliances})

class ProductDetailView(View):
    def get(self, request,pk):
        product = get_object_or_404(Product, pk=pk)
        item_already_in_cart=False
        if request.user.is_authenticated:
            item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:6]
        
        return render(request, 'app/productdetail.html', {
            'product': product,
            'item_already_in_cart': item_already_in_cart,
            'related_products': related_products
        })

def add_to_cart(request):
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        user = request.user
        # Check if item already in cart
        cart_item = Cart.objects.filter(user=user, product=product).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            Cart(user=user, product=product).save()
        messages.success(request, f"{product.title} added to cart successfully!")
    else:
        # Session-based cart for guests
        cart = request.session.get('cart', {})
        str_id = str(product_id)
        if str_id in cart:
            cart[str_id] += 1
        else:
            cart[str_id] = 1
        request.session['cart'] = cart
        messages.info(request, f"{product.title} added to guest cart. Login to checkout!")
    
    return redirect('/cart')

def show_cart(request):
    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    cart_items = []

    if request.user.is_authenticated:
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        for p in cart_items:
            amount += (p.quantity * p.product.discounted_price)
    else:
        # Guest cart items
        session_cart = request.session.get('cart', {})
        for prod_id, quantity in session_cart.items():
            product = Product.objects.filter(id=prod_id).first()
            if product:
                # Mock a cart object for the template
                item = type('obj', (object,), {
                    'product': product,
                    'quantity': quantity,
                    'total_cost': quantity * product.discounted_price
                })
                cart_items.append(item)
                amount += item.total_cost

    if cart_items:
        total_amount = amount + shipping_amount
        return render(request, 'app/addtocart.html', {
            'carts': cart_items, 
            'totalamount': total_amount, 
            'amount': amount,
            'shipping_amount': shipping_amount
        })
    else:
        return render(request, 'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        amount = 0.0
        shipping_amount = 70.0
        quantity = 0

        if request.user.is_authenticated:
            c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
            c.quantity += 1
            c.save()
            quantity = c.quantity
            cart_product = Cart.objects.filter(user=request.user)
            for p in cart_product:
                amount += (p.quantity * p.product.discounted_price)
        else:
            cart = request.session.get('cart', {})
            str_id = str(prod_id)
            if str_id in cart:
                cart[str_id] += 1
                quantity = cart[str_id]
                request.session['cart'] = cart
            
            for p_id, q in cart.items():
                product = Product.objects.filter(id=p_id).first()
                if product:
                    amount += (q * product.discounted_price)

        data = {
            'quantity': quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        amount = 0.0
        shipping_amount = 70.0
        quantity = 0

        if request.user.is_authenticated:
            c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            quantity = c.quantity
            cart_product = Cart.objects.filter(user=request.user)
            for p in cart_product:
                amount += (p.quantity * p.product.discounted_price)
        else:
            cart = request.session.get('cart', {})
            str_id = str(prod_id)
            if str_id in cart and cart[str_id] > 1:
                cart[str_id] -= 1
                quantity = cart[str_id]
                request.session['cart'] = cart
            else:
                quantity = cart.get(str_id, 0)
            
            for p_id, q in cart.items():
                product = Product.objects.filter(id=p_id).first()
                if product:
                    amount += (q * product.discounted_price)

        data = {
            'quantity': quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        amount = 0.0
        shipping_amount = 70.0

        if request.user.is_authenticated:
            c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
            c.delete()
            cart_product = Cart.objects.filter(user=request.user)
            for p in cart_product:
                amount += (p.quantity * p.product.discounted_price)
        else:
            cart = request.session.get('cart', {})
            str_id = str(prod_id)
            if str_id in cart:
                del cart[str_id]
                request.session['cart'] = cart
            
            for p_id, q in cart.items():
                product = Product.objects.filter(id=p_id).first()
                if product:
                    amount += (q * product.discounted_price)

        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount if amount > 0 else 0
        }
        return JsonResponse(data)



@login_required
def cancel(request, pk):
    order = get_object_or_404(OrderPlaced, id=pk, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f"Order #{pk} has been cancelled successfully.")
        return redirect("orders")
    return render(request, 'app/cancel_order.html', {'order': order})

    

@login_required
def payment_done(request):
    user = request.user
    custid=request.GET.get('custid')
    customer=get_object_or_404(Customer, id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    
    # Clear buy now session if it exists
    if 'buy_now_prod' in request.session:
        del request.session['buy_now_prod']
        
    return redirect("orders")


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})

def buy_now(request):
    product_id = request.GET.get('prod_id')
    if product_id:
        request.session['buy_now_prod'] = product_id
        return redirect('checkout')
    return redirect('home')



@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})


def change_password(request):
 return render(request, 'app/changepassword.html')

def category(request, code):
    category_map = {
        'M': 'Mobiles',
        'L': 'Laptops',
        'TW': 'Top Wear',
        'BW': 'Bottom Wear',
        'FW': 'Footwear',
        'AS': 'Accessories',
        'AL': 'Appliances'
    }
    
    category_name = category_map.get(code, 'Products')
    products = Product.objects.filter(category=code)
    
    # Filtering logic
    brand = request.GET.get('brand')
    price = request.GET.get('price')
    
    if brand:
        products = products.filter(brand=brand)
    if price == 'below':
        products = products.filter(discounted_price__lt=10000)
    elif price == 'above':
        products = products.filter(discounted_price__gt=10000)
    
    # Get all unique brands for this category for the sidebar
    brands = Product.objects.filter(category=code).values_list('brand', flat=True).distinct()
    
    return render(request, 'app/category.html', {
        'products': products,
        'category_name': category_name,
        'brands': brands,
        'category_code': code
    })

def mobile(request, data=None):
    # Keep the original mobile view logic for backward compatibility if needed, 
    # but we could also just use the generic category view.
    # Let's make it more robust.
    mobiles = Product.objects.filter(category='M')
    if data:
        if data in ['Samsung', 'Apple', 'Redmi']:
            mobiles = mobiles.filter(brand=data)
        elif data == 'below':
            mobiles = mobiles.filter(discounted_price__lt=10000)
        elif data == 'above':
            mobiles = mobiles.filter(discounted_price__gt=10000)
    
    return render(request, 'app/mobile.html', {'mobiles': mobiles})

def login(request):
 return render(request, 'app/login.html')

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegisterationForm()
        return render(request, 'app/customerregistration.html',{'form':form})
    def post(self,request):
        form = CustomerRegisterationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    
    # Check if this is a Buy Now flow
    buy_now_id = request.session.get('buy_now_prod')
    if buy_now_id:
        product = get_object_or_404(Product, id=buy_now_id)
        # Mock a cart item for the template
        item = type('obj', (object,), {
            'product': product,
            'quantity': 1,
            'total_cost': product.discounted_price
        })
        cart_items = [item]
        amount = product.discounted_price
        # Clear it after getting the data (or keep it until payment done)
    else:
        cart_items = Cart.objects.filter(user=user)
        amount = 0.0
        for p in cart_items:
            amount += (p.quantity * p.product.discounted_price)

    shipping_amount = 70.0
    totalamount = 0.0
    if cart_items:
        totalamount = amount + shipping_amount
        return render(request, 'app/checkout.html', {
            'add': add, 
            'totalamount': totalamount, 
            'cart_items': cart_items,
            'amount': amount
        })
    
    return redirect('home')


@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulations|| Profile Updated Successfully')
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})
            
def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(brand__icontains=query) |
            Q(category__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    return render(request, 'app/search.html', {
        'products': products,
        'query': query
    })
