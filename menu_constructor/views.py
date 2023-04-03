from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import Menu, MenuItem


# Create your views here.
def index(request):
    menus = Menu.objects.all().order_by("title")
    context = {"menus": menus}
    return render(request, "menu_constructor/index.html", context)


def show_menu(request, menu_slug):
    menu = get_object_or_404(Menu, slug=menu_slug)
    items = menu.items.filter(parent__isnull=True).order_by("title")
    context = {"menu": menu, "items": items}
    return render(request, "menu_constructor/menu.html", context)


def open_menu(request, menu_slug, item_slug):
    menu = get_object_or_404(Menu, slug=menu_slug)
    active_item = get_object_or_404(MenuItem, menu=menu, slug=item_slug)
    parents_chain = []
    while active_item is not None:
        parents_chain.append(active_item)
        active_item = active_item.parent
    items = menu.items.filter(
        Q(parent__isnull=True) | Q(parent__in=parents_chain)
    )
    parents_dict, titles_chain = {1: (0, "")}, ""
    for i in range(len(parents_chain))[::-1]:
        level = len(parents_chain) - i
        titles_chain += parents_chain[i].title
        parents_dict[parents_chain[i].slug] = (level, titles_chain)
    for item in items:
        parent_slug = 1 if item.parent is None else item.parent.slug
        level = parents_dict[parent_slug][0]
        if level > 0:
            item.start = level * "- "
        else:
            item.start = ""
        item.full_path = parents_dict[parent_slug][1] + item.title
    items = list(items)
    items.sort(key=lambda x: x.full_path)
    context = {"menu": menu, "items": items}
    return render(request, "menu_constructor/menu.html", context)
