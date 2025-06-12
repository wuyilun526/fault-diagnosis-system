from django.db import models
from knowledge_base.models import FaultCategory, FaultKnowledge

class FaultCase(models.Model):
    alert_info = models.TextField()
    metrics_info = models.TextField()
    log_info = models.TextField()
    category = models.ForeignKey(FaultCategory, on_delete=models.SET_NULL, null=True, blank=True)
    matched_knowledge = models.ForeignKey(FaultKnowledge, on_delete=models.SET_NULL, null=True, blank=True)
    analysis_result = models.TextField()
    solution = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fault Case {self.id} - {self.created_at}"

    class Meta:
        verbose_name_plural = "Fault Cases"
