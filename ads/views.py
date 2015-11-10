#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import resolve

from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate

from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.core.cache import cache

from django.utils.translation import ugettext_lazy as _

from ads.models import Ad, District, Category, SubCategory, PaidOption, Town, ImageAttachment, VisitHistory, VideoAttachment
from ads import forms
from ads.forms import ImageAttachmentForm, VideoAttachmentForm
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from ads import tasks
from rudeword.models import RudeWord, WordAnalyser
from recipes.email import get_mailbox_by_email

from haystack.models import SearchResult


import json
from datetime import datetime
import urllib
import hashlib

from os.path import basename
import re


from email_templates.models import EmailTemplate
from registration import signals


def home(request):
    categories = Category.objects.all()
    ordering = [1, 4, 8, 11, 14, 2, 5, 9, 12, 15, 3, 6, 10, 13]
    categories = sorted(categories, key=lambda i: ordering.index(i.id))
    return render(request, 'ads/home.html', {'form': forms.FilterSearchForm(hide_fields=['offering',
                                                                                         'category', 'district']),
                                             'categories': categories})


def category(request, slug, page=None):
    cat = Category.objects.filter(slug=slug)[:1][0]
    page, form, counts, params = get_listing_items(request, page, cat)

    # params without category
    data = request.GET.copy()
    str_data = {}
    for k, v in data.iteritems():
        str_data[k] = unicode(v).encode('utf-8')
    params = urllib.urlencode(str_data, True)

    private = None
    if 'private' in request.GET:
        private = "private" if request.GET.get('private') == "private" else "business"
    return render(request, 'ads/category.html',
                  {'page': page,
                   'form': form,
                   'today': datetime.now(),
                   'category': cat.id,
                   'cat': cat,
                   'counts': counts,
                   'params': params,
                   'private': private,
                   'referer': (_('Search'), "search")})


def search(request, page=None):
    page, form, counts, params = get_listing_items(request, page)
    private = None
    if 'private' in request.GET:
        private = "private" if request.GET.get('private') == "private" else "business"

    return render(request, 'search/search.html',  {'page': page,
                                                   'today': datetime.now(),
                                                   'form': form,
                                                   'counts': counts,
                                                   'params': params,
                                                   'private': private,
                                                   'q': request.GET.get('q'),
                                                   'referer': (_('Search'), "search")})


