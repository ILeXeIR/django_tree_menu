# URLs for app 'menu_constructor'

from django.urls import path
from . import views


app_name = "menu_constructor"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:menu_slug>/", views.show_menu, name="show_menu"),
]