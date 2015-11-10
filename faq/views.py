from django.shortcuts import get_object_or_404, render, redirect
from models import FaqArticle



def home(request):
    return render(request, 'faq/index.html', {'articles': FaqArticle.objects.all().filter(disabled=False)})


def detail(request, slug, article_id):
    article = get_object_or_404(FaqArticle, pk=article_id)
    if article.slug != slug:
        redirect('faq_article', slug=article.slug, article_id=article_id)
    return render(request, 'faq/detail.html', {'article': article})


def terms(request):
    article = get_object_or_404(FaqArticle, pk=1)
    return render(request, 'faq/detail.html', {'article': article})