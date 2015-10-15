from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
# Create your models here.

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class SongDetail(models.Model):
    song_id = models.IntegerField("Song ID", blank=False, null=False )
    title = models.CharField("Title", max_length=255, blank=False, null=False)
    description = models.TextField("Description", max_length=1000, blank=False, null=False)
    url = models.URLField("URL", max_length=255, blank=False, null=False)
    creation_date = models.DateTimeField("Creation Date", blank=False, null=False, auto_now_add=True)
    modificaion_date = models.DateTimeField("Modification Date", blank=False, null=False, auto_now=True)