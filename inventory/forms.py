from django import forms
from django.db import models
from django.forms import fields

from .models import Ingredient, MenuItem, RecipeRequirement

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'

def RecipeRequirementsForm(extra=0):
    if extra:
        return forms.inlineformset_factory(MenuItem, RecipeRequirement, fields=('ingredient', 'amount'), extra=extra)
    else:
        return forms.inlineformset_factory(MenuItem, RecipeRequirement, fields=('ingredient', 'amount'))