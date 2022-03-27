from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(**kwargs):
    if kwargs['created']:
        user = kwargs['instance']
        customer = Group.objects.get(name__exact='Пользователь')
        customer.user_set.add(user)
        Profile.objects.create(
            user=user,
            role=customer
        )
