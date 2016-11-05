from django.db import models


class Category(models.Model):

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='products')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

