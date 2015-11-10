#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from django.forms import ModelForm, TextInput, Textarea, Select, CheckboxInput, RadioSelect, DateInput, HiddenInput, EmailInput
from ads.models import District, Town, Category, SubCategory, Ad, ImageAttachment, VideoAttachment, ComparedDistrict, ComparedCategory, ComparedPrivate, ComparedPriceNeg, ComparedOffering
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.safestring import mark_safe
from slugify import slugify


class FilterSearchForm(SearchForm):
    #private = forms.CharField(required=False)


    # offering = forms.ChoiceField(choices=[("", _("Looking for estate")), ("1", _("Offering estate"))],
    #                              widget=RadioSelect(attrs={}), initial="", required=False)

    def __init__(self, *args, **kwargs):
        self.hide_fields = []
        if 'hide_fields' in kwargs:
            self.hide_fields = kwargs.pop('hide_fields')

        super(FilterSearchForm, self).__init__(*args, **kwargs)

        self.fields['town'] = forms.ChoiceField(choices=[("", _("All cities"))] + [(town.id, town.name) for town in Town.objects.all()],
                                                initial="1", required=False)

        if 'offering' not in self.hide_fields:
            self.fields['offering'] = forms.ChoiceField(choices=[("", _("Looking for estate")), ("1", _("Offering estate"))],
                                                        widget=RadioSelect(attrs={}), initial="", required=False)
        if 'category' not in self.hide_fields:
            self.fields['category'] = forms.ChoiceField(required=False,
                                                        choices=[('', _('All categories'))]+[(cat.id, cat.name)
                                                                                             for cat in Category.objects.all()])
        if 'district' not in self.hide_fields:
            dist_choices = [('', _('All districts'))]
            if args and args[0].get('town'):
                dist_choices += [(dist.id, dist.name) for dist in District.objects.filter(town_id=args[0].get('town'))]

            self.fields['district'] = forms.ChoiceField(required=False, choices=dist_choices)

        if args and 'category' in args[0]:
            if args[0]['category']:
                sub_cats = SubCategory.objects.all().filter(category=args[0]['category'])
                if len(sub_cats):
                    self.fields['sub_category'] = forms.ChoiceField(required=False,
                                                                    choices=[('', _('All subcategories'))]+[(cat.id, cat.name)
                                                                                                            for cat in sub_cats])

    # def no_query_found(self):
    #     return self.searchqueryset.all()

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        # sqs = super(FilterSearchForm, self).search().order_by('-order_date')
        if not self.is_valid():
            return self.no_query_found()

        return Ad.search(self.cleaned_data).order_by('-order_date')


class PriceSearchForm(FilterSearchForm):
    price_from = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Price from")}))
    price_to = forms.IntegerField(required=False,  widget=forms.TextInput(attrs={'placeholder': _("Price to")}))


class RoomSearchForm(PriceSearchForm):
    rooms_count_from = forms.IntegerField(required=False,  widget=forms.TextInput(attrs={'placeholder': _("Rooms from")}))
    rooms_count_to = forms.IntegerField(required=False,  widget=forms.TextInput(attrs={'placeholder': _("Rooms to")}))


class HouseSearchForm(PriceSearchForm):
    area_from = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Area from")}))
    area_to = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Area to")}))


class ApartmentSearchForm(PriceSearchForm):
    # area_living_from = forms.IntegerField(required=False,  widget=forms.TextInput(attrs={'placeholder':
    #                                                                                      _("Area living from")}))
    # area_living_to = forms.IntegerField(required=False,  widget=forms.TextInput(attrs={'placeholder':
    #                                                                                    _("Area living to")}))
    rooms_count_from = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Rooms from")}))
    rooms_count_to = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Rooms to")}))
    floor_from = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Floor from")}))
    floor_to = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': _("Floor to")}))


def make_label_req(text):
    return mark_safe(ugettext(text) + "&nbsp;<em>*</em>")


class TestForm(ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'town', 'offering', 'category', 'desc', 'district', 'address', 'lat', 'lon', 'phone', 'private']
        labels = {
            'title': _('Ad Title'),
            'offering': _('You are'),
            'price_negotiated': _('Negotiated'),
            'private': _('I\'m owner'),
            'town': _('Town'),
            'district': _('District'),
            'desc': _('Description'),
            'category': _('Category'),
            'phone': _('Phone'),
            'address': _('Address'),
            'sub_category': _('Subcategory'),
            'price': _('Price'),
            'floor': _('Floor'),
            'floor_max': _('Total floors'),
            'rooms_count': _('Rooms count'),
            'area_living': _('Area living'),
            'area_kitchen': _('Area kitchen'),
            'area_land': _('Area land'),
            'area': _('Area'),
            'email': _('E-mail'),
            'distance': _('Distance'),
            'free_from': _('Free from')
        }


