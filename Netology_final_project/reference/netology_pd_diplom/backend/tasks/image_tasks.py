from celery import shared_task
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

@shared_task
def generate_user_avatar_thumbnails(user_id):
    from backend.models.users import User
    user = User.objects.get(pk=user_id)
    if user.avatar:
        war = VersatileImageFieldWarmer(
            instance=user,
            image_attr='avatar',
            rendition_key_set='user_avatar',
            save=False
        )
        war.warm()

@shared_task
def generate_product_image_thumbnails(product_info_id):
    from backend.models.catalog import ProductInfo 
    pi = ProductInfo.objects.get(pk=product_info_id)
    if pi.image:
        war = VersatileImageFieldWarmer(
            instance=pi,
            image_attr='image',
            rendition_key_set='product_image',
            save=False
        )
        war.warm()