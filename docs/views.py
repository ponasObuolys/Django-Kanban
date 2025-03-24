from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import DocumentationCategory, DocumentationArticle

@method_decorator(login_required, name='dispatch')
class DocumentationHomeView(ListView):
    """Dokumentacijos pagrindinis puslapis"""
    model = DocumentationCategory
    template_name = 'docs/home.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return DocumentationCategory.objects.prefetch_related('articles').all()

@method_decorator(login_required, name='dispatch')
class DocumentationCategoryView(DetailView):
    """Dokumentacijos kategorijos puslapis"""
    model = DocumentationCategory
    template_name = 'docs/category.html'
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = self.object.articles.filter(is_published=True).order_by('order')
        return context

@method_decorator(login_required, name='dispatch')
class DocumentationArticleView(DetailView):
    """Dokumentacijos straipsnio puslapis"""
    model = DocumentationArticle
    template_name = 'docs/article.html'
    context_object_name = 'article'
    slug_url_kwarg = 'article_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pridedame kategorijas į kontekstą, kad būtų galima rodyti šoninį meniu
        context['categories'] = DocumentationCategory.objects.prefetch_related('articles').all()
        # Surasti ankstesnį ir kitą straipsnius
        try:
            context['prev_article'] = DocumentationArticle.objects.filter(
                category=self.object.category, 
                order__lt=self.object.order,
                is_published=True
            ).order_by('-order').first()
        except:
            context['prev_article'] = None
            
        try:
            context['next_article'] = DocumentationArticle.objects.filter(
                category=self.object.category, 
                order__gt=self.object.order,
                is_published=True
            ).order_by('order').first()
        except:
            context['next_article'] = None
            
        return context

def index(request):
    categories = DocumentationCategory.objects.all().order_by('order')
    return render(request, 'docs/index.html', {
        'categories': categories,
    })

def category(request, slug):
    categories = DocumentationCategory.objects.all().order_by('order')
    category = get_object_or_404(DocumentationCategory, slug=slug)
    return render(request, 'docs/category.html', {
        'category': category,
        'categories': categories,
    })

def article(request, slug):
    categories = DocumentationCategory.objects.all().order_by('order')
    article = get_object_or_404(DocumentationArticle, slug=slug)
    
    # Surasti ankstesnį ir kitą straipsnius
    try:
        prev_article = DocumentationArticle.objects.filter(
            category=article.category, 
            order__lt=article.order
        ).order_by('-order').first()
    except:
        prev_article = None
        
    try:
        next_article = DocumentationArticle.objects.filter(
            category=article.category, 
            order__gt=article.order
        ).order_by('order').first()
    except:
        next_article = None
    
    return render(request, 'docs/article.html', {
        'article': article,
        'categories': categories,
        'prev_article': prev_article,
        'next_article': next_article
    })

def search(request):
    categories = DocumentationCategory.objects.all().order_by('order')
    query = request.GET.get('q', '')
    
    if query:
        articles = DocumentationArticle.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()
    else:
        articles = []
    
    return render(request, 'docs/search.html', {
        'articles': articles,
        'query': query,
        'categories': categories,
    })