def get_listing_items(request, page=None, cat=None):  # this is not view, just same code for two views above
    limit = 12
    data = request.GET.copy()
    if cat:
        data['category'] = cat.id

    str_data = {}
    for k, v in data.iteritems():
        str_data[k] = unicode(v).encode('utf-8')
    params = urllib.urlencode(str_data, True)

    cache_key = 'search_' + params + '_p' + str(page or 1)
    cache_key = hashlib.md5(cache_key).hexdigest()
    cache_context = cache.get(cache_key)
    if cache_context is None:
        if cat is None and 'category' in request.GET and request.GET['category']:
            cat = Category.objects.get(pk=request.GET['category'])

        form_class = Ad.get_search_form(request, cat)
        form = form_class(data, label_suffix="")
        objects = form.search()

        #  filter by private here, cos we need all/private/business stats
        all_ads = None
        private = None
        if 'private' in data:
            all_ads = objects.count()
            objects = objects.filter(private=int(data['private'] == "private"))
            private = "private" if data['private'] == "private" else "business"

        paginator = Paginator(objects, limit)
        try:
            page = paginator.page(page or 1)
        except EmptyPage:
            raise Http404

        if private is None:
            all_ads = paginator.count
            private_c = objects.filter(private=1).count()
            business_c = all_ads - private_c
        elif private == 'private':
            private_c = paginator.count
            business_c = all_ads - private_c
        else:
            business_c = paginator.count
            private_c = all_ads - business_c
        counts = {'all': all_ads,
                  'private': private_c,
                  'business': business_c}

        # !!!! prepare data !!!!
        ids = [int(obj.pk) for obj in page.object_list]
        # for haystack results check that items still in DB and fetch them
        if page.object_list and isinstance(page.object_list[0], SearchResult):
            ads = {obj.id: obj for obj in Ad.objects.filter(id__in=ids)[:limit]}
            new_object_list = []
            for obj in page.object_list:
                if int(obj.pk) in ads:
                    new_object_list.append(ads[int(obj.pk)])
            page.object_list = new_object_list

        images = ImageAttachment.objects.all().filter(ad_id__in=ids)
        logos = {ad_id: None for ad_id in ids}
        for img in images:
            logos[img.ad_id] = img
        dist_ids = [obj.district_id for obj in page.object_list]
        districts = {dist.id: dist for dist in District.objects.all().filter(id__in=set(dist_ids))}

        if cat:
            categories = {cat.id: cat}
        else:
            cat_ids = [obj.category_id for obj in page.object_list]
            categories = {cat.id: cat for cat in Category.objects.all().filter(id__in=set(cat_ids))}

        sub_cat_ids = []
        for obj in page.object_list:
            if obj.sub_category_id:
                sub_cat_ids.append(obj.sub_category_id)
        sub_categories = {cat.id: cat for cat in SubCategory.objects.all().filter(id__in=set(sub_cat_ids))}

        new = []
        for obj in page.object_list:
            obj.category = categories[obj.category_id]
            if obj.sub_category_id:
                obj.sub_category = sub_categories[obj.sub_category_id]
            if obj.district_id:
                obj.district = districts[obj.district_id]
            obj.logo = logos[obj.id]
            new.append(obj)
        page.object_list = new

        page.paginator.object_list = page.object_list
        cache.set(cache_key, {'page': page, 'counts': counts, 'form': form}, 3600)
    else:
        counts = cache_context['counts']
        form = cache_context['form']
        page = cache_context['page']

    return page, form, counts, params




def autocomplete(request):
    sqs = Ad.search(request.GET, True)[:5]
    suggestions = [result.title for result in sqs]
    import re
    q = request.GET.get('q', '')
    regexp = re.compile(r'[\w]*[\s\W]*[\w]*' + re.escape(q) + r'[\w]*[\s\W]*[\w]*', re.IGNORECASE | re.UNICODE)
    res = []
    for item in suggestions:
        match = regexp.search(item)
        if match is not None:
            res.append(match.group(0))
        else:
            res.append(item)

    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({
        'results': res
    })
    return HttpResponse(the_data, content_type='application/json')


def ajax_get_filters(request, cat_id, sub_cat_id):
    if request.GET.get('offering'):
        form_class = forms.FilterSearchForm
    else:
        try:
            if sub_cat_id != '0':
                cat = get_object_or_404(SubCategory, pk=sub_cat_id)
                if cat.form_filter is None:
                    cat = cat.category
            else:
                cat = get_object_or_404(Category, pk=cat_id)
        except Category.DoesNotExist:
            form_class = forms.PriceSearchForm
        else:
            if cat.form_filter:
                try:
                    form_class = getattr(forms, cat.form_filter)
                except AttributeError:
                    form_class = forms.PriceSearchForm
            else:
                form_class = forms.PriceSearchForm
    form = form_class({'category': cat_id, 'sub_category': sub_cat_id})
    return render(request, 'ads/additional_filters.html', {'form': form, 'is_ajax': True})


@cache_page(3600)
def get_district_opts(request, town_id):
    return render(request, 'ads/district_options.html', {'options': District.objects.filter(town_id=town_id)})


def detail(request, slug, ad_id):
    # messages.success(request, _('Your add was successfully added.'))
    # messages.info(request, 'Three credits remain in your account.')
    # messages.warning(request, 'Your account expires in three days.')
    # messages.error(request, 'Document deleted because you use rude words in it :"dfgdfgdg", "dgdfgdfgg", "drfgfffffffffffffhgfhgf", "drgggggg", "dfgdfgdg", "dgdfgdfgg", "drfgfffffffffffffhgfhgf", "drgggggg".')

    cache_key = 'detail_%s' % ad_id
    ad = cache.get(cache_key)
    if ad is None:
        ad = get_object_or_404(Ad, pk=ad_id)
        ad.town, ad.category, ad.sub_category, ad.user = ad.town, ad.category, ad.sub_category, ad.user
        ad.similars = ad.similar.all()
        ad.images, ad.videos = ad.imageattachment_set.all(), ad.videoattachment_set.all()

    if ad.blocked is not False and request.user.id == ad.user.id:
        if ad.rude_words:
            messages.error(request, _('Your ad was blocked, because you use rude words in it: %s') % ", ".join([w.id for w in ad.rude_words.all()]))
        else:
            messages.error(request, _('Your ad was blocked by admin'))
    elif ad.disabled or ad.blocked is not False:
        raise Http404()

    # for breadcrumb
    referer = (_('Search'), reverse('search', args=(1,)) + '?'
               + urllib.urlencode({'category': ad.category_id,
                                   'town': ad.town_id,
                                   'district': ad.district_id if ad.district_id else '',
                                   'offering': "" if ad.offering else 1}), "search")

    if 'HTTP_REFERER' in request.META:
        referer_arr = request.META['HTTP_REFERER'].split('/')[:4]
        if referer_arr == request.build_absolute_uri(reverse('search', args=(1,))).split('/')[:4]:
            referer = (_('Search'), request.META['HTTP_REFERER'], "search")
        elif referer_arr == request.build_absolute_uri(reverse('profile')).split('/')[:4]:
            referer = (_('Profile'), request.META['HTTP_REFERER'], "user")


    # save last viewed
    ad.add_to_visited(request)
    cache.set(cache_key, ad, 3600)

    if request.user.is_authenticated():
        ids_q = VisitHistory.objects.filter(user=request.user).exclude(ad_id=ad_id)[:3].values_list('ad', flat=True)
        ids = [aid for aid in ids_q]
        history = Ad.objects.filter(id__in=ids)
    else:
        history = Ad.objects.filter(pk__in=request.session['history']).exclude(pk=ad_id)[:3] if request.session['history'] else []
    return render(request, 'ads/detail.html', {'ad': ad, 'referer': referer, 'today': datetime.now(),
                                               'send_form': forms.SendToFriendForm(initial={'ad_id': ad_id}),
                                               'history': history})


def ajax_send_to_friend(request):
    from email_templates.models import EmailTemplate
    if request.method == 'POST':
        form = forms.SendToFriendForm(request.POST)
        if form.is_valid():
            try:
                ad = Ad.objects.get(pk=form.cleaned_data['ad_id'])
            except Ad.DoesNotExist:
                return HttpResponse(json.dumps({'error': 'Ad does not exist anymore'}), content_type="application/json")
            else:
                # from django.core.mail import EmailMessage
                # email = EmailMessage(ad.title, ad.desc, to=[form.cleaned_data['email']])
                # email.send()
                images = ad.imageattachment_set.all()
                if images:
                    image = images[0]
                else:
                    image = None
                email = EmailTemplate.objects.get(pk='send_ad_to_friend')
                email.send(form.cleaned_data['email'], None, ad=ad, image=image.file.url if image is not None else None)

                return HttpResponse(json.dumps({'success': 1}), content_type="application/json")
    return HttpResponse(json.dumps({'error': 'method'}), content_type="application/json")


