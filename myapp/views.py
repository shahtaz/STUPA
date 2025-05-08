from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from .forms import CustomUserCreationForm, CheckoutForm, ExpertNoteForm,PDFCollectionForm,ProfileImageForm, CommunityForm,CommunityPostForm
from django.core.paginator import Paginator
from .models import Product, App, Device, LinkedDevice, Book, CartItem, Order,PDFCollection,UserProfile, Community, CommunityPost
from .ai_analysis import analyze_pdf,extract_text_from_pdf,format_summary, summarize_text,generate_note_file,analyze_pdf
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
# View for login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'myapp/login.html')

# View for signup
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'myapp/signup.html', {'form': form})

# Home page view
@login_required
def home_view(request):
    products = Product.objects.filter(main_prod=True)
    modules = Product.objects.filter(main_prod=False)
    return render(request, 'myapp/home.html', {'products': products, 'modules':modules})
    # return render(request, 'myapp/home.html')


def store(request):
    items = Product.objects.all()
    return render(request, 'myapp/store.html', {'items': items}) 


def productview(request, slug):
    if Product.objects.filter(slug=slug).exists():
        product = Product.objects.filter(slug=slug).first()
        context = {'product': product}
    else:
        messages.error(request, "No product found")
        context = {}

    return render(request, 'myapp/view.html', context)


def apps_view(request):
    all_apps = App.objects.all()
    return render(request, 'myapp/apps.html', {'apps': all_apps})








@login_required
def update_device(request):
    user = request.user
    devices = Device.objects.all()

    # Check if user has already linked a device
    try:
        linked_device = LinkedDevice.objects.get(user=user)
        linked = True
    except LinkedDevice.DoesNotExist:
        linked_device = None
        linked = False

    if request.method == 'POST':
        if not linked and 'device_id' in request.POST:
            device_id = request.POST.get('device_id')
            try:
                device = Device.objects.get(device_id=device_id)
                # Check if this device is already linked to another user
                if LinkedDevice.objects.filter(device=device).exists():
                    messages.error(request, 'This device is already linked to another account.')
                else:
                    LinkedDevice.objects.create(
                        user=user,
                        device=device,
                        current_version=device.firmware_version,
                        is_up_to_date=True
                    )
                    messages.success(request, 'Device linked successfully.')
                    return redirect('update-device')
            except Device.DoesNotExist:
                messages.error(request, 'Device not found.')

        elif linked_device:
            if 'check_update' in request.POST:
                # Get the latest firmware version of the device
                latest_version = linked_device.device.firmware_version

                # Check if current version is different from the latest version
                if linked_device.current_version != latest_version:
                    linked_device.is_up_to_date = False
                    linked_device.save()
                    messages.warning(request, 'Update available.')
                else:
                    messages.success(request, 'Device is up to date.')

            elif 'perform_update' in request.POST:
                # Perform update by setting the current version to the latest firmware version
                linked_device.current_version = linked_device.device.firmware_version
                linked_device.is_up_to_date = True
                linked_device.save()
                messages.success(request, 'Device updated successfully.')

    context = {
        'linked': linked,
        'linked_device': linked_device,
        'devices': devices  # Not used in template now but kept for flexibility
    }
    return render(request, 'myapp/update.html', context)





# def library(request):
#     return render(request, 'myapp/library.html')
def library_view(request):
    # Search functionality
    search_query = request.GET.get('search', '')  # Get search query from URL parameters
    books = Book.objects.filter(name__icontains=search_query)  # Filter books by name

    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/library.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
def cart_controller(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')

        if action == 'update':
            item = get_object_or_404(CartItem, id=item_id, user=request.user)
            quantity = int(request.POST.get('quantity', 1))
            item.quantity = max(1, quantity)
            item.save()

        elif action == 'delete':
            item = get_object_or_404(CartItem, id=item_id, user=request.user)
            item.delete()

        elif action == 'checkout':
            return redirect('checkout')  # Or render checkout

    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_subtotal() for item in cart_items)
    return render(request, 'myapp/cart.html', {'cart_items': cart_items, 'total': total})


# @login_required
# def checkout_view(request):
#     # Handle checkout logic here
#     return render(request, 'myapp/checkout.html')


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)  # Get the product using the slug
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    # If the item already exists in the cart, increase the quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')  

