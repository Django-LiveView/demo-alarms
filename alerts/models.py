from django.db import models


class Alert(models.Model):
    ALERT_TYPES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]

    type = models.CharField(max_length=10, choices=ALERT_TYPES)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.created_at}"