def post_ad(request):

    files = {'images': [], 'video': []}

    if request.method == "POST":

        from_class = Ad.get_form_class(request.POST.get('category'), request.POST.get('sub_category'),
                                       request.POST.get('offering') == "True")
        form = from_class(request.POST, anonym=(not request.user.is_authenticated()))
        if form.is_valid():
            obj = form.save(commit=False)  # returns unsaved instance
            if request.user.is_authenticated():
                obj.user = request.user
                if not obj.district:
                    obj.town = Town.objects.get(pk=request.session.get('TOWN_SELECTED', 1))
                obj.save()
                obj.blocked = WordAnalyser.block_object(obj, Ad.fields_for_analyse)
                if obj.blocked is not False:
                    obj.save()
            else:
                try:
                    obj.user = get_user_model().objects.get(email=form.cleaned_data['email'])
                except get_user_model().DoesNotExist:
                    obj.user = get_user_model().objects.create_user(form.cleaned_data['email'], None, is_active=False)
                finally:
                    obj.save_as_disabled(form.cleaned_data['email'])

            tasks.find_similar(obj.id)
            Ad.save_files(request.POST, obj)
            if obj.disabled:
                return redirect('activate_ad', ad_id=obj.id)
            else:
                messages.success(request, _('Your add was successfully added.'))
                return redirect(obj.get_absolute_url())
        else:
            for img_id in request.POST.getlist('images[]'):
                file_obj = ImageAttachment.objects.get(pk=img_id)
                if file_obj:
                    files['images'].append(file_obj)
            for vid_id in request.POST.getlist('video[]'):
                file_obj = VideoAttachment.objects.get(pk=vid_id)
                if file_obj:
                    files['video'].append(file_obj)
    else:
        from_class = Ad.get_form_class(offering=True)
        form = from_class(anonym=(not request.user.is_authenticated()))

    return render(request, 'ads/post_ad.html', {'form': form,
                                                'files': files,
                                                'images_limit': settings.UPLOAD_IMAGES_LIMIT - len(files['images']),
                                                'video_limit': settings.UPLOAD_VIDEO_LIMIT - len(files['video'])})


def activate_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if not ad.disabled:
        return redirect(ad.get_absolute_url())
    messages.warning(request, _('Go to your Email-inbox and click on link to activate this ad.'))
    return render(request, 'ads/activate_ad.html', {'ad': ad, 'mail_inbox': get_mailbox_by_email(ad.user.email)})


def activate_ad_key(request, ad_id, activation_key):
    ad = Ad.objects.get(pk=ad_id)
    if not ad.disabled:
        return redirect(ad.get_absolute_url())
    if ad.activation_key == activation_key:
        ad.disabled = False
        ad.activation_key = 'ACTIVATED'
        ad.save()
        if not request.user.is_authenticated():
            user = authenticate(username=ad.user.email, password=None, anonymus=True)
            login(request, user)
        messages.success(request, _('Your add was successfully activated.'))
        return redirect(ad.get_absolute_url())
    return redirect('activate_ad', ad_id=ad.id)


@login_required
def edit_ad(request, ad_id=None):
    instance = get_object_or_404(Ad, id=ad_id, user_id=request.user.id)

    if request.method == "POST":
        cache_key = 'detail_%s' % ad_id
        cache.delete(cache_key)
        offering = request.POST.get('offering')
        if offering:
            offering = True if offering == 'True' else False

        from_class = Ad.get_form_class(request.POST.get('category'),
                                       request.POST.get('sub_category'),
                                       (offering if offering is not None else instance.offering))

        form = from_class(request.POST, instance=instance)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.blocked = WordAnalyser.block_object(obj, Ad.fields_for_analyse)
            obj.save()
            tasks.find_similar(obj.id)
            Ad.save_files(request.POST, obj)
            messages.success(request, _('Your add was successfully updated.'))
            return redirect(obj.get_absolute_url())
    else:
        from_class = Ad.get_form_class(instance.category,
                                       instance.sub_category if hasattr(instance, 'sub_category') else None,
                                       instance.offering)
        form = from_class(instance=instance)

    files = {'images': instance.imageattachment_set.all(), 'video': instance.videoattachment_set.all()}

    return render(request, 'ads/post_ad.html', {'form': form,
                                                'files': files,
                                                'images_limit': settings.UPLOAD_IMAGES_LIMIT - len(files['images']),
                                                'video_limit': settings.UPLOAD_VIDEO_LIMIT - len(files['video'])})


#@cache_page(3600)
def ajax_get_fields(request, cat_id, sub_cat_id):
    if sub_cat_id != '0':
        cat = SubCategory.objects.get(pk=sub_cat_id)
        if cat.form_add is None:
            cat = cat.category
    else:
        cat = Category.objects.get(pk=cat_id)

    from_class = Ad.get_form_class(cat_id, sub_cat_id if sub_cat_id != '0' else None,
                                   offering=not request.GET.get('looking', False))

    form = from_class(initial={'category': cat_id, 'sub_category': sub_cat_id})
    cont = {'form': form} # if cat.form_add else {}
    return render(request, 'ads/additional_fields.html', cont)


