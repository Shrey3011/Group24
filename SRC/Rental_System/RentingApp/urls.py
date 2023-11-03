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

]
