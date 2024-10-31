from django.db import models

class FacebookPage(models.Model):
    page_id = models.CharField(max_length=50, unique=True) 
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Facebook Page"
        verbose_name_plural = "Facebook Pages"