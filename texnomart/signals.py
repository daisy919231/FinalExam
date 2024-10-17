from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
import json 
import os 
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.forms.models import model_to_dict

from texnomart.models import Product, Category
from django.dispatch import receiver
from config.settings import EMAIL_DEFAULT_SENDER
from django.contrib.auth import User
from django.core.mail import send_mail


@receiver(post_save, sender=Product)
def send_creation_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'New Product Notification'
        message = 'A new product has been added.'
        from_email = EMAIL_DEFAULT_SENDER
        recipient_list = [user.email for user in User.objects.all()]

        send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Category)
def send_creation_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'New category Notification'
        message = 'A new category has been added.'
        from_email = EMAIL_DEFAULT_SENDER
        recipient_list = [user.email for user in User.objects.all()]

        send_mail(subject, message, from_email, recipient_list)


### FOR PRODUCT ###
@receiver(pre_delete, sender=Product)
def send_deletion_notification(sender, instance, **kwargs):
    fixture_path = Path(os.path.join(settings.BASE_DIR, "texnomart", "product_data", "products_deleted.json"))
    
    # Convert category to a dictionary
    category_instance = model_to_dict(instance.category) if instance.category else {}
    
    data = {
        'id': instance.id,
        'name': instance.name,
        'description': instance.description,
        'price': instance.price,
        'category': category_instance,
        'discount': instance.discount,
        'quantity': instance.quantity,
        'slug': instance.slug
    }

    with open(fixture_path, 'a+') as f:
        if fixture_path.suffix == ".json":
           
            json.dump(data, f, indent=4)
            f.write(",\n")  

            subject = 'Another product Notification'
            message = 'Another product has been deleted.'
            from_email = EMAIL_DEFAULT_SENDER
            recipient_list = [user.email for user in User.objects.all()]

            send_mail(subject, message, from_email, recipient_list)
        else:
            f.seek(0)  
            fixture = f.read()
    
    return None 


# FOR CATEGORY

@receiver(pre_delete, sender=Category)
def send_deletion_notification(sender, instance, **kwargs):
    fixture_path = Path(os.path.join(settings.BASE_DIR, "texnomart", "category_data", "categories_deleted.json"))
    
    # Convert category to a dictionary
    # category_instance = model_to_dict(instance.category) if instance.category else {}
    
    data = {
        'id': instance.id,
        'title': instance.title,
        'slug': instance.slug
    }

    with open(fixture_path, 'a+') as f:
        if fixture_path.suffix == ".json":
           
            json.dump(data, f, indent=4)
            f.write(",\n")  

            subject = 'Another product category Notification'
            message = 'Another product category has been deleted.'
            from_email = EMAIL_DEFAULT_SENDER
            recipient_list = [user.email for user in User.objects.all()]

            send_mail(subject, message, from_email, recipient_list)
        else:
            f.seek(0)  
            fixture = f.read()
    
    return None 