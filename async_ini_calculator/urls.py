from django.urls import path
from . import views

urlpatterns = [
    path('calculate-ini/', views.CalculateINIView.as_view(), name='calculate-ini'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('test/', views.TestView.as_view(), name='test'),
]