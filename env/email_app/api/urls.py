from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserEmailViewSet

router = DefaultRouter
router.register(r"email-check", UserEmailViewSet, basename='email-check')

urlpatterns = [
    path('', include(router.urls))
]
