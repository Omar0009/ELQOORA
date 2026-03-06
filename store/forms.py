from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'eq-input'


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'eq-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'eq-input', 'placeholder': 'Password'}))


DISTRICTS = [
    ('', 'Select District'),
    ('Dhaka', 'Dhaka'), ('Chittagong', 'Chittagong'), ('Sylhet', 'Sylhet'),
    ('Rajshahi', 'Rajshahi'), ('Khulna', 'Khulna'), ('Barishal', 'Barishal'),
    ('Rangpur', 'Rangpur'), ('Mymensingh', 'Mymensingh'), ('Comilla', 'Comilla'),
    ('Narayanganj', 'Narayanganj'), ('Gazipur', 'Gazipur'), ('Tangail', 'Tangail'),
    ('Bogra', 'Bogura'), ('Jessore', 'Jashore'), ("Cox's Bazar", "Cox's Bazar"),
    ('Narsingdi', 'Narsingdi'), ('Manikganj', 'Manikganj'), ('Other', 'Other'),
]


class OrderForm(forms.ModelForm):
    district = forms.ChoiceField(choices=DISTRICTS, widget=forms.Select(attrs={'class': 'eq-input'}))

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'district', 'postal_code', 'payment_method', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'eq-input', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'eq-input', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'eq-input', 'placeholder': '01XXXXXXXXX'}),
            'address': forms.Textarea(attrs={'class': 'eq-input', 'rows': 3, 'placeholder': 'House, Road, Area'}),
            'city': forms.TextInput(attrs={'class': 'eq-input', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'eq-input', 'placeholder': '1200'}),
            'payment_method': forms.Select(attrs={'class': 'eq-input'}),
            'notes': forms.Textarea(attrs={'class': 'eq-input', 'rows': 2, 'placeholder': 'Special instructions (optional)'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'eq-input'}),
            'comment': forms.Textarea(attrs={'class': 'eq-input', 'rows': 4, 'placeholder': 'Share your experience...'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'eq-input'}),
            'last_name': forms.TextInput(attrs={'class': 'eq-input'}),
            'email': forms.EmailInput(attrs={'class': 'eq-input'}),
        }
