from django.db import models

from django.utils.translation import ugettext_lazy as _


PRODUCT_TYPES = (
    ('s', 'Sellable'),
    ('r', 'Rentable'),
)


class Category(models.Model):

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    product_type = models.CharField(max_length=1, choices=PRODUCT_TYPES, default='s')

    def __str__(self):
        return self.name


class HowItWorks(models.Model):

    name = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('How it works')
        verbose_name_plural = _('How it works')

    def __str__(self):
        return self.name
