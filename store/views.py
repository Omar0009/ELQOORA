from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product, Category, Order, OrderItem, Review, Banner, Wishlist
from .forms import RegisterForm, LoginForm, OrderForm, ReviewForm, ProfileForm


def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def home(request):
    banners = Banner.objects.filter(active=True)
    featured = Product.objects.filter(featured=True, available=True)[:8]
    new_arrivals = Product.objects.filter(new_arrival=True, available=True).order_by('-created_at')[:8]
    categories = Category.objects.annotate(cnt=Count('products')).filter(cnt__gt=0)
    best_sellers = Product.objects.filter(available=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-views')[:4]
    return render(request, 'store/home.html', {
        'banners': banners, 'featured': featured,
        'new_arrivals': new_arrivals, 'categories': categories, 'best_sellers': best_sellers,
    })


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category', '')
    search = request.GET.get('q', '')
    sort = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_map = {'newest': '-created_at', 'price_low': 'price', 'price_high': '-price', 'popular': '-views'}
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/product_list.html', {
        'products': page_obj, 'categories': categories, 'current_category': current_category,
        'search': search, 'sort': sort, 'min_price': min_price, 'max_price': max_price,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    product.views += 1
    product.save(update_fields=['views'])
    related = Product.objects.filter(category=product.category, available=True).exclude(pk=product.pk)[:4]
    reviews = product.reviews.filter(approved=True)
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    review_form = ReviewForm()
    user_in_wishlist = user_reviewed = False
    if request.user.is_authenticated:
        user_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        user_reviewed = Review.objects.filter(user=request.user, product=product).exists()
    if request.method == 'POST' and request.user.is_authenticated and not user_reviewed:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            r = review_form.save(commit=False)
            r.product = product; r.user = request.user; r.save()
            messages.success(request, 'Review submitted!')
            return redirect('store:product_detail', slug=slug)
    return render(request, 'store/product_detail.html', {
        'product': product, 'related': related, 'reviews': reviews,
        'avg_rating': round(avg_rating, 1), 'review_form': review_form,
        'user_in_wishlist': user_in_wishlist, 'user_reviewed': user_reviewed,
    })


def cart_view(request):
    cart = get_cart(request)
    items, total = [], 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=pid)
            sub = p.price * qty
            total += sub
            items.append({'product': p, 'quantity': qty, 'subtotal': sub})
        except Product.DoesNotExist:
            pass
    delivery = 80 if total > 0 else 0
    return render(request, 'store/cart.html', {
        'cart_items': items, 'total': total, 'delivery': delivery, 'grand_total': total + delivery
    })


def add_to_cart(request, product_id):
    cart = get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get('quantity', 1))
    cart[pid] = cart.get(pid, 0) + qty
    save_cart(request, cart)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': sum(cart.values())})
    messages.success(request, 'Added to cart! 🛒')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    return redirect('store:cart')


def update_cart(request, product_id):
    cart = get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get('quantity', 1))
    if qty > 0:
        cart[pid] = qty
    else:
        cart.pop(pid, None)
    save_cart(request, cart)
    return redirect('store:cart')


def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:cart')
    items, total = [], 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=pid)
            sub = p.price * qty
            total += sub
            items.append({'product': p, 'quantity': qty, 'subtotal': sub})
        except Product.DoesNotExist:
            pass
    delivery = 80
    grand_total = total + delivery
    initial = {}
    if request.user.is_authenticated:
        initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
    form = OrderForm(initial=initial)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = total
            order.delivery_charge = delivery
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in items:
                OrderItem.objects.create(
                    order=order, product=item['product'],
                    product_name=item['product'].name,
                    product_price=item['product'].price,
                    quantity=item['quantity'],
                )
                p = item['product']
                p.stock = max(0, p.stock - item['quantity'])
                p.save(update_fields=['stock'])
            request.session['cart'] = {}
            request.session.modified = True
            # Log order for admin visibility
            import logging
            logger = logging.getLogger('django')
            logger.info(f"NEW ORDER: #{order.order_number} | {order.full_name} | {order.phone} | ৳{order.grand_total} | {order.get_payment_method_display()}")
            messages.success(request, f'✅ Order #{order.order_number} placed successfully!')
            return redirect('store:order_success', order.order_number)
    return render(request, 'store/checkout.html', {
        'form': form, 'cart_items': items, 'total': total,
        'delivery': delivery, 'grand_total': grand_total,
    })


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})


def register(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to ELQOORA, {user.username}!')
            return redirect('store:home')
    return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(request.GET.get('next', 'store:home'))
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out. See you soon!')
    return redirect('store:home')


@login_required
def profile(request):
    form = ProfileForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
    orders = Order.objects.filter(user=request.user).count()
    return render(request, 'store/profile.html', {'form': form, 'order_count': orders})


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'added': created})
    messages.success(request, 'Wishlist updated!')
    return redirect(request.META.get('HTTP_REFERER', '/'))
