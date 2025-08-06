# models.py
from django.db import models
from ckeditor.fields import RichTextField

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField(config_name='default')  # Uses your CKEDITOR_CONFIGS
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"