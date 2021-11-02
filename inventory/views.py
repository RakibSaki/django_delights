from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import datetime

from inventory.models import Ingredient, MenuItem, Purchase, RecipeRequirement
from .forms import AddInventoryForm, CreatePurchaseForm, IngredientForm, MenuItemForm, PurchaseForm, RecipeRequirementsForm

# Create your views here.
@login_required
def home(request):
    purchases = Purchase.objects.all()
    purchases_today = purchases.filter(time__gte=datetime.date.today())
    total = 0
    profit = 0
    for i in range(len(purchases_today)):
        purchases_today[i].time = purchases_today[i].time.strftime('%I:%M %p')
        total += purchases_today[i].total
        profit += purchases_today[i].profit
    ingredients = Ingredient.objects.all()
    ingredients_stock = ingredients.filter(in_stock__gt=0)
    ingredients_stock = sorted(ingredients_stock, key=lambda i:i.value(), reverse=True)
    value = 0
    for ingredient in ingredients:
        value += ingredient.value()
    now = datetime.datetime.now()
    purchases24 = purchases.filter(time__gte=now-datetime.timedelta(days=1))
    # calculate restock
    purchases24_yesterday = purchases24.filter(time__lte=now-datetime.timedelta(hours=now.hour, minutes=now.minute))
    stocks = [i.in_stock for i in ingredients]
    indices = [i.pk for i in ingredients]
    for ingredient in ingredients:
        indices.append(ingredient.pk)
    for purchase in purchases24_yesterday:
        for requirement in purchase.menu_item.recipeRequirement.all():
            stocks[indices.index(requirement.ingredient.id)] -= requirement.amoount * purchase.amount
    stocks = [abs(a) for a in stocks]
    for purchase in purchases24:
        for requirement in purchase.menu_item.recipeRequirement.all():
            stocks[indices.index(requirement.ingredient.id)] -= requirement.amount * purchase.amount
    restocks = []
    costs = []
    restock = 0
    for i in range(len(stocks)):
        if stocks[i] < 0:
            astock = abs(stocks[i])
            restocks.append(astock)
            cost = abs(astock) * float(ingredients[i].price)
            restock += cost
            costs.append(round(cost, 2))
        else:
            restocks.append(0)
            costs.append(0)
    for i in range(len(restocks)):
        ingredients[i].restock = restocks[i]
        ingredients[i].cost = costs[i]
    ingredients = sorted(ingredients, key=lambda i:i.cost, reverse=True)
    return render(request, 'inventory/home.html', {
        'total': total,
        'profit': profit,
        'value': round(value, 2),
        'restock': round(restock, 2),
        'purchases': purchases_today[:5],
        'ingredients': ingredients_stock[:5],
        'restock_amounts': restocks,
        'restock_ingredients': ingredients[:5]
    })

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
    form = MenuItemForm()
    formset = RecipeRequirementsForm(0)
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        formset = RecipeRequirementsForm()(request.POST)
        if create == 'create':
            print('am asked to create new item')
            if form.is_valid() and formset.is_valid():
                print('creating new item')
                menuItem = form.save()
                for rform in formset:
                    if rform['ingredient'].value().isnumeric() or type(rform['ingredient'].value()) == int:
                        recipeRequirement = RecipeRequirement(menuItem=menuItem, ingredient=Ingredient.objects.get(pk=rform['ingredient'].value()), amount=rform['amount'].value())
                        recipeRequirement.save()
                return redirect('menu')
            else:
                print('you messed it up')
        else:
            print('managing form')
            form.hide_errors = True
            formset = manageRecipeRequirementsForm(formset)

    return render(request, 'inventory/menu/create.html', {
        'form': form,
        'formset': formset
    })


