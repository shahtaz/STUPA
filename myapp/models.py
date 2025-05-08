from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import datetime
import os
from django.db import models
from django.contrib.auth.models import User
import random
# Create your models here.

def generate_device_id():
    device_id = str(random.randint(100000, 999999))  
    
    while Device.objects.filter(device_id=device_id).exists():
        device_id = str(random.randint(100000, 999999)) 
    
    return device_id

def get_file_path(request, filename):
    original_filename = filename
    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # Correct the formatting of time (removed `:`)
    filename = "%s_%s" % (now_time, original_filename)  # Concatenate current time with original filename
    return os.path.join('product', filename)


class Product(models.Model):
    slug = models.CharField(max_length=150, null=False, blank=False)
    name = models.CharField(max_length=150, null=False, blank=False)
    image1 = models.ImageField(upload_to=get_file_path, null=False, blank=False)
    image2 = models.ImageField(upload_to=get_file_path, null=False, blank=False)
    image3 = models.ImageField(upload_to=get_file_path, null=False, blank=False)
    short_description = models.TextField(max_length=500, null=False, blank=False)
    long_description = models.TextField(max_length=500, null=False, blank=False)
    main_prod = models.BooleanField(default=False, help_text='1 for main product and 0 for modules')
    trending = models.BooleanField(default=False, help_text='1 to show in the home page')
    price = models.FloatField(null=False, blank=False)

    size = models.CharField(max_length=150, null=True, blank=True)
    resolution = models.CharField(max_length=150, null=True, blank=True)
    processor = models.CharField(max_length=150, null=True, blank=True)
    ram = models.CharField(max_length=150, null=True, blank=True)
    storage = models.CharField(max_length=150, null=True, blank=True)
    os = models.CharField(max_length=150, null=True, blank=True)
    battery = models.CharField(max_length=150, null=True, blank=True)
    connectivity = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name
    

def upload_book_pdf(instance, filename):
    return f"library_pdfs/{filename}"

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to=upload_book_pdf)

    def __str__(self):
        return self.name
    

def upload_app_file(instance, filename):
    return f"app_file/{filename}"

class App(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    file = models.FileField(upload_to=upload_app_file)
    app_logo = models.ImageField(upload_to=upload_app_file, null=True, blank=True)  

    def __str__(self):
        return f"{self.name} v{self.version}"
    

class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True, default=generate_device_id)
    name = models.CharField(max_length=100, default="paperspace")
    firmware_version = models.CharField(max_length=50, default="zero")

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class LinkedDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    linked_at = models.DateTimeField(auto_now_add=True)
    current_version = models.CharField(max_length=50)
    is_up_to_date = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.device.name}"

# Delete file when a Product is deleted
@receiver(post_delete, sender=Product)
def delete_product_images(sender, instance, **kwargs):
    for image in [instance.image1, instance.image2, instance.image3]:
        if image and image.storage.exists(image.name):
            image.delete(save=False)

# Delete file when a Book is deleted
@receiver(post_delete, sender=Book)
def delete_book_pdf(sender, instance, **kwargs):
    if instance.pdf_file and instance.pdf_file.storage.exists(instance.pdf_file.name):
        instance.pdf_file.delete(save=False)

@receiver(post_delete, sender=App)
def delete_app_files(sender, instance, **kwargs):
    if instance.file and instance.file.storage.exists(instance.file.name):
        instance.file.delete(save=False)

    if instance.app_logo and instance.app_logo.storage.exists(instance.app_logo.name):
        instance.app_logo.delete(save=False)


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.product.price * self.quantity


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    

class Order(models.Model):
    username = models.CharField(max_length=100)
    account_name = models.CharField(max_length=200)
    delivery_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.username}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.product.price * self.quantity
    


# for the collecit on page wui
class PDFCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} by {self.user.username}"
    


def user_profile_path(instance, filename):
    return f'user_profile/{instance.user.username}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=user_profile_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            old = UserProfile.objects.get(pk=self.pk)
            if old.profile_image != self.profile_image and old.profile_image:
                old.profile_image.delete(save=False)
        except UserProfile.DoesNotExist:
            pass
        super().save(*args, **kwargs)

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    community_id = models.CharField(max_length=10, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    members = models.ManyToManyField(User, related_name='communities')

class CommunityPost(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    file = models.FileField(upload_to='community_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} in {self.community.name}"