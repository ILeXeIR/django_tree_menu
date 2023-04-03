from django.shortcuts import render, get_object_or_404

from .models import Menu, MenuItem


# Create your views here.
def index(request):
    menus = Menu.objects.all().order_by("title")
    context = {"menus": menus}
    return render(request, "menu_constructor/index.html", context)


def show_menu(request, menu_slug):
    menu = get_object_or_404(Menu, slug=menu_slug)
    items = menu.menuitem_set.order_by("title")
    context = {"menu": menu, "items": items}
    return render(request, "menu_constructor/menu.html", context)