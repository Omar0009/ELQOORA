ELQOORA — Premium E-Commerce Platform 🛍️
Made for my own practise

Bangladesh's Premium Online Store 
Built with Django, payments in BDT ৳

---

##  Features

## 🛒 Store
- Animated homepage with hero, marquee, category grid, countdown timer
- Product listings with filters (category, price range, sort)
- Product detail with image zoom, quantity picker, reviews & ratings
- Shopping cart with quantity updates
- Secure checkout with Bangladesh districts
- Payment methods: Cash on Delivery, bKash, Nagad, Rocket
- Order confirmation with order number (#EQ...)

### 👤 Users
- Register / Login / Logout
- Profile management
- Order history
- Wishlist (add/remove)

### 🔑 Admin Panel (`/admin/`)
- **Custom Dashboard** (`/admin/dashboard/`) with:
  - Revenue stats (total, monthly, today) in BDT ৳
  - Orders breakdown (today, pending, delivered, etc.)
  - Product stats (active, out of stock, low stock)
  - Customer count
  - 7-day sales chart (bar + line)
  - Category breakdown donut chart
  - Recent orders table
  - Top products by views
  - Low stock alert table
- Full Product management (with thumbnail preview, price badges, stock indicators)
- Order management (status badges, inline items)
- Category management
- Review moderation
- Banner management

### 🎨 Design
- Dark luxury theme (gold & deep navy)
- Cinzel + DM Sans typography
- Smooth animations on every element
- Floating page loader
- Auto-dismissing toast notifications
- Scroll reveal animations
- Product card hover effects
- Responsive mobile layout

---

## 🚀 Quick Start

```bash
# 1. Install Python 3.10+ and pip

# 2. Run the setup script (installs deps, migrates DB, loads sample data)
chmod +x setup_and_run.sh
./setup_and_run.sh

# OR manually:
pip install -r requirements.txt
python manage.py makemigrations store
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🌐 URLs
| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Storefront Homepage |
| `http://localhost:8000/products/` | Product Listing |
| `http://localhost:8000/cart/` | Shopping Cart |
| `http://localhost:8000/checkout/` | Checkout |
| `http://localhost:8000/admin/` | Django Admin |
| `http://localhost:8000/admin/dashboard/` | **ELQOORA Dashboard** |

## 🔐 Default Admin
- **Username:** `admin`
- **Password:** `admin123`

---

## 📁 Project Structure
```
elqoora/
├── elqoora/          # Django project config
├── store/            # Main app
│   ├── models.py     # Category, Product, Order, Review, Banner, Wishlist
│   ├── views.py      # All views
│   ├── admin.py      # Custom admin + dashboard
│   ├── urls.py       # URL routing
│   ├── forms.py      # All forms
│   └── templates/
│       ├── store/    # Public templates
│       └── admin/    # Custom admin dashboard
├── media/            # Uploaded images
├── requirements.txt
├── setup_and_run.sh  # One-command setup
└── manage.py
```

## 💳 Supported Payments
- 💵 Cash on Delivery (COD)
- 💳 bKash
- 🟠 Nagad  
- 🚀 Rocket

---

Made with ❤️ for you 
thanks from Omar
