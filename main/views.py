from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Max,Min,Count,Avg
from django.db.models.functions import ExtractMonth
from .models import Banner, Category,Brand, Product, ProductAttribute, CartOrder,CartOrderItems, ProductReview, Wishlist, UserAddressBook
from .forms import SignupForm,ReviewAdd,AddressBookForm,ProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# Home
def home(request):
    banners=Banner.objects.all().order_by('-id')
    data=Product.objects.filter(is_featured=True).order_by('-id')
    return render(request,'index.html',{'data':data,'banners':banners})



#category
def category_list(request):
    data=Category.objects.all().order_by('-id')
    return render(request,'category_list.html',{'data':data})


#Brands
def brand_list(request):
    data=Brand.objects.all().order_by('-id')
    return render(request,'brand_list.html',{'data':data})

# Product List
def product_list(request):
    total_data=Product.objects.count()
    data=Product.objects.all().order_by('-id')[:6]
    return render(request,'product_list.html',
        { 
            'data':data,
            'total_data':total_data
        }
        )


#Product List According to Category
def category_product_list(request,cat_id):
    category=Category.objects.get(id=cat_id)
    data=Product.objects.filter(category=category).order_by('-id')
    return render(request,'category_product_list.html',
        {  
           'data':data,
        }
        )


#Product List According to Brands
def brand_product_list(request,brand_id):
    brand=Brand.objects.get(id=brand_id)
    data=Product.objects.filter(brand=brand).order_by('-id')
    return render(request,'brand_product_list.html',
        {  
           'data':data,
        }
        )



# Product Details
def product_detail(request,slug,id):
    product=Product.objects.get(id=id)
    related_products=Product.objects.filter(category=product.category).exclude(id=id)[:4]
    colors=ProductAttribute.objects.filter(product=product).values('color__id','color__title','color__color_code').distinct()
    sizes=ProductAttribute.objects.filter(product=product).values('id','size__id','size__title','price','color__id','image').distinct()
    reviewForm=ReviewAdd()
	 #Check
    if request.user.is_authenticated:
        canAdd=True
        reviewCheck=ProductReview.objects.filter(user=request.user,product=product).count()
        if reviewCheck > 0:
            canAdd=False
    else:
        canAdd=False
    #EndCheck

    #Fetch reviews
    reviews=ProductReview.objects.filter(product=product)
    #EndFetch

    #Fetch avg rating for reviews
    #avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    #end avgrating


    return render(request, 'product_detail.html',{'data':product,'related':related_products,'colors':colors,'sizes':sizes,'reviewForm':reviewForm,'canAdd':canAdd,'reviews':reviews,})#'avg_reviews':avg_reviews})


# Search
def search(request):
	q=request.GET['q']
	data=Product.objects.filter(title__icontains=q).order_by('id')
	return render(request,'search.html',{'data':data})


# Filter Data
def filter_data(request):
	colors=request.GET.getlist('color[]')
	categories=request.GET.getlist('category[]')
	brands=request.GET.getlist('brand[]')
	sizes=request.GET.getlist('size[]')
	minPrice=request.GET['minPrice']
	maxPrice=request.GET['maxPrice']
	allProducts=Product.objects.all().order_by('-id').distinct()
	allProducts=allProducts.filter(productattribute__price__gte=minPrice)
	allProducts=allProducts.filter(productattribute__price__lte=maxPrice)
	if len(colors)>0:
		allProducts=allProducts.filter(productattribute__color__id__in=colors).distinct()
	if len(categories)>0:
		allProducts=allProducts.filter(category__id__in=categories).distinct()
	if len(brands)>0:
		allProducts=allProducts.filter(brand__id__in=brands).distinct()
	if len(sizes)>0:
		allProducts=allProducts.filter(productattribute__size__id__in=sizes).distinct()
	t=render_to_string('ajax/product-list.html',{'data':allProducts})
	return JsonResponse({'data':t})

def load_more_data(request):
	offset=int(request.GET['offset'])
	limit=int(request.GET['limit'])
	data=Product.objects.all().order_by('-id')[offset:offset+limit]
	t=render_to_string('ajax/product-list.html',{'data':data})
	return JsonResponse({'data':t}
)

# Add to cart
def add_to_cart(request):
    #using session. cart items are saved in database only for logged in users. for others it's saved in sessions
    cart_p={}
    cart_p[str(request.GET['id'])]={
        'image':request.GET['image'],
        'title':request.GET['title'],
        'qty':request.GET['qty'],
        'price':request.GET['price'],
    }
    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data=request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty']=int(cart_data[str(request.GET['id'])]['qty'])+int(cart_p[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cartdata']=cart_data
        else:
            cart_data=request.session['cartdata']
            cart_data.update(cart_p)
            request.session['cartdata']=cart_data
    else:
        request.session['cartdata']=cart_p
    return JsonResponse({'data':request.session['cartdata'],'totalitems':len(request.session['cartdata'])})


