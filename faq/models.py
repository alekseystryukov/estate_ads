from django.db import models

from easymode.i18n.decorators import I18n
# from django.utils.text import slugify
from slugify import slugify

@I18n('title', 'desc')
class FaqArticle(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, editable=False)
    desc = models.TextField('text')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    disabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title_ru)
        super(FaqArticle, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "FAQ article"
        verbose_name_plural = "FAQ articles"

    def __unicode__(self):
        return self.title
