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
    path('menu/<pk>/delete/', views.DeleteMenuItem.as_view(), name='deletemenuitem'),
]