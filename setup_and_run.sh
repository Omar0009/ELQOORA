#!/bin/bash
# ═══════════════════════════════════════════════════════
#   ELQOORA E-Commerce — Setup Script
# ═══════════════════════════════════════════════════════

echo ""
echo "  ███████╗██╗      ██████╗  ██████╗  ██████╗ ██████╗  █████╗ "
echo "  ██╔════╝██║     ██╔═══██╗██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗"
echo "  █████╗  ██║     ██║   ██║██║   ██║██║   ██║██████╔╝███████║"
echo "  ██╔══╝  ██║     ██║▄▄ ██║██║   ██║██║   ██║██╔══██╗██╔══██║"
echo "  ███████╗███████╗╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║  ██║"
echo "  ╚══════╝╚══════╝ ╚══▀▀═╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝"
echo ""
echo "  Premium E-Commerce — Bangladesh (BDT ৳)"
echo "═══════════════════════════════════════════════════════"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🗄️  Running database migrations..."
python manage.py makemigrations store
python manage.py migrate

echo ""
echo "👤 Creating superuser (admin)..."
echo "   Username: admin | Password: admin123"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@elqoora.com', 'admin123')
    print('   ✅ Superuser created!')
else:
    print('   ℹ️  Superuser already exists.')
"

echo ""
echo "🌱 Loading sample data..."
python manage.py shell -c "
from store.models import Category, Product, Banner
from django.utils.text import slugify

# Categories
cats_data = [
    ('Electronics', 'fas fa-mobile-alt'),
    ('Fashion', 'fas fa-tshirt'),
    ('Home & Living', 'fas fa-home'),
    ('Sports & Fitness', 'fas fa-dumbbell'),
    ('Beauty & Health', 'fas fa-spa'),
    ('Books & Stationery', 'fas fa-book'),
]
cats = {}
for name, icon in cats_data:
    slug = slugify(name)
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})
    cats[name] = cat
    print(f'   📁 Category: {name}')

# Products
products = [
    ('Samsung Galaxy A54', 'Electronics', 34999, 42000, 'Samsung Galaxy A54 5G smartphone with 50MP camera, 5000mAh battery, and Super AMOLED display.', 15, True, True),
    ('iPhone 15 Case', 'Electronics', 799, 1299, 'Premium leather case for iPhone 15 with card holder and kickstand.', 50, True, False),
    ('Casual T-Shirt (Men)', 'Fashion', 549, 799, 'Premium cotton casual t-shirt for men. Available in multiple colors. Breathable and comfortable.', 100, True, True),
    ('Women Kurti Set', 'Fashion', 1299, 1800, 'Beautiful printed kurti set for women. Perfect for casual and semi-formal occasions.', 60, True, False),
    ('Smart LED Bulb', 'Home & Living', 399, 599, '9W LED smart bulb, WiFi controlled, 16 million colors, compatible with Alexa & Google Home.', 200, True, True),
    ('Yoga Mat', 'Sports & Fitness', 899, 1299, 'Non-slip premium yoga mat, 6mm thick, eco-friendly TPE material. Perfect for all exercises.', 40, True, False),
    ('Face Wash Gel', 'Beauty & Health', 349, 449, 'Deep cleansing face wash with neem and tulsi extracts. Suitable for all skin types.', 150, True, True),
    ('Notebook A4 (Pack of 3)', 'Books & Stationery', 249, 350, 'Premium quality A4 notebook with 200 pages each. Ideal for students and professionals.', 300, True, False),
    ('Wireless Earbuds', 'Electronics', 1499, 2499, 'True wireless earbuds with 30hr battery life, deep bass, and Bluetooth 5.3.', 25, True, True),
    ('Running Shoes', 'Sports & Fitness', 2499, 3500, 'Lightweight running shoes with air cushion sole. Perfect for jogging and gym workouts.', 30, True, True),
    ('Rice Cooker 1.8L', 'Home & Living', 1899, 2500, 'Automatic rice cooker with keep-warm function, non-stick inner pot, 1.8L capacity.', 20, True, False),
    ('Moisturizer SPF 30', 'Beauty & Health', 599, 799, 'Daily moisturizer with SPF 30 protection. Hydrates and protects from UV rays.', 80, True, False),
]

for name, cat_name, price, orig, desc, stock, featured, new_arrival in products:
    slug = slugify(name)
    Product.objects.get_or_create(slug=slug, defaults={
        'name': name, 'category': cats[cat_name], 'price': price,
        'original_price': orig, 'description': desc, 'stock': stock,
        'available': True, 'featured': featured, 'new_arrival': new_arrival
    })
    print(f'   📦 Product: {name} — ৳{price:,}')

# Banners
Banner.objects.get_or_create(
    title='Welcome to ELQOORA',
    defaults={'subtitle': 'Premium Shopping in BDT ৳', 'active': True, 'order': 1}
)
print('   🎨 Sample data loaded!')
"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ ELQOORA is ready!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  🌐 Store:      http://localhost:8000/"
echo "  🔐 Admin:      http://localhost:8000/admin/"
echo "  📊 Dashboard:  http://localhost:8000/admin/dashboard/"
echo ""
echo "  👤 Admin Login:"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "  Starting development server..."
echo "═══════════════════════════════════════════════════════"
python manage.py runserver
