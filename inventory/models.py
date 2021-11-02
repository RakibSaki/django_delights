from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.urls import reverse_lazy
import datetime

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(blank=False, max_length=50, unique=True)
    class Unit(models.TextChoices):
        KILOGRAMS = 'kg', _('kilograms')
        GRAMS = 'g', _('grams')
        LITRES = 'l', _('litres')
        MILLILITRES = 'ml', _('millilitres')
        OUNCES = 'oz', _('ounces')
        POUNDS = 'lb', _('pounds')
        GALLONS = 'gal', _('gallons')
        PACKETS = 'pkt', _('packets')
        UNITS = '-', _('units')
    unit = models.CharField(blank=False, max_length=3, choices=Unit.choices, default=Unit.UNITS)
    in_stock = models.FloatField(default=0)
    price = models.DecimalField(blank=False, max_digits=6, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])
    def __str__(self):
        return f'{self.name} /{self.unit}'
    def get_absolute_url(self):
        return reverse_lazy('ingredients')
    def value(self):
        return self.in_stock * float(self.price)
    class Meta:
        ordering = ['name']

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
    class Meta:
        ordering = ['name']

class RecipeRequirement(models.Model):
    menuItem = models.ForeignKey(MenuItem, blank=False, related_name='recipeRequirement', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, blank=False, related_name='of', on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, validators=[MinValueValidator(limit_value=0.001)])
    class Meta:
        unique_together = [['menuItem', 'ingredient']]
    def __str__(self) -> str:
        return f'{self.menuItem} | {self.ingredient} {self.amount} {self.ingredient.unit}'

class Purchase(models.Model):
    menu_item = models.ForeignKey(MenuItem, blank=False, related_name='sale', on_delete=models.CASCADE)
    amount = models.IntegerField(default=1, validators=[MinValueValidator(limit_value=1)])
    total = models.DecimalField(blank=False, max_digits=6, decimal_places=2, validators=[MinValueValidator(limit_value=0.01)])
    profit = models.DecimalField(blank=False, max_digits=6, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    def get_absolute_url(self):
        return reverse_lazy('purchases')
    def __str__(self):
        return f'purchase of { self.amount } { self.menu_item } made on { self.time.strftime("%B %d, %Y") } for ${ self.total}'
    class Meta:
        ordering = ['-time', 'menu_item']