from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import FaultCategory, FaultKnowledge
from .serializers import FaultCategorySerializer, FaultKnowledgeSerializer

# Create your views here.

class FaultCategoryViewSet(viewsets.ModelViewSet):
    queryset = FaultCategory.objects.all()
    serializer_class = FaultCategorySerializer
    permission_classes = [AllowAny]

class FaultKnowledgeViewSet(viewsets.ModelViewSet):
    queryset = FaultKnowledge.objects.all()
    serializer_class = FaultKnowledgeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = FaultKnowledge.objects.all()
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset
