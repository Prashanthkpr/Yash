from django.urls import path
from Menu.views import *

app_name = 'Menu'

urlpatterns = [
    path('', home, name="home")
]
