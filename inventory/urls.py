from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ingredients/create/', views.CreateIngredient.as_view(), name='createingredient'),
    path('ingredients/', views.Ingredients.as_view(), name='ingredients'),
    path('ingredients/<pk>/update/', views.UpdateIngredient.as_view(), name='updateingredient'),
    path('ingredients/<pk>/delete/', views.DeleteIngredient.as_view(), name='deleteingredient'),
    path('menu/create/', views.CreateMenuItem, name='createmenuitem'),
    path('menu/create/<create>', views.CreateMenuItem, name='createmenuitem'),
    path('menu/', views.Menu.as_view(), name='menu'),
    path('menu/<pk>/update/', views.UpdateMenuItem, name='updatemenuitem'),
    path('menu/<pk>/update/<update>', views.UpdateMenuItem, name='updatemenuitem'),
    path('menu/<pk>/delete/', views.DeleteMenuItem.as_view(), name='deletemenuitem'),
    path('menu/cost/', views.Cost, name='cost'),
    path('inventory/', views.Inventory, name='inventory'),
    path('inventory/add/', views.AddInventory, name='addinventory'),
    path('inventory/add/<pk>/', views.AddInventory, name='addinventory'),
    path('inventory/cost/', views.InventoryCost, name='inventorycost'),
    path('inventory/restock/', views.Restock, name='restock'),
    path('purchases/create/', views.CreatePurchase, name='createpurchase'),
    path('purchases/create/<pk>/', views.CreatePurchase, name='createpurchase'),
    path('purchases/', views.Purchases.as_view(), name='purchases'),
    path('purchases/<pk>/update/', views.UpdatePurchase.as_view(), name='updatepurchase'),
    path('purchases/<pk>/delete/', views.DeletePurchase.as_view(), name='deletepurchase'),
    path('logout/', views.LogoutTry, name='logouttry')
]