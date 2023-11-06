from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('customer/',views.customer,name='customer'),
    path('addvehicle/',views.addvehicle,name='addvehicle'),
    path('register/',views.register,name='register'),
    path('login/',views.login_handler,name='login'),
    path('logout/',views.logoutuser,name='logout'),
    path('productview/<str:pk>/',views.productview,name='productview'),
    path('history',views.history,name='history'),
    path('requestpage',views.requestpage,name='requestpage'),
    path('change_password/', views.change_password, name='change_password'),
    path('search_vehicle',views.search_vehicle,name='search_vehicle'),
    path('search_vehicle_filter',views.search_vehicle_filter,name='search_vehicle_filter')
    path('profile/',views.Profile,name='Profile'),
    path('myvehicle/', views.myvehicle, name='myvehicle'),
    path('myvehicleview/<str:pk>', views.myvehicleview, name='myvehicleview'),
    path('profilepath/<str:pk>/',views.profilepath,name='profilepath'),
    path('edit_vehicle/<str:pk>', views.edit_vehicle, name='edit_vehicle'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('password_reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='RentingApp/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='RentingApp/password_reset_complete.html'),
         name='password_reset_complete'),
]
