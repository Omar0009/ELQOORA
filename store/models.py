from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class e.g. fa-mobile")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list') + f'?category={self.slug}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in BDT ৳")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0 and self.available


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=80)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number}"

    @property
    def grand_total(self):
        total = self.total_price or 0
        delivery = self.delivery_charge or 0
        return total + delivery

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random, string
            self.order_number = 'EQ' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        if not self.product_price or not self.quantity:
            return 0
        return self.product_price * self.quantity


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    cta_text = models.CharField(max_length=50, default='Shop Now')
    cta_link = models.CharField(max_length=200, default='/products/')
    bg_color = models.CharField(max_length=20, default='#0f172a')
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
