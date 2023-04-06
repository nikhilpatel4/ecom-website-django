from django.shortcuts import render
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from college.models import Product, Category, Cart, CartProduct, User, Customer, Order
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from college.forms import CheckoutForm,CustomerRegistrationForm,CustomerLoginForm
from django.db.models import Q


# Create your views here.
#cart nam ke tables me jab koi user addtocart karta haii to cart table me abhi only total field me total ja
#raha haii or customer field none haii to hamko aisa karna haii ki jab koi user login rahe or wah addto cart kare
#to uska nam cart nam ke table me customer field me uska nam store ho or total field me total price store ho
#to uske liye hamne class Ecommixin banaya haii ab ham is class ko inherite karege sare classes me
#taki jab user login rahe to o sari pages acesss kar sake or cart table me nam bhi jaye


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id") #addtocart hoga to cart_id session me data store hoga
        if cart_id: #agar cart_id me data hai
            cart_obj = Cart.objects.get(id=cart_id) #to o data hamko get karna haii kaha se cart table se or cart_obj veriableme store karna haii
            if request.user.is_authenticated and request.user.customer:
                #agar user authenticated haii matlab login haii or customer haii matlab customer table se onetoone haii
                cart_obj.customer = request.user.customer #to us cutomer ki request ko save karna haii cart_obj me
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)




class HomeView(EcomMixin,TemplateView):
    template_name = "college/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "vivek" #sare  product vivek me store rahege
        all_products = Product.objects.all().order_by("-id")

        paginator = Paginator(all_products, 8) #paginator ak library haii django me to mene bola ki
                                               # product tables  ke sare variables store haii all_product variables
                                                # me to ab hamne all_product me jitne bhi product haii usko paginate kiya or kaha
                                                #ki ak page pe only 8 product hi show ho or paginate aa jaye
        page_number = self.request.GET.get('page') #isase page number pata chal jayega
        print(page_number)
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context



class AllProductsView(EcomMixin,TemplateView):
    template_name = "college/allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context

class ProductDetailView(EcomMixin,TemplateView):
    template_name = "college/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context




class AddToCartView(EcomMixin,TemplateView):
    template_name = "college/addtocart.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # print(product_id)
        # get product
        product_obj = Product.objects.get(id=product_id)
        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id: #agar card_id haii to
            cart_obj = Cart.objects.get(id=cart_id)

            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()

                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart

            else:
                #agar cart_id nhi haii to cart name ke tables me insert hoga
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        else: #agar same usi cart ko wapis add kiya to
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context


class MyCartView( EcomMixin,TemplateView):
    template_name = "college/mycart.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class ManageCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]  # id fetch kara haiiyaha par
        action = request.GET.get("action")  # ab action parameter ko get kiya haii
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("mycart")



class EmptyCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None) #agar session me cart_id pressent nhi haii none haii
        if cart_id:    #cart id is not none

            cart = Cart.objects.get(id=cart_id) #cart id is not none to cart name ke tables se cart_id me jo data haii uski id get karege or cart nam ke veriables me store karege
            cart.cartproduct_set.all().delete() #ab all the product delete karna haii cartproduct table se
            cart.total = 0
            cart.save()
        return redirect("mycart")


class CheckoutView(EcomMixin,CreateView):
    template_name = "college/checkout.html"
    form_class = CheckoutForm #hamne ak form.py file me checkoutform nam ki class banaya haii usko connect kiya hai
    success_url = reverse_lazy("home") #jab checkout form successfully save ho jayega to home page pe redirect ho jayega

#most imp code for checked user is a login or not if user is not login so page is redirect after press the button checkout
    #and user is redirect on login page
