from django.contrib import admin
from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.continent_view),
    path('admin/', admin.site.urls),
    path('history/', views.history_view),
]
