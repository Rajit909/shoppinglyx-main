from .models import Cart

def cart_count(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
    else:
        # For guest users, count items in session cart
        cart = request.session.get('cart', {})
        totalitem = len(cart) # or sum of quantities if preferred, but usually count of unique items
    
    return {'totalitem': totalitem}
