from django.db.models import Q
from django.shortcuts import render

from .models import Menu, MenuItem

from django.db import connection, reset_queries
import time
import functools


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func

# Create your views here.
@query_debugger
def index(request):
    menus = Menu.objects.all().order_by("title")
    context = {"menus": menus}
    return render(request, "menu_constructor/index.html", context)


@query_debugger
def show_menu(request, menu_slug):
    # Добавить проверку для пустого меню
    # menu = get_object_or_404(Menu, slug=menu_slug)
    # items = menu.items.filter(parent__isnull=True).order_by("title")
    items = MenuItem.objects.filter(
            menu__slug=menu_slug, parent__isnull=True
        ).select_related("menu").order_by("title")
    for item in items:
        menu = item.menu
        break
    context = {"menu": menu, "items": items}
    return render(request, "menu_constructor/menu.html", context)


@query_debugger
def open_menu(request, menu_slug, item_slug):
    items = MenuItem.objects.filter(menu__slug=menu_slug).select_related(
            "menu", "parent")
    values_list = items.values("id", "parent", "title", "slug")
    values_dict = {}
    for item in values_list:
        id = item.pop("id")
        if item["slug"] == item_slug:
            active_id = id
        values_dict[id] = (item["parent"], item["title"])
    parents_chain = []
    while active_id is not None:
        parents_chain.append(active_id)
        active_id = values_dict[active_id][0]
    items = items.filter(
        Q(parent__isnull=True) | Q(parent_id__in=parents_chain)
    )
    parents_dict, title_string = {"None": (0, "")}, ""
    for i in range(len(parents_chain))[::-1]:
        level = len(parents_chain) - i
        title_string += values_dict[parents_chain[i]][1]
        parents_dict[parents_chain[i]] = (level, title_string)
    for item in items:
        parent_id = "None" if item.parent is None else item.parent_id
        level = parents_dict[parent_id][0]
        item.start = level * "- " if level > 0 else ""
        item.full_path = parents_dict[parent_id][1] + item.title
    menu = item.menu
    items = list(items)
    items.sort(key=lambda x: x.full_path)
    context = {"menu": menu, "items": items}
    return render(request, "menu_constructor/menu.html", context)
