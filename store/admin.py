from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.utils.html import format_html
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, Order, OrderItem, Review, Banner, Wishlist


# ── Inline: safe for unsaved objects ─────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'product_name', 'product_price', 'quantity', 'get_subtotal']
    readonly_fields = ['get_subtotal']

    def get_subtotal(self, obj):
        try:
            if obj and obj.pk and obj.product_price and obj.quantity:
                val = (obj.product_price or 0) * (obj.quantity or 0)
                return format_html('<b style="color:#059669;">৳{:,.0f}</b>', val)
        except Exception:
            pass
        return '—'
    get_subtotal.short_description = 'Subtotal'


# ── Category ──────────────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def product_count(self, obj):
        c = obj.products.count()
        return format_html('<b style="color:#e02020;">{} products</b>', c)
    product_count.short_description = 'Products'


# ── Product ───────────────────────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'name', 'category', 'price_col', 'stock_col', 'available', 'featured', 'views', 'created_at']
    list_display_links = ['thumb', 'name']
    list_filter = ['category', 'available', 'featured', 'new_arrival', 'created_at']
    list_editable = ['available', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    fieldsets = (
        ('📦 Basic Info', {'fields': ('name', 'slug', 'category', 'description', 'image')}),
        ('💰 Pricing (BDT ৳)', {'fields': ('price', 'original_price')}),
        ('📊 Inventory', {'fields': ('stock', 'available', 'featured', 'new_arrival')}),
        ('📈 Stats', {'fields': ('views', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="48" height="48" style="border-radius:6px;object-fit:cover;">', obj.image.url)
        return format_html('<div style="width:48px;height:48px;background:#fee2e2;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:20px;">📦</div>')
    thumb.short_description = ''

    def price_col(self, obj):
        html = f'<b style="color:#e02020;font-size:14px;">৳{obj.price:,.0f}</b>'
        if obj.discount_percent:
            html += f' <del style="color:#aaa;font-size:11px;">৳{obj.original_price:,.0f}</del>'
            html += f' <span style="background:#fee2e2;color:#e02020;padding:1px 6px;border-radius:99px;font-size:10px;">{obj.discount_percent}%</span>'
        return format_html(html)
    price_col.short_description = 'Price (BDT)'

    def stock_col(self, obj):
        if obj.stock > 10:
            return format_html('<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;">✅ {}</span>', obj.stock)
        elif obj.stock > 0:
            return format_html('<span style="background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;">⚠️ {}</span>', obj.stock)
        return format_html('<span style="background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;">❌ Out</span>')
    stock_col.short_description = 'Stock'


# ── Order ─────────────────────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'grand_col', 'status_badge', 'status', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_number', 'full_name', 'phone', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('🧾 Order Info', {'fields': ('order_number', 'status', 'payment_method', 'payment_status')}),
        ('👤 Customer', {'fields': ('user', 'full_name', 'email', 'phone')}),
        ('📍 Delivery Address', {'fields': ('address', 'city', 'district', 'postal_code')}),
        ('💰 Pricing (BDT)', {'fields': ('total_price', 'delivery_charge')}),
        ('📝 Notes', {'fields': ('notes',)}),
        ('🕐 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def grand_col(self, obj):
        try:
            return format_html('<b style="color:#e02020;">৳{:,.0f}</b>', obj.grand_total)
        except Exception:
            return '—'
    grand_col.short_description = 'Grand Total'

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b', 'confirmed': '#3b82f6', 'processing': '#8b5cf6',
            'shipped': '#06b6d4', 'delivered': '#10b981', 'cancelled': '#ef4444'
        }
        c = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;">{}</span>',
            c, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'


# ── Review ────────────────────────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'stars', 'comment_short', 'approved', 'created_at']
    list_filter = ['rating', 'approved']
    list_editable = ['approved']

    def stars(self, obj):
        return format_html('<span style="color:#f59e0b;">{}☆</span>', '★' * obj.rating)
    stars.short_description = 'Rating'

    def comment_short(self, obj):
        return obj.comment[:60] + '…' if len(obj.comment) > 60 else obj.comment
    comment_short.short_description = 'Comment'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'cta_text', 'active', 'order']
    list_editable = ['active', 'order']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']


# ── Custom Dashboard ──────────────────────────────────────────────────────────
_orig_get_urls = admin.AdminSite.get_urls

def _new_get_urls(self):
    from django.urls import path as dpath
    urls = _orig_get_urls(self)
    return [dpath('dashboard/', self.admin_view(_dashboard_view), name='elqoora_dashboard')] + urls

admin.AdminSite.get_urls = _new_get_urls


def _dashboard_view(request):
    from django.db.models.functions import TruncDate
    from django.contrib.auth.models import User as AuthUser
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    stats = {
        'total_orders': Order.objects.count(),
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'delivered_orders': Order.objects.filter(status='delivered').count(),
        'total_revenue': Order.objects.filter(payment_status=True).aggregate(t=Sum('total_price'))['t'] or 0,
        'month_revenue': Order.objects.filter(payment_status=True, created_at__gte=month_ago).aggregate(t=Sum('total_price'))['t'] or 0,
        'today_revenue': Order.objects.filter(payment_status=True, created_at__date=today).aggregate(t=Sum('total_price'))['t'] or 0,
        'total_products': Product.objects.count(),
        'available_products': Product.objects.filter(available=True).count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
        'low_stock': Product.objects.filter(stock__gt=0, stock__lte=5).count(),
        'total_customers': AuthUser.objects.filter(is_staff=False).count(),
        'new_customers_month': AuthUser.objects.filter(is_staff=False, date_joined__gte=month_ago).count(),
        'total_reviews': Review.objects.count(),
    }
    status_counts = {s: Order.objects.filter(status=s).count() for s, _ in Order.STATUS_CHOICES}
    recent_orders = Order.objects.order_by('-created_at')[:10]
    new_pending = Order.objects.filter(status='pending').order_by('-created_at')
    top_products = Product.objects.order_by('-views')[:6]
    low_stock_prods = Product.objects.filter(stock__lte=5, available=True).order_by('stock')[:8]

    daily_data = (
        Order.objects.filter(created_at__gte=week_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(orders=Count('id'), revenue=Sum('total_price'))
        .order_by('date')
    )
    chart_labels = [str(d['date']) for d in daily_data]
    chart_orders = [d['orders'] for d in daily_data]
    chart_revenue = [float(d['revenue'] or 0) for d in daily_data]

    cat_data = (
        OrderItem.objects.filter(order__created_at__gte=month_ago)
        .values('product__category__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:6]
    )

    ctx = {
        'title': 'ELQOORA Dashboard',
        **stats,
        'status_counts': status_counts,
        'recent_orders': recent_orders,
        'new_pending': new_pending,
        'top_products': top_products,
        'low_stock_prods': low_stock_prods,
        'chart_labels': chart_labels,
        'chart_orders': chart_orders,
        'chart_revenue': chart_revenue,
        'cat_data': list(cat_data),
    }
    return render(request, 'admin/elqoora_dashboard.html', ctx)
