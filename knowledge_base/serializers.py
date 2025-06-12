from rest_framework import serializers
from .models import FaultCategory, FaultKnowledge

class FaultCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FaultCategory
        fields = '__all__'

class FaultKnowledgeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FaultKnowledge
        fields = ['id', 'category', 'category_name', 'title', 'symptoms', 'solution', 'created_at', 'updated_at'] 