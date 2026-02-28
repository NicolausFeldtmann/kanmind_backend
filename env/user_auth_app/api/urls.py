from django.urls import path
from views import RegistationView, CustomLoginView

urlpatterns = [
    path('registration/', RegistationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login')
]
