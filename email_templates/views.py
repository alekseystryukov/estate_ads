from django.shortcuts import render


def preview(request):
    return render(request, 'email_templates/mce_preview.html', {})