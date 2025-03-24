from django.contrib import admin
from .models import DocumentationCategory, DocumentationArticle

@admin.register(DocumentationCategory)
class DocumentationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(DocumentationArticle)
class DocumentationArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'slug', 'order', 'is_published', 'updated_at')
    list_filter = ('category', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    ordering = ('category__order', 'order')
    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'slug', 'content')
        }),
        ('Options', {
            'fields': ('order', 'is_published')
        }),
    )
