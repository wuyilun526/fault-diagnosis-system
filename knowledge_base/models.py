from django.db import models

# Create your models here.

class FaultCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Fault Categories"

class FaultKnowledge(models.Model):
    category = models.ForeignKey(FaultCategory, on_delete=models.CASCADE, related_name='faults')
    title = models.CharField(max_length=200)
    symptoms = models.TextField()
    solution = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Fault Knowledge"