class AdForm(ModelForm):
    image = forms.ImageField(required=False)
    #  overwrite model objects
    required_for_users = ['sub_category', 'floor', 'floor_max', 'rooms_count', 'area_living',
                          'title',  'district', 'area_kitchen', 'area_land', 'area', 'free_from']

    def add_prefix(self, field_name):
        if field_name == 'image':
            field_name = 'images[]'  # to get many images for HTML4 upload
        return super(AdForm, self).add_prefix(field_name)


    class Meta:
        model = Ad
        fields = ['title', 'town', 'offering', 'category', 'desc', 'district', 'address', 'lat', 'lon', 'phone', 'private']
        labels = {
            'title': make_label_req('Ad Title'),
            'offering': _('You are'),
            'price_negotiated': _('Negotiated'),
            'private': _('I\'m owner'),
            'town': make_label_req('Town'),
            'district': make_label_req('District'),
            'desc': make_label_req('Description'),
            'category': make_label_req('Category'),
            'phone': _('Phone'),
            'address': _('Address'),
            'sub_category': make_label_req('Subcategory'),
            'price': _('Price'),
            'floor': make_label_req('Floor'),
            'floor_max': make_label_req('Total floors'),
            'rooms_count': make_label_req('Rooms count'),
            'area_living': make_label_req('Area living'),
            'area_kitchen': make_label_req('Area kitchen'),
            'area_land': make_label_req('Area land'),
            'area': make_label_req('Area'),
            'email': make_label_req('E-mail'),
            'distance': _('Distance'),
            'free_from': _('Free from')
        }
        error_messages = {
            'title': {
                'max_length': _("This title is too long."),
            },
        },
        widgets = {
            "title": TextInput(attrs={"class": ""}),
            "desc": Textarea(attrs={"class": "", "required": "required"}),
            "offering": RadioSelect(attrs={"class": ""}, choices=((False, _('Looking for estate')),
                                                                  (True, _('Offering estate')))),
            "town": Select(attrs={"class": "", "required": "required"}),
            "district": Select(attrs={"class": ""}),
            "address": TextInput(attrs={"class": "",
                                        "placeholder": _("Start typing address or place marker on a map")}),
            "lat": HiddenInput(),
            "lon": HiddenInput(),
            "category": Select(attrs={"class": "", "required": "required"}),
            "sub_category": Select(attrs={"class": "", "required": "required"}),

            "phone": TextInput(attrs={"class": ""}),
            "private": CheckboxInput(attrs={"class": ""}),
            "price_negotiated": CheckboxInput(attrs={"class": ""}),
            "price": TextInput(attrs={"class": "", "data-parsley-type": "number"}),
            "floor": TextInput(attrs={"class": "", "required": "required",
                                      "data-parsley-type": "integer"}),
            "floor_max": TextInput(attrs={"class": "", "required": "required",
                                          "data-parsley-type": "integer", "min": 1}),
            "rooms_count": TextInput(attrs={"class": "", "required": "required", "min": 1,
                                            "data-parsley-type": "integer",  "data-parsley-trigger": "change"}),
            "area_living": TextInput(attrs={"class": "", "required": "required",
                                              "data-parsley-type": "number"}),
            "area_kitchen": TextInput(attrs={"class": "", "required": "required",
                                             "data-parsley-type": "number"}),
            "area_land": TextInput(attrs={"class": "", "required": "required",
                                            "data-parsley-type": "number"}),
            "area": TextInput(attrs={"class": "", "required": "required",
                                       "data-parsley-type": "number"}),
            "distance": TextInput(attrs={"class": ""}),
            "free_from": HiddenInput(attrs={"class": ""}),
        }

    def __init__(self,  *args, **kwargs):
        kwargs.setdefault('label_suffix', '')

        anonym = kwargs.pop('anonym') if 'anonym' in kwargs else None

        offering = None
        if args and "offering" in args[0] and args[0]['offering']:
            offering = True if args[0]['offering'] == 'True' else False

        elif 'initial' in kwargs and 'offering' in kwargs['initial'] and kwargs['initial']['offering']:
            offering = kwargs['initial']['offering']
        elif 'instance' in kwargs and hasattr(kwargs['instance'], 'offering'):
            offering = kwargs['instance'].offering
        town_id = None
        if args and "town" in args[0] and args[0]['town']:
            town_id = args[0]['town']
        elif 'initial' in kwargs and 'town' in kwargs['initial'] and kwargs['initial']['town']:
            town_id = kwargs['initial']['town']
        elif 'instance' in kwargs and hasattr(kwargs['instance'], 'town'):
            town_id = kwargs['instance'].town_id

        super(AdForm, self).__init__(*args, **kwargs)  # populates the post

        for f_n in self.fields:
            if f_n == 'district' and offering is False or town_id is not None and District.objects.filter(town_id=town_id).count() == 0:
                continue  # if you are looking for estate, district field is not required
            if f_n in self.required_for_users:
                self.fields[f_n].required = True
                self.fields[f_n].widget.attrs['required'] = 'required'
        if anonym:
            self.fields['email'] = forms.EmailField(label=make_label_req("E-mail"),
                                                    widget=EmailInput(attrs={"class": "",
                                                                             "required": "required"}))

        self.fields['town'].queryset = Town.objects.all()
        self.fields['town'].empty_label = None
        self.fields['town'].initial = 1

        self.fields['district'].queryset = District.objects.filter(town_id=(town_id or 1))
        self.fields['district'].empty_label = _("Select")
        self.fields['category'].empty_label = _("Select")


        category_id = None
        if args and "category" in args[0] and args[0]['category']:
            category_id = args[0]['category']
        elif 'initial' in kwargs and 'category' in kwargs['initial'] and kwargs['initial']['category']:
            category_id = kwargs['initial']['category']
        elif 'instance' in kwargs and hasattr(kwargs['instance'], 'category'):
            category_id = kwargs['instance'].category.id

        if category_id is not None and 'sub_category' in self.fields:  # we shouldn't show empty subcategory select
            self.fields['sub_category'].queryset = SubCategory.objects.filter(category=category_id)
            self.fields['sub_category'].empty_label = _("Select")
            if self.fields['sub_category'].queryset.count() == 0:
                del self.fields['sub_category']

    def clean_email(self):
        try:
            user = get_user_model().objects.get(email=self.cleaned_data['email'])
            if user.banned:
                raise forms.ValidationError(_("This email address is banned!"))
        except get_user_model().DoesNotExist:
            pass
        return self.cleaned_data['email']

    def clean_title(self):
        if not slugify(self.cleaned_data['title']):
            raise forms.ValidationError(_("This field should contain letters!"))
        return self.cleaned_data['title']

