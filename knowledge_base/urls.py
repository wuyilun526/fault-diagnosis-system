from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FaultCategoryViewSet, FaultKnowledgeViewSet

router = DefaultRouter()
router.register(r'categories', FaultCategoryViewSet)
router.register(r'knowledge', FaultKnowledgeViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 