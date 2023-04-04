from django.core.validators import validate_slug
from django.db import models


# Create your models here.
class Menu(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=32, unique=True,
                            validators=[validate_slug])

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    # Добавить проверку на зацикливание и принадлежность одному меню
    title = models.CharField(max_length=255)
    menu = models.ForeignKey("Menu", on_delete=models.CASCADE,
                             related_name="items")
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               blank=True, null=True,
                               related_name="children")
    slug = models.CharField(max_length=32, validators=[validate_slug])

    class Meta:
        unique_together = ("menu", "slug")

    def __str__(self):
        return self.title