#  forms for estate proposals
class AdFormPrice(AdForm):
    class Meta(AdForm.Meta):
        fields = AdForm.Meta.fields + ['price', 'price_negotiated', 'sub_category']


class AdFormApartment(AdForm):
    class Meta(AdForm.Meta):
        fields = AdFormPrice.Meta.fields + ['rooms_count', 'area_living', 'area_kitchen', 'area',
                                            'floor', 'floor_max', 'free_from']


class AdFormRoom(AdForm):
    class Meta(AdForm.Meta):
        fields = AdFormPrice.Meta.fields + ['rooms_count']


class AdFormHouse(AdForm):
    class Meta(AdForm.Meta):
        fields = AdFormPrice.Meta.fields + ['area', 'distance']


class AdFormLand(AdForm):
    class Meta(AdForm.Meta):
        fields = AdFormPrice.Meta.fields + ['area_land', 'distance']


class AdFormPremises(AdForm):
    class Meta(AdForm.Meta):
        fields = AdFormPrice.Meta.fields + ['area']

#  forms for looking estate,  offering == False
class AdLookingForm(AdForm):
    class Meta(AdForm.Meta):
        exclude = ['address']

class AdLookingFormMore(AdLookingForm):
    class Meta(AdForm.Meta):
        fields = AdLookingForm.Meta.fields + ['sub_category']





class ImageAttachmentForm(ModelForm):
    class Meta:
        model = ImageAttachment
        fields = ['file']


class VideoAttachmentForm(ModelForm):

    class Meta:
        model = VideoAttachment
        fields = ['file']


