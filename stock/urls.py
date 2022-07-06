from django.urls import path
from . import views
app_name = "stock"
urlpatterns = [
    path("index/", views.index, name="index"),
    path("", views.input, name="input"),
    
]
