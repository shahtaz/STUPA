from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from .models import Product, Book, App, Device, LinkedDevice, Order, Community, CommunityPost
# Register your models here.

#this admin.py is for the back-end admin dashboard 
#product admin customization
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'main_prod', 'trending', 'size', 'resolution', 'processor', 'ram', 'storage', 'os', 'battery', 'connectivity')
    search_fields = ('name', 'slug', 'short_description', 'long_description')
    list_filter = ('main_prod', 'trending', 'size', 'processor')
    prepopulated_fields = {'slug': ('name',)}


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pdf_file')
    search_fields = ('name', 'author')



class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'file', 'logo_preview')
    search_fields = ('name', 'version')

    def logo_preview(self, obj):
        if obj.app_logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.app_logo.url)
        return "-"
    logo_preview.short_description = 'App Logo'


def set_devices_not_up_to_date(modeladmin, request, queryset):
    queryset.update(is_up_to_date=False)
    
class LinkedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'linked_at', 'current_version', 'is_up_to_date')
    actions = [set_devices_not_up_to_date]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_name', 'username', 'total_amount', 'created_at')
    search_fields = ('username', 'account_name')


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'community_id', 'description')

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('community', 'user', 'message', 'created_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(Device)
admin.site.register(Book, BookAdmin)
admin.site.register(LinkedDevice, LinkedDeviceAdmin)
