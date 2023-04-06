from django.contrib import admin
from django.urls import path
from .views import *
from django.urls.conf import include
from college import views
from django.views.generic.base import RedirectView
urlpatterns = [
    path('home/', views.HomeView.as_view(),name="home"),
    path('allproducts/', views.AllProductsView.as_view()),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="productdetail"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    # path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),
    path("register/", CustomerRegistrationView.as_view(), name="customerregistration"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(),name="customerorderdetail"),
    path("forgot-password/", PasswordForgotView.as_view(), name="passworforgot"),
    path("search/", SearchView.as_view(), name="search"),
    path('', RedirectView.as_view(url="home/")),



]
