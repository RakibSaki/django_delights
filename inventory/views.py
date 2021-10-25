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
def CreateMenuItem(request, create=None):
    # form builders
    form = MenuItemForm
    formset = RecipeRequirementsForm()
    if request.method == 'POST':
        # update form
        form = form(request.POST)
        if create == 'create':
            # it is final form, try to create stuff
            if form.is_valid():
                newMenuItem = form.save(commit=False)
                formset = formset(request.POST, instance=newMenuItem)
                if formset.is_valid():
                    form.save()
                    formset.save()
                    return redirect('menu')
            else:
                formset = formset(request.POST)
        else:
            # they want the form modified
            formset = manageRecipeRequirementsForm(formset(request.POST))
            form.hide_errors = True
            formset.hide_errors = True
    else:
        # if it's get request then formset has no initial context
        formset = formset()
    return render(request, 'inventory/menu/create.html', {
        'form': form,
        'formset': formset
    })


def manageRecipeRequirementsForm(formset):
    data = []
    deleted = False
    for form in formset:
        if not form['DELETE'].value():
            data.append({
                'ingredient': form['ingredient'].value,
                'amount': form['amount'].value
            })
        else:
            deleted = True
    n = len(data)
    if not deleted:
        n += 1
    return RecipeRequirementsForm(n)(initial=data)

class Menu(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/menu/list.html'

class DeleteMenuItem(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'inventory/menu/delete.html'
    def get_success_url(self):
        return reverse_lazy('menu')