@login_required
def UpdateMenuItem(request, pk, update=None):
    menuItem = MenuItem.objects.get(pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menuItem)
        formset = RecipeRequirementsForm()(request.POST)
        if update == 'update':
            print('am asked to update this item')
            if form.is_valid() and formset.is_valid():
                print('updating this item')
                menuItem = form.save()
                recipeRequirements = menuItem.recipeRequirement.all()
                print('requires now', len(recipeRequirements))
                i = 0
                while i < min(len(recipeRequirements), len(formset)):
                    if formset[i]['ingredient'].value().isnumeric() or type(formset[i]['ingredient'].value()) == int:
                        recipeRequirements[i].ingredient = Ingredient.objects.get(pk=formset[i]['ingredient'].value())
                        recipeRequirements[i].amount = formset[i]['amount'].value()
                        recipeRequirements[i].save()
                    i += 1
                if i < len(formset):
                    while i < len(formset):
                        print('adding more')
                        print(formset[i]['ingredient'].value().isnumeric())
                        if formset[i]['ingredient'].value().isnumeric() or type(formset[i]['ingredient'].value()) == int:
                            recipeRequirement = RecipeRequirement(menuItem=menuItem, ingredient=Ingredient.objects.get(pk=formset[i]['ingredient'].value()), amount=formset[i]['amount'].value())
                            recipeRequirement.save()
                            print('added')
                        i += 1
                else:
                    while i < len(recipeRequirements):
                        recipeRequirements[i].delete()
                        i += 1
                return redirect('menu')
            else:
                print('you messed it up')
                print(form.errors)
                print(formset.errors)
        else:
            print('managing form')
            form.hide_errors = True
            formset = manageRecipeRequirementsForm(formset)
    else:
        recipeRequirements = menuItem.recipeRequirement.all()
        form = MenuItemForm(instance=menuItem)
        data = []
        for recipeRequirement in recipeRequirements:
            data.append({
                'ingredient': recipeRequirement.ingredient.id,
                'amount': recipeRequirement.amount
            })
        formset = RecipeRequirementsForm(len(recipeRequirements))(initial=data)

    return render(request, 'inventory/menu/update.html', {
        'object': menuItem,
        'form': form,
        'formset': formset
    })

