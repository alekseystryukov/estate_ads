# coding=utf-8
import datetime
from haystack import indexes
from ads.models import Ad


class AdIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    #author = indexes.CharField(model_attr='user')
    title = indexes.CharField(model_attr='title')
    desc = indexes.CharField(model_attr='desc')
    private = indexes.BooleanField(model_attr='private')

    offering = indexes.BooleanField(model_attr='offering', default=True)
    disabled = indexes.BooleanField(model_attr='disabled', default=False)
    blocked = indexes.BooleanField(model_attr='blocked', default=False)

    order_date = indexes.DateTimeField(model_attr='order_date')
    town = indexes.IntegerField(model_attr='town_id')
    district = indexes.IntegerField(model_attr='district_id', null=True)
    category = indexes.IntegerField(model_attr='category_id')
    sub_category = indexes.IntegerField(model_attr='sub_category_id', null=True)

    price = indexes.IntegerField(model_attr='price', null=True)
    area = indexes.IntegerField(model_attr='area', null=True)
    area_living = indexes.IntegerField(model_attr='area_living', null=True)
    floor = indexes.IntegerField(model_attr='floor', null=True)
    rooms_count = indexes.IntegerField(model_attr='rooms_count', null=True)

    # We add this for autocomplete.
    content_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return Ad

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(disabled=False, blocked=False)  # pub_date__lte=datetime.datetime.now(),

    def get_updated_field(self):
        return "mod_date"

   # def prepare_author(self, obj):
   #     return "%s <%s>" % (obj.user.get_full_name(), obj.user.email)
