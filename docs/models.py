from django.db import models
from django.utils.translation import gettext_lazy as _

class DocumentationCategory(models.Model):
    """Dokumentacijos kategorija"""
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    
    class Meta:
        verbose_name = _("Documentation Category")
        verbose_name_plural = _("Documentation Categories")
        ordering = ['order']
    
    def __str__(self):
        return self.name

class DocumentationArticle(models.Model):
    """Dokumentacijos straipsnis"""
    category = models.ForeignKey(
        DocumentationCategory, 
        on_delete=models.CASCADE, 
        related_name='articles',
        verbose_name=_("Category")
    )
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    content = models.TextField(_("Content"))
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_published = models.BooleanField(_("Is Published"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Documentation Article")
        verbose_name_plural = _("Documentation Articles")
        ordering = ['category__order', 'order']
    
    def __str__(self):
        return self.title