#ye code jab user login rahe tab hi usko checkout.html page pe jane de
    def dispatch(self, request, *args, **kwargs): #this method is not doing anything but whenever user request then method will be exicuted
        print("hello iam dispatch method")
        if request.user.is_authenticated and request.user.customer: #jab user login rahega iska matlab user
            # authenticated haii matlab login haii or user tables one two one relationship me haii cyustomer table se
            #matlab ki user authenticated haii login haii or custemor tables me bhi haii wahi user request.user.customer
            print("login user") #jab user login rahega tab ye msg print hoga concole me
            pass
        else:
            print("not login user") #jab user login nhi hoga
            return redirect("/college/login/?next=/checkout/") #jab user login nhi rahega to redirect ho jayega login page pe
        return super().dispatch(request, *args, **kwargs)




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context


    def form_valid(self, form): #yaha se code data ko insert karne ke liye haii checkout
        cart_id = self.request.session.get("cart_id") #jo session hai cart_id jisme  data haii
        if cart_id: #to if condition chalegi
            cart_obj = Cart.objects.get(id=cart_id)  #jo data cart nam ke tables me uski id match hoti haii cart_id me jo data haii to usko cart_obj veriables me store karege
            form.instance.cart = cart_obj #cart_obj me jitna bhi data haii o insert hoga    fields = ["ordered_by", "shipping_address", "mobile", "email", "payment_method"] in sab field me
            form.instance.subtotal = cart_obj.total #sub total wali field me cart_obje me jo subtotal haii o insert hoga
            form.instance.discount = 0 #discount wale field me 0 insert hoga bydefayult
            form.instance.total = cart_obj.total #total wali field me bhi subtotal ka hi data jayega
            form.instance.order_status = "Order Received" #order_status field me order receive hi jayega bydefault
            del self.request.session['cart_id'] #delete session mens cart item delete after checkout the data

            # jab user place order karega or request me jo hamne field banaya pyment method ki
            # to jo use kalti select karega to uski request yaha aayegi
            # pm = form.cleaned_data.get("payment_method") #yaha par request ko get karega jo url me aayege pyment method field se
            # order = form.save() #us request ko save karega order veriable me
            # if pm == "Khalti": #jab request me khati hoga
            #     return redirect(reverse("khaltirequest") + "?o_id=" + str(order.id)) #to is urls.py mapping page pe jayega

            ## + "?o_id=" + str(order.id))  khalti-request page par Your order amount is Rs.ke  bhi age order product ka total  likha aana chahiye
            # elif pm == "Esewa":
            #     return redirect(reverse("ecomapp:esewarequest") + "?o_id=" + str(order.id))


        else:
            return render("mycart") #jab data insert ho jayega to mycart pe redirect hoga
        return super().form_valid(form)





#payment getway lagane ka logik haiii
class KhaltiRequestView(View): #yaha se redirwct hohga khaltirequest.html page pe
    def get(self, request, *args, **kwargs):
        # o_id = request.GET.get("o_id") # khalti-request page par Your order amount is Rs.ke  bhi age order product ka total  likha aana chahiye
        # order = Order.objects.get(id=o_id) #bs is liye ye logik likha haii
        context = {
            # "order": order #Your order amount is Rs. 70000 aisa print hoga khalti-request page pe

        }
        return render(request, "college/khaltirequest.html", context)


#
# class KhaltiVerifyView(View):
#     def get(self, request, *args, **kwargs):
#         token = request.GET.get("token")
#         amount = request.GET.get("amount")
#         o_id = request.GET.get("order_id")
#         print(token, amount, o_id)
#
#         url = "https://khalti.com/api/v2/payment/verify/"
#         payload = {
#             "token": token,
#             "amount": amount
#         }
#         headers = {
#             "Authorization": "Key test_secret_key_f59e8b7d18b4499ca40f68195a846e9b"
#         }
#
#         order_obj = Order.objects.get(id=o_id)
#
#         response = requests.post(url, payload, headers=headers)
#         resp_dict = response.json()
#         if resp_dict.get("idx"):
#             success = True
#             order_obj.payment_completed = True
#             order_obj.save()
#         else:
#             success = False
#         data = {
#             "success": success
#         }
#         return JsonResponse(data)
#
#





