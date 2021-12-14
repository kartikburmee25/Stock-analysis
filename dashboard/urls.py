from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='dashboard_home'),
    path('<ticker_symbol>-<period>', views.stock_summary, name='tearsheet')
]