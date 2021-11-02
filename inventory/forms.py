from django import forms

from .models import Ingredient, MenuItem, Purchase, RecipeRequirement

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'

def RecipeRequirementsForm(extra=None, max_num=None):
    if extra != None:
        return forms.inlineformset_factory(MenuItem, RecipeRequirement, fields=('ingredient', 'amount'), extra=extra)
    return forms.inlineformset_factory(MenuItem, RecipeRequirement, fields=('ingredient', 'amount'))

class AddInventoryForm(forms.ModelForm):
    class Meta:
        model = RecipeRequirement
        exclude = ('menuItem',)

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'

class CreatePurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        exclude = ('total', 'profit')