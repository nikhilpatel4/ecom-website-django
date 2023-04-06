from django import forms
from .models import Order, Customer, Product
from django.contrib.auth.models import User



class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]

#hamare pass ak tables haii order nam ka jisme hame checkout user ka data insert karn hai
#to ham django ka form used kar rahe haii jisme field hogi order_by ki
#shipping_address, mobile, email, payment_method baki ka data user ka jo session me stored haii o bhi insert karna haii
#order nam ke tables me



#registration form banane ke liye jo customer tables haii usme jitna field haiii hamare pass customer nam ke tables me
# user field haii fullname hai or address haii baki email password ki field nhi haii or user field bhi onetoone
#relationshiop me haii  is liye hamko email password or userrname ke liye ye lana pada
# username = forms.CharField(widget=forms.TextInput())
   # password = forms.CharField(widget=forms.PasswordInput())
   # email = forms.CharField(widget=forms.EmailInput())

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ["username", "password", "email", "full_name", "address"]

#agar koi user pahle se exict haii or usi nam ka user wapis registration karega to nhi hoga alredy exists nam ka error dega
    def clean_username(self):
            uname = self.cleaned_data.get("username")
            if User.objects.filter(username=uname).exists(): #agar exict haii
                raise forms.ValidationError(
                    "Customer with this username already exists.")

            return uname  #or uska nam return karega


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
#hamko login karne ke liye two field chahiye username or password  jo user table se hogi