@csrf_exempt
def file_upload(request, ftype):
    response = {'OK': 0}
    if request.method == 'POST':
        print(request.FILES)
        print(request.POST)
        if ftype == 'video':
            form = VideoAttachmentForm(request.POST, request.FILES)

        else:  # image
            form = ImageAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            thumb = thumbnail_url(obj.file, 'photo') if ftype != 'video' else ""
            response = {'OK': 1, 'id': obj.id, 'url': thumb, 'name': re.sub("_[^_]*(?=\.[^\.]*$)", "", basename(obj.file.name))}
        else:
            response['error'] = form.errors['file']
    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required
def paid_option(request, option_id, ad_id):
    option = PaidOption.objects.get(pk=option_id)
    ad = Ad.objects.get(pk=ad_id)
    is_available = option.is_available(request.user.score)

    if is_available:
        if request.method == 'POST':
            if option.uid == 'premium_status':
                ad.set_premium(option.duration)
            elif option.uid == 'vip_status':
                ad.set_vip(option.duration)
            else:
                return redirect(ad.get_absolute_url())
            ad.save()
            request.user.score -= option.cost
            request.user.save()
            return redirect(ad.get_absolute_url())
    else:
        messages.error(request, 'You have not enough money on your balance.')

    return render(request, 'ads/paid_option.html', {'option': option, 'ad': ad, 'is_available': is_available,
                                                    'referer': (_('Search'), "search", "search")})


@login_required
def profile(request):
    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile info was saved.'))
    else:
        form = forms.UserForm(instance=request.user)
    return render(request, 'ads/profile.html', {'form': form, 'type': 'info'})


@login_required
def profile_ads(request, page):
    if request.method == 'POST':
        pid = disable = None
        if 'disable' in request.POST:
            disable = True
            pid = request.POST['disable']
        elif 'restore' in request.POST:
            disable = False
            pid = request.POST['restore']
        if pid is not None:
            ad = Ad.objects.get(pk=pid)
            if ad.user == request.user:
                ad.disabled = disable
                ad.save()
                messages.success(request, _('Your add was successfully disabled.') if disable else _('Your add was successfully enabled.'))
    return render(request, 'ads/profile_ads.html', {'page': Paginator(request.user.ad_set.all(), 10).page(page or 1),
                                                    'page_num': page, 'type': 'ads_list'})


@login_required
def profile_visits(request, page):
    if 'history' in request.session and request.session['history']:
        ads = Ad.objects.filter(pk__in=request.session['history'])
        for ad in ads:
            visit, created = VisitHistory.objects.get_or_create(ad=ad, user=request.user)
        request.session['history'] = []
        request.session.modified = True
    page = page or 1
    objects = VisitHistory.objects.filter(user=request.user)
    return render(request, 'ads/profile_visits.html', {'page': Paginator(objects, 10).page(page),
                                                       'page_num': page, 'type': 'visits'})


def ajax_task_state(request):
    from celery.result import AsyncResult
    result = AsyncResult(request.GET.get('task_id'))
    return HttpResponse(json.dumps({'status': result.status, 'ready': result.ready(),
                                    'result': result.result, 'state': result.state}), content_type="application/json")


def error404(request):
    return render(request, 'errors/404.html', {'body_cls': 'errorPage'})


def error500(request):
    return render(request, 'errors/500.html', {'body_cls': 'errorPage'})



import locale
import sys

def view_locale(request):
    loc_info = "getlocale: " + str(locale.getlocale()) + \
        "<br/>getdefaultlocale(): " + str(locale.getdefaultlocale()) + \
        "<br/>fs_encoding: " + str(sys.getfilesystemencoding()) + \
        "<br/>sys default encoding: " + str(sys.getdefaultencoding()) + \
        "<br/>sys default encoding: " + str(sys.getdefaultencoding())
    return HttpResponse(loc_info)

