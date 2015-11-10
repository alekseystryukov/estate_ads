#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import pymorphy2
import re
import string


class RudeWord(models.Model):

    id = models.CharField(max_length=50, primary_key=True)
    word = models.CharField(max_length=50)
    strong = models.BooleanField(default=False)

    def __unicode__(self):
        return self.id

    def save(self, **kwargs):
        self.word = self.word.strip()
        self.id = WordAnalyser.top_normal(self.word)
        if not RudeWord.objects.filter(pk=self.id).exists():
            super(RudeWord, self).save(**kwargs)

    def search(self, text):
        pass


class WordAnalyser():

    morph = pymorphy2.MorphAnalyzer()
    punctuation = set(string.punctuation)

    def __init__(self,  *args, **kwargs):
        pass

    @classmethod
    def first_normal(cls, word):
        result = cls.morph.parse(word)
        # Get first word of set
        result = result.pop()
        #print(result.score)
        return result.normal_form

    @classmethod
    def top_normal(cls, word):
        result = cls.morph.parse(word)
        # Get variant with top score
        top_norm = None
        for res in result:
            if top_norm is None or res.score > top_norm.score:
                top_norm = res
        return top_norm.normal_form

    @classmethod
    def block_object(cls, obj, fields):
        if type(fields) in (str, unicode):
            fields = [fields]

        haystack = u''
        for field in fields:
            try:
                value = getattr(obj, field)
            except AttributeError:
                print("Warning:'%s' hasn't attribute '%s'" % (str(obj), field))
            else:
                haystack += u" " + value
        rude_ws = cls.get_rude_words(haystack)
        if rude_ws:
            obj.rude_words = rude_ws
            for word in rude_ws:
                if word.strong:
                    return True
            return None
        return False

    @classmethod
    def get_rude_words(cls, haystack):
        haystack = ''.join(ch for ch in haystack if ch not in cls.punctuation)
        word_list = list(set(haystack.split()))  # unique words
        word_list = filter(lambda wr: not wr.isnumeric(), word_list)  # not numeric

        normals = []
        for w in word_list:
            normals.append(cls.top_normal(w))
        # for n in normals:
        #     print(n)
        return RudeWord.objects.all().filter(pk__in=normals)