class CustomerRegistrationView(CreateView):
    template_name = "college/customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("home")

#registration form ka data insert karne ke liye customer wale field me
    def form_valid(self, form):
        username = form.cleaned_data.get("username") #username ka data get karega
        password = form.cleaned_data.get("password")#password ka data get karega
        email = form.cleaned_data.get("email") #Email get karega or email nam ke veriables me store karega
        user = User.objects.create_user(username, email, password) #or username email password insert karega User nam ke tables me
        #ab hamara user create ho gaya haii ab hamko Customer create karna haii
        form.instance.user = user #iska matlab ki form.py me jo field hamne mention ki haii full name address customer nam ke tables me store ho jayega or email pass username store hoga user table me
                                  #customer table me full name or address is liye insert hoga kyo ki hamne form.py file me diya haii model customer
        login(self.request, user) #login process request karega user
        return super().form_valid(form)

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("customerlogin")


class CustomerLoginView(FormView):
    template_name = "college/customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    # form_valid method is a type of post method and is available in createview formview and updateview
    #jab user login ho jayega or home page aa jayega
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword) #jab usser login rahega
        if usr is not None and Customer.objects.filter(user=usr).exists(): #jab user none nhi rahega matlab user ka na get rahega or password
            # bhi get rahega uname or pward me or user tables se data get karega uname or pword ka or us data ko filter karega
            #customer tables se kyo ki customer one to one relation shion me haii user se
            login(self.request, usr) #ham tab login kar sakte haii
        else: #agar user none haii matlab galat id pass word dala haii to envalid crudentioal ka error dega form_class me jo uper define haii
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)
    #
    # def get_success_url(self): #ja user checkout button pe click kar ke login kare or agar user login nhi haii
    #     #to sidha login button form pe ja raha haii lekin jab user login kar lega to wapis checkout page pe hi aana
    #     #chahiye uska code haii
    #     if "/college/next" in self.request.GET:
    #         next_url = self.request.GET.get("/college/next")
    #         return next_url
    #     else:
    #         return self.success_url




class CustomerProfileView(TemplateView):
    template_name = "college/customerprofile.html"

    def dispatch(self, request, *args, **kwargs): #agar user login haii to usko uski profile show honi chaiye
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            #agar user authenticated haii login haii to customertables se login user ka data filter karna haii
            #us user ka dat filter karna haii jo login se request aai ho ex vicky to vicky ka data filter karna haii
            pass
        else: #agar user login nhi haii to profile/ url pe redirect hona chahiye or is url pe login form haii
            return redirect("/college/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):#agar user login haii customer tables de jo user se onetoone haii uska data fetch karna hai customer tables se ok
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer #bs itna code user profile ka

        #ab hamko jo user login haii usne kya kya order kiya haii uska data dikhana haii order tables se
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context




class CustomerOrderDetailView(DetailView):
    template_name = "college/customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj" #agar user login haii to hi usko order id ka data show hona chahiye

    #agar ye code nhi bhi likha to bhi data fetch hoke show hoga but without login ke bhi urls ke throuhgh
    #haya par koi bhi user pahuch sakta haii
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id) #order tables se url me se fetch id ko get karege
            if request.user.customer != order.cart.customer: #or agar user customer haii
                return redirect("customerprofile") #to redirect hona haii
        else: #or agar login ngi haii to is url pe redirect hona haii
            return redirect("/college/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)



class SearchView(TemplateView):
    template_name = "college/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")#hamne serch field me name=keyword diya haii jo data aa raha haii
        #url me o keyword nam se haii usko hamne store kiya kw veriables me
        #ab hamne product tables se data ko fielter karwaya or surching lagaya title ,description ,returnpolicy pe serch keyword lagay haii
        results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw))
        print(results)
        context["results"] = results
        return context




class PasswordForgotView(TemplateView):
    template_name = "college/forgotpassword.html"





