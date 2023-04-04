from django.db.models import Q
from django.shortcuts import render

from .models import Menu, MenuItem


# Create your views here.
def index(request):
    menus = Menu.objects.all().order_by("title")
    context = {"menus": menus}
    return render(request, "menu_constructor/index.html", context)


def open_menu(request, menu_slug, item_slug=None):
    context = {"menu_slug": menu_slug, "item_slug": item_slug}
    return render(request, "menu_constructor/menu.html", context)
