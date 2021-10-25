from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from inventory.models import Ingredient, MenuItem
from .forms import IngredientForm, MenuItemForm, RecipeRequirementsForm

# Create your views here.
@login_required
def home(request):
    return render(request, 'inventory/home.html')

class CreateIngredient(LoginRequiredMixin, CreateView):
    model = Ingredient
    template_name = 'inventory/ingredients/create.html'
    form_class = IngredientForm

class Ingredients(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'inventory/ingredients/list.html'

class UpdateIngredient(LoginRequiredMixin, UpdateView):
    model = Ingredient
    template_name = 'inventory/ingredients/update.html'
    form_class = IngredientForm

class DeleteIngredient(LoginRequiredMixin, DeleteView):
    model = Ingredient
    template_name = 'inventory/ingredients/delete.html'
    def get_success_url(self):
        return reverse_lazy('ingredients')

@login_required
def CreateMenuItem(request):
    renderForm = MenuItemForm
    renderFormset = RecipeRequirementsForm()
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        formset = RecipeRequirementsForm()
        if form.is_valid():
            newMenuItem = form.save(commit=False)
            formset = formset(request.POST, instance=newMenuItem)
            if formset.is_valid():
                form.save()
                formset.save()
                return redirect('menu')
        print(formset.errors)
        renderForm = form
        renderFormset = formset
    return render(request, 'inventory/menu/create.html', {
        'form': renderForm,
        'formset': renderFormset
    })

@login_required
def RecipeRequirements(request):
    renderFormset = RecipeRequirementsForm()
    if request.method == 'POST':
        recievedFormset = renderFormset(request.POST)
        deleted = False
        data = []
        for form in recievedFormset:
            if not form['DELETE'].value():
                data.append({
                    'ingredient': form['ingredient'].value,
                    'amount': form['amount'].value
                })
            else:
                deleted = True
        if not deleted:
            n = len(data) + 1
        else:
            n = len(data)
        renderFormset = RecipeRequirementsForm(n)
        renderFormset = renderFormset(initial=data)
    return render(request, 'inventory/menu/recipe_requirements_form.html', {
        'formset': renderFormset
    })

class Menu(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/menu/list.html'

class DeleteMenuItem(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'inventory/menu/delete.html'
    def get_success_url(self):
        return reverse_lazy('menu')