class UserForm(ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['name', 'phone', 'is_private']
        labels = {
            'name': _('Your name'),
            'phone': _('Your contact phone'),
            'is_private': _('I\'m a private person'),
        }
        widgets = {
            "name": TextInput(attrs={"class": "form-control"}),
            "phone": TextInput(attrs={"class": "form-control"}),
            "is_private": CheckboxInput(attrs={"class": "form-control"}),
        }


class SendToFriendForm(forms.Form):
    email = forms.EmailField(widget=EmailInput(attrs={"placeholder": _("E-mail")}))
    ad_id = forms.IntegerField(widget=HiddenInput())


class MatchFieldsForm(forms.Form):
    """
    Import CSV, stage 1
    """
    required = ['title', 'desc', 'district', 'category', 'price', 'pub_date', 'offering']


    def __init__(self, *args, **kwargs):
        f_headers = kwargs.pop('match_fields', [])
        super(MatchFieldsForm, self).__init__(*args, **kwargs)

        non_required = ['url', 'address', 'lat', 'lon', 'phone', 'private', 'price_negotiated', 'currency',
                        'rooms_count', 'area_living', 'area_kitchen', 'area', 'floor', 'floor_max', 'buildings_type',
                        'free_from', 'distance', 'area_land']
        all_fields = self.required + non_required
        # choices = (('---------', [('', _('Select'),)],),
        #            ('From file', [(index, header) for index, header in enumerate(f_headers)],),
        #            ('Constant values', [(f_field, f_field) for f_field in all_fields],))

        multi_choices = (('From file', [(index, header) for index, header in enumerate(f_headers)],),
                         ('Or', [("Constant", "Set Constant Value")],),)
        choices = (('---------', [('', _('Select'),)],),) + multi_choices

        initial_val = {'title': f_headers.index('Текст') if 'Текст' in f_headers else None,
                       'desc': [i for i, x in enumerate(f_headers) if x in ['Текст', 'Метро']],
                       'district': [i for i, x in enumerate(f_headers) if x in ['Нас.п.', 'Район']],
                       'category': 'Constant', 'private': 'Constant', 'offering': 'Constant',
                       'price': f_headers.index('Цена') if 'Цена' in f_headers else None,
                       'pub_date': f_headers.index('Дата') if 'Дата' in f_headers else None,
                       'url': f_headers.index('Ссылка') if 'Ссылка' in f_headers else None,
                       'address': f_headers.index('Улица') if 'Улица' in f_headers else None,
                       'phone': [i for i, x in enumerate(f_headers) if x == "Тел"],
                       'rooms_count': f_headers.index('Кол.комн.') if 'Кол.комн.' in f_headers else None,
                       'area_living': f_headers.index('Жил') if 'Жил' in f_headers else None,
                       'area_kitchen': f_headers.index('Кух') if 'Кух' in f_headers else None,
                       'area': f_headers.index('Общ') if 'Общ' in f_headers else None,
                       'floor': f_headers.index('Эт') if 'Эт' in f_headers else None,
                       'floor_max': f_headers.index('Этажн') if 'Этажн' in f_headers else None,
                       'area_land': f_headers.index('Пл.уч.') if 'Пл.уч.' in f_headers else None}
        for field in all_fields:
            # устанавливаем значения по умолчанию
            initial = initial_val.get(field)

            if field in ['phone', 'district', 'desc']:
                self.fields[field] = forms.MultipleChoiceField(choices=multi_choices,
                                                               initial=initial,
                                                               required=field in self.required)
            else:
                self.fields[field] = forms.ChoiceField(choices=choices, initial=initial,
                                                       required=field in self.required)



class CompareFieldsForm(forms.Form):
    """
    Import CSV, stage 2
    Matching imported and actual db-values (categories, districts, etc.)
    """
    compared_fields = {'district': {'choices': (('---------', [('', _('Select'),)],),),
                                    'model': ComparedDistrict, 'foreign': District},
                       'category': {'choices': [('', '--------')], 'model': ComparedCategory},
                       'private':  {'choices': [(False, _('No'),), (True, _('Yes'),)], 'model': ComparedPrivate},
                       'offering': {'choices': [(False, _('No'),), (True, _('Yes'),)], 'model': ComparedOffering},
                       'price_negotiated': {'choices': [(False, _('No'),), (True, _('Yes'),)],
                                            'model': ComparedPriceNeg} }

    def __init__(self, *args, **kwargs):
        field_names = kwargs.pop('compare_fields')
        current = kwargs.pop('current_field')

        for cat in Category.objects.all():
            self.compared_fields['category']['choices'].append((cat.id, cat.name))
            for sub_cat in SubCategory.objects.filter(category=cat):
                self. compared_fields['category']['choices'].append((str(cat.id)+'-'+str(sub_cat.id),
                                                                    u'-'.join((cat.name, sub_cat.name))))

        districts = tuple([town.name, [(town.id, town.name)] +
                          [(str(town.id) + '-' + str(dist.id), town.name+'/'+dist.name)
                           for dist in District.objects.all().filter(town=town)]] for town in Town.objects.all())
        self.compared_fields['district']['choices'] += districts


        super(CompareFieldsForm, self).__init__(*args, **kwargs)

        model = self.compared_fields[current]['model']
        in_values = dict((m.id, m) for m in model.objects.filter(pk__in=field_names[current]))
        i = 1
        #from ads.models import Town, District
        # town = Town.objects.get(pk=1)
        #districts = District.objects.all()

        for value in field_names[current]:
            # distict = District(town=town, name_en=value, name_uk=value, name_ru=value)
            # distict.save()
            label = value
            if value in in_values:
                if current == 'category':
                    obj = in_values[value]
                    if obj.category:
                        value = obj.category.id
                    elif obj.sub_category:
                        value = str(obj.sub_category.category.id) + '-' + str(obj.sub_category.id)
                elif current == 'district':
                    obj = in_values[value]
                    if obj.district:
                        value = str(obj.district.town.id)+'-'+str(obj.district.id)
                    else:
                        value = obj.town.id
                elif 'foreign' in self.compared_fields[current]:
                    value = in_values[value].value.id
                else:
                    value = in_values[value].value
            elif current == 'district':
                for town, dists in districts:
                    for dist in dists:
                        if town + ", " + dist[1] == value:
                            value = dist[0]

            self.fields[current+'_'+str(i)] = forms.ChoiceField(initial=value, required=True, label=label,
                                                                choices=self.compared_fields[current]['choices'])
            i += 1



    def is_valid(self):
        # run the parent validation first
        valid = super(CompareFieldsForm, self).is_valid()

        for name in self.cleaned_data:
            type_field = '_'.join(name.split('_')[0:-1])
            if type_field in self.compared_fields:
                model = self.compared_fields[type_field]['model']
                if type_field == 'category':
                    cat = sub_cat = None
                    cat_values = self.cleaned_data[name].split('-')
                    if len(cat_values) > 1:
                        sub_cat = SubCategory.objects.get(pk=cat_values[1])
                    else:
                        cat = Category.objects.get(pk=cat_values[0])
                    initial, created = model.objects.get_or_create(pk=self.fields[name].label,
                                                                   defaults={'category': cat, 'sub_category': sub_cat})
                    if not created and (initial.category != cat or initial.sub_category != sub_cat):
                        initial.category = cat
                        initial.sub_category = sub_cat
                        initial.save()

                elif type_field == 'district':
                    town = district = None
                    values = self.cleaned_data[name].split('-')
                    if len(values) > 1:
                        district = District.objects.get(pk=values[1])
                    else:
                        town = Town.objects.get(pk=values[0])
                    initial, created = model.objects.get_or_create(pk=self.fields[name].label,
                                                                   defaults={'town': town, 'district': district})
                    if not created and (initial.town != town or initial.district != district):
                        initial.town = town
                        initial.district = district
                        initial.save()

                else:
                    if 'foreign' in self.compared_fields[type_field]:
                        val = self.compared_fields[type_field]['foreign'].objects.get(pk=self.cleaned_data[name])
                    else:
                        val = self.cleaned_data[name]
                    if type_field in ['price_negotiated', 'private']:  # boolean
                        val = True if str(val) == 'True' else False

                    initial, created = model.objects.get_or_create(pk=self.fields[name].label, defaults={'value': val})
                    if not created and initial.value != val:
                        initial.value = val
                        initial.save()

        return valid


class SetConstantValueForm(forms.Form):
    """
    Import CSV, stage 3
    For some fields we can specify one value for all imported entries
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('matching')
        super(SetConstantValueForm, self).__init__(*args, **kwargs)

        for field in fields:
            if fields[field] == 'Constant' or 'Constant' in fields[field]:
                if field in CompareFieldsForm.compared_fields:
                    self.fields[field] = forms.ChoiceField(required=True, label=field,
                                                           choices=CompareFieldsForm.compared_fields[field]['choices'])
                else:
                    self.fields[field] = forms.CharField(required=True, label=field)

