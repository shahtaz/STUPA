from django.urls import path
from . import views


from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('store/', views.store, name = 'store'),
    path('apps/', views.apps_view, name = 'apps'),
    path('update/', views.update_device, name='update-device'),
    path('library/', views.library_view, name='library'),
    path('cart/', views.cart_controller, name='cart'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('delete-from-cart/<int:item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('expert-note/', views.upload_and_generate_note, name='expert_note'),
    path('collection/', views.collection, name='collection'),
    path('delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    path('profile/', views.profile_view, name='profile'),
    path('community/create/', views.create_community, name='create_community'),
    path('community/<str:community_id>/', views.community_page, name='community_page'),
    path('join-community/', views.join_community, name='join_community'),
    path('community/delete/<str:community_id>/', views.delete_community, name='delete_community'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('myapp/store/<str:slug>', views.productview, name='productview')
]
