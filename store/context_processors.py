from .models import Category

def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    categories = Category.objects.all()
    return {'cart_count': count, 'all_categories': categories}