# Cart List Page
def cart_list(request):
	total_amt=0
	if 'cartdata' in request.session:
		for p_id,item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
		return render(request, 'cart.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt},)
	else:
		return render(request, 'cart.html',{'cart_data':'','totalitems':0,'total_amt':total_amt})


    

#Delete cart item
def delete_cart_item(request):
	p_id=str(request.GET['id'])
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			del request.session['cartdata'][p_id]
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})

	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})


#Update Cart Item
def update_cart_item(request):
	p_id=str(request.GET['id'])
	p_qty=request.GET['qty']
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=p_qty
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})

# Signup Form
def signup(request):
	if request.method=='POST':
		form=SignupForm(request.POST)
		if form.is_valid():
			form.save()
			username=form.cleaned_data.get('username')
			pwd=form.cleaned_data.get('password1')
			user=authenticate(username=username,password=pwd)
			login(request, user)
			return redirect('home')
	form=SignupForm
	return render(request, 'registration/signup.html',{'form':form})


#initial checkout
@login_required
def initial_checkout(request):
    total_amt=0
    if 'cartdata' in request.session:
        for p_id,item in request.session['cartdata'].items():
            total_amt+=int(item['qty'])*float(item['price'])
            return render(request,'checkout.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	
# Checkout
@login_required
def checkout(request):
	total_amt=0
	totalAmt=0
	if 'cartdata' in request.session:
		for p_id,item in request.session['cartdata'].items():
			totalAmt+=int(item['qty'])*float(item['price'])
            # Order
		order=CartOrder.objects.create(
				user=request.user,
				total_amt=totalAmt,
			)
		# End
		for p_id,item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
			# OrderItems
			items=CartOrderItems.objects.create(
				order=order,
				invoice_no='INV-'+str(order.id),
				item=item['title'],
				image=item['image'],
				qty=item['qty'],
				price=item['price'],
				total=float(item['qty'])*float(item['price'])
				)
			# End
		return render(request, 'order-complete.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})

# Save Review
def save_review(request,pid):
	product=Product.objects.get(pk=pid)
	user=request.user
	review=ProductReview.objects.create(
		user=user,
		product=product,
		review_text=request.POST['review_text'],
		review_rating=request.POST['review_rating'],
		)
	data={
		'user':user.username,
		'review_text':request.POST['review_text'],
		'review_rating':request.POST['review_rating']
	}

	# Fetch avg rating for reviews
	#avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
	# End

	return JsonResponse({'bool':True,'data':data})#'avg_reviews':avg_reviews})


# User dashborad
import calendar
def my_dashboard(request):
	orders=CartOrder.objects.annotate(month=ExtractMonth('order_dt')).values('month').annotate(count=Count('id')).values('month','count')
	monthNumber=[]
	totalOrders=[]
	for d in orders:
		monthNumber.append(calendar.month_name[d['month']])	
		totalOrders.append(d['count'])	
	return render(request,'user/dashboard.html',{'monthNumber':monthNumber,'totalOrders':totalOrders})


# My orders
def my_orders(request):
	orders=CartOrder.objects.filter(user=request.user).order_by('-id')
	return render(request,'user/orders.html',{'orders':orders})

# order Details 
def my_order_items(request,id):
	order=CartOrder.objects.get(pk=id)
	orderitems=CartOrderItems.objects.filter(order=order).order_by('-id')
	return render(request, 'user/order-items.html',{'orderitems':orderitems})

# Wishlist
def add_wishlist(request):
	pid=request.GET['product']
	product=Product.objects.get(pk=pid)
	data={}
	checkw=Wishlist.objects.filter(product=product,user=request.user).count()
	if checkw > 0:
		data={
			'bool':False
		}
	else:
		wishlist=Wishlist.objects.create(
			product=product,
			user=request.user
		)
		data={
			'bool':True
		}
	return JsonResponse(data)

# My Wishlist
def my_wishlist(request):
	wlist=Wishlist.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/wishlist.html',{'wlist':wlist})

# My Reviews
def my_reviews(request):
	reviews=ProductReview.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/reviews.html',{'reviews':reviews})

# My AddressBook
def my_addressbook(request):
	addbook=UserAddressBook.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/addressbook.html',{'addbook':addbook})


# Save addressbook
def save_address(request):
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm
	return render(request, 'user/add-address.html',{'form':form,'msg':msg})


# Activate address
def activate_address(request):
	a_id=str(request.GET['id'])
	UserAddressBook.objects.update(status=False)
	UserAddressBook.objects.filter(id=a_id).update(status=True)
	return JsonResponse({'bool':True})

# Edit Profile
def edit_profile(request):
	msg=None
	if request.method=='POST':
		form=ProfileForm(request.POST,instance=request.user)
		if form.is_valid():
			form.save()
			msg='Data has been saved'
	form=ProfileForm(instance=request.user)
	return render(request, 'user/edit-profile.html',{'form':form,'msg':msg})

# Update addressbook
def update_address(request,id):
	address=UserAddressBook.objects.get(pk=id)
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST,instance=address)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm(instance=address)
	return render(request, 'user/update-address.html',{'form':form,'msg':msg})



