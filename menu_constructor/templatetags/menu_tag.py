from django import template
from django.db.models import Q

from menu_constructor.models import Menu, MenuItem


register = template.Library()


@register.inclusion_tag('menu_tag.html')
def draw_menu(menu_slug, item_slug=None):

    if item_slug is None:
        items = MenuItem.objects.filter(
            menu__slug=menu_slug, parent__isnull=True
        ).select_related("menu").order_by("title")
        if items:
            menu = items[0].menu
        else:
            menu = Menu.objects.get(slug=menu_slug)
        return {"menu": menu, "items": items}

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
    return {"menu": menu, "items": items}