from django.db import models


class Types(models.Model):
    type = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'value'], name='unique type-value')
        ]


class Estate(models.Model):
    address = models.CharField(max_length=255)
    bathrooms = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='bathrooms', blank=True)
    bedrooms = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='bedrooms', blank=True)
    created_at = models.DateTimeField("Creation Date", auto_now=True)
    price = models.IntegerField()
    verified = models.BooleanField()
    type = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='estate_type', blank=True)
    price_duration = models.CharField(max_length=255)
    size = models.IntegerField()
    furnished = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='furnished', blank=True)
    description = models.TextField()
    title = models.CharField(max_length=255)
    city = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='city', blank=True)
    category = models.ForeignKey(
        Types, on_delete=models.SET_NULL, null=True, related_name='estate_category', blank=True)
