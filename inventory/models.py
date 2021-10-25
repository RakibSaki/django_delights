from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.urls import reverse_lazy

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(blank=False, max_length=50, unique=True)
    class Unit(models.TextChoices):
        KILOGRAMS = 'kg', _('kilograms')
        LITRES = 'l', _('litres')
        UNITS = '-', _('units')
    unit = models.CharField(blank=False, max_length=3, choices=Unit.choices, default=Unit.UNITS)
    in_stock = models.FloatField(default=0)
    price = models.DecimalField(blank=False, max_digits=6, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse_lazy('ingredients')

class MenuItem(models.Model):
    name = models.CharField(blank=False, max_length=50, unique=True)
    price = models.DecimalField(blank=False, max_digits=6, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])
    def __str__(self):
        return self.name
    def cost(self):
        result = 0
        for recipeRequirement in self.recipeRequirement.all():
            result += float(recipeRequirement.ingredient.price) * recipeRequirement.amount
        return result
    def get_absolute_url(self):
        return reverse_lazy('menu')

class RecipeRequirement(models.Model):
    menuItem = models.ForeignKey(MenuItem, blank=False, related_name='recipeRequirement', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, blank=False, related_name='of', on_delete=models.PROTECT)
    amount = models.FloatField(blank=False, validators=[MinValueValidator(limit_value=0.001)])
    class Meta:
        unique_together = [['menuItem', 'ingredient']]
    def __str__(self) -> str:
        return f'{self.menuItem} | {self.ingredient} {self.amount} {self.ingredient.unit}'