class Menu(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/menu/list.html'



class DeleteMenuItem(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'inventory/menu/delete.html'
    def get_success_url(self):
        return reverse_lazy('menu')

@login_required
def Cost(request):
    formset = RecipeRequirementsForm(0)(request.POST)
    data = RecipeRequirementsData(formset)
    result = 0
    for recipeRequirement in data:
        try:
            result += float(Ingredient.objects.get(pk=int(recipeRequirement['ingredient'])).price) * float(recipeRequirement['amount'])
        except:
            pass
    return HttpResponse(round(result, 3))

def RecipeRequirementsData(formset):
    data=[]
    for rform in formset:
        if not rform['DELETE'].value():
            data.append({
                'ingredient': rform['ingredient'].value(),
                'amount': rform['amount'].value()
            })
    return data


def manageRecipeRequirementsForm(formset):
    data=RecipeRequirementsData(formset)
    print(data)
    n = len(data) + 1
    if formset.deleted_forms:
        print('deleted')
        n -= 1
    return RecipeRequirementsForm(n)(initial=data)

@login_required
def Inventory(request):
    in_stock = Ingredient.objects.filter(in_stock__gt=0)
    out_of_stock = Ingredient.objects.exclude(in_stock__gt=0)
    return render(request, 'inventory/inventory/list.html', {
        'in_stock': in_stock,
        'out_of_stock': out_of_stock
    })

@login_required
def AddInventory(request, pk=None):
    form = AddInventoryForm()
    if pk:
        form = AddInventoryForm(initial={'ingredient': pk, 'amount': 1})
    if request.method == 'POST':
        form = AddInventoryForm(request.POST)
        if form.is_valid():
            ingredient = Ingredient.objects.get(pk=form['ingredient'].value())
            amount = form['amount'].value()
            ingredient.in_stock = ingredient.in_stock + float(amount)
            ingredient.save()
            return redirect('inventory')
    return render(request, 'inventory/inventory/add.html', {
        'form': form
    })

@login_required
def InventoryCost(request):
    try:
        result = float(Ingredient.objects.get(pk=request.POST['ingredient']).price) * float(request.POST['amount'])
        
        print('succeeded')
        return HttpResponse(round(result, 3))
    except:
        print('failed')
        return HttpResponse('')

@login_required
def Restock(request):
    purchases = Purchase.objects.all()
    ingredients = Ingredient.objects.all()
    now = datetime.datetime.now()
    # last 24 hour purchases
    purchases24 = purchases.filter(time__gte=now-datetime.timedelta(days=1))
    # yesterday's purchases after now time yesterday
    purchases24_yesterday = purchases24.filter(time__lte=now-datetime.timedelta(hours=now.hour, minutes=now.minute))
    # record of stocks
    stocks = [i.in_stock for i in ingredients]
    # help connect between stocks records and ingredients
    indices = [i.pk for i in ingredients]
    for ingredient in ingredients:
        indices.append(ingredient.pk)
    # predict stocks at end of today
    for purchase in purchases24_yesterday:
        for requirement in purchase.menu_item.recipeRequirement.all():
            stocks[indices.index(requirement.ingredient.id)] -= requirement.amoount * purchase.amount
    # stocks can not go below zero
    stocks = [abs(a) for a in stocks]
    # predict stocks at end of tomorrow
    for purchase in purchases24:
        for requirement in purchase.menu_item.recipeRequirement.all():
            stocks[indices.index(requirement.ingredient.id)] -= requirement.amount * purchase.amount
    # predieted 'negative stocks' are needed to be restocked
    restocks = []
    costs = []
    restock = 0
    for i in range(len(stocks)):
        if stocks[i] < 0:
            astock = abs(stocks[i])
            restocks.append(astock)
            cost = abs(astock) * float(ingredients[i].price)
            restock += cost
            costs.append(round(cost, 2))
        else:
            restocks.append(0)
            costs.append(0)
    for i in range(len(restocks)):
        ingredients[i].restock = restocks[i]
        ingredients[i].cost = costs[i]
    # sort from most costly restock to least costly restock
    ingredients = sorted(ingredients, key=lambda i:i.cost, reverse=True)
    return render(request, 'inventory/inventory/restock.html', {
        'restock': round(restock, 2),
        'restock_amounts': restocks,
        'ingredients': ingredients
    })

@login_required
def CreatePurchase(request, pk=None):
    form = CreatePurchaseForm
    if pk:
        form = CreatePurchaseForm(initial={'menu_item': pk, 'amount': 1})
    message = None
    if request.method == 'POST':
        form = CreatePurchaseForm(request.POST)
        if form.is_valid():
            menuItem = MenuItem.objects.get(pk=form['menu_item'].value())
            amount = int(form['amount'].value())
            sufficient_inventory = True
            recipeRequirements = menuItem.recipeRequirement.all()
            cost = 0
            for recipeRequirement in recipeRequirements:
                if recipeRequirement.ingredient.in_stock < recipeRequirement.amount * amount:
                    sufficient_inventory = False
                    break
                cost += recipeRequirement.ingredient.price * amount
            if sufficient_inventory:
                for recipeRequirement in recipeRequirements:
                    ingredient = recipeRequirement.ingredient
                    ingredient.in_stock -= recipeRequirement.amount * amount
                    ingredient.save()
                total = menuItem.price * amount
                purchase = Purchase(menu_item=menuItem, amount=amount, total=total, profit=total-cost)
                purchase.save()
                return redirect('purchases')
            else:
                message = 'Not enough ingredients in stock to cook these items!'
    return render(request, 'inventory/purchase/create.html', {
        'form': form,
        'message': message
    })

class Purchases(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'inventory/purchase/list.html'

class UpdatePurchase(LoginRequiredMixin, UpdateView):
    model = Purchase
    template_name = 'inventory/purchase/update.html'
    form_class = PurchaseForm

class DeletePurchase(LoginRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'inventory/purchase/delete.html'
    def get_success_url(self):
        return reverse_lazy('purchases')

@login_required
def LogoutTry(request):
    return render(request, 'registration/logout.html')