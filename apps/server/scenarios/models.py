from django.db import models


class Scenario(models.Model):
    """
    Represents a financial scenario in the system.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Scenario"
        verbose_name_plural = "Scenarios"
        ordering = ["created_at"]
