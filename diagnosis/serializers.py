from rest_framework import serializers
from .models import FaultCase
from knowledge_base.serializers import FaultCategorySerializer, FaultKnowledgeSerializer

class FaultCaseSerializer(serializers.ModelSerializer):
    category_details = FaultCategorySerializer(source='category', read_only=True)
    matched_knowledge_details = FaultKnowledgeSerializer(source='matched_knowledge', read_only=True)

    class Meta:
        model = FaultCase
        fields = ['id', 'alert_info', 'metrics_info', 'log_info', 'category', 'category_details',
                 'matched_knowledge', 'matched_knowledge_details', 'analysis_result', 'solution',
                 'created_at', 'updated_at'] 