def update_cart(request, item_id):
    if request.method == 'POST':
        try:
            # Get the cart item using the item_id
            cart_item = CartItem.objects.get(id=item_id)

            # Get the new quantity from the form data
            new_quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided

            # Update the quantity of the cart item
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()

            # Redirect back to the cart page after updating
            return redirect('cart')  # Ensure 'cart' is the name of your cart view URL
        except CartItem.DoesNotExist:
            # Handle the case where the item does not exist
            return HttpResponse('Cart item not found', status=404)
    else:
        # If the request method is not POST, redirect to the cart page or show an error
        return redirect('cart')
    

def delete_from_cart(request, item_id):
    try:
        # Find the cart item by its ID
        cart_item = get_object_or_404(CartItem, id=item_id)

        # Delete the item
        cart_item.delete()

        # Redirect back to the cart page after deletion
        return redirect('cart')  # Ensure 'cart' is the name of your cart view URL
    except CartItem.DoesNotExist:
        # Handle the case if the item does not exist
        return redirect('cart')
    
def calculate_total_amount(user):
    cart_items = CartItem.objects.filter(user=user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return total

def clear_cart(request):
    # Delete all cart items for the current user
    CartItem.objects.filter(user=request.user).delete()
    
    # Redirect to the home page
    return redirect('home')


@login_required
def checkout_view(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)  # Pass user here
        if form.is_valid():
            order = form.save(commit=False)
            order.username = request.user.username
            order.account_name = request.user.get_full_name()
            order.total_amount = calculate_total_amount(request.user)  # Calculate total amount
            order.save()

            # Clear the cart after the order is placed
            clear_cart(request)

            # Redirect to the order confirmation or another page
            return redirect('home')  # Adjust the redirect URL as necessary
    else:
        form = CheckoutForm(user=request.user)  # Pass user here as well

    return render(request, 'myapp/checkout.html', {'form': form})



def upload_and_generate_note(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        output_format = request.POST.get("format", "txt")

        text = extract_text_from_pdf(pdf_file)
        target_word_count = len(text.split()) // 2
        summary = summarize_text(text, target_word_count)
        file_buffer = generate_note_file(summary, output_format)

        filename = f"note.{output_format}"
        return FileResponse(file_buffer, as_attachment=True, filename=filename)

    return render(request, "myapp/expert_note.html")


@login_required
def collection(request):
    # Fetch the user's PDFs from the database
    pdfs = PDFCollection.objects.filter(user=request.user)

    if request.method == 'POST':
        # Handle PDF upload
        form = PDFCollectionForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_collection = form.save(commit=False)
            pdf_collection.user = request.user
            pdf_collection.save()
            return redirect('collection')
    else:
        form = PDFCollectionForm()

    return render(request, 'myapp/collection.html', {'form': form, 'pdfs': pdfs})

@login_required
def delete_pdf(request, pdf_id):
    try:
        pdf = PDFCollection.objects.get(id=pdf_id, user=request.user)

        # Delete the file from the storage
        if pdf.file and os.path.isfile(pdf.file.path):
            os.remove(pdf.file.path)

        # Delete the database entry
        pdf.delete()
    except PDFCollection.DoesNotExist:
        pass

    return redirect('collection')



@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    communities = request.user.communities.all()

    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileImageForm(instance=user_profile)

    context = {
        'form': form,
        'user_profile': user_profile,
        'communities': communities,
    }
    return render(request, 'myapp/profile.html', context)




# @login_required
# def community_view(request, community_id):
#     community = get_object_or_404(Community, community_id=community_id)
#     posts = community.communitypost_set.all()
#     is_creator = (community.creator == request.user)

#     return render(request, 'myapp/community.html', {
#         'community': community,
#         'posts': posts,
#         'is_creator': is_creator
#     })



@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            community.members.add(request.user)
            return redirect('profile')
    else:
        form = CommunityForm()
    return render(request, 'myapp/create_community.html', {'form': form})

@login_required
def delete_community(request, community_id):
    community = get_object_or_404(Community, community_id=community_id)
    if community.creator == request.user:
        community.delete()
    return redirect('profile')


@login_required
def join_community(request):
    if request.method == 'POST':
        community_id = request.POST.get('community_id')
        try:
            community = Community.objects.get(community_id=community_id)
            community.members.add(request.user)
            return redirect('profile')  
        except Community.DoesNotExist:
            return render(request, 'myapp/profile.html', {
                'error': 'Community not found.',
            })
    return redirect('profile')


@login_required
def community_page(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    posts = community.posts.all().order_by('-created_at')  
    form = CommunityPostForm()

    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.community = community
            post.user = request.user
            post.save()
            return redirect('community_page', community_id=community.id)

    return render(request, 'myapp/community_page.html', {
        'community': community,
        'posts': posts,
        'form': form,
    })