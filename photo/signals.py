
def photo_post_save(instance, **kwargs):
    album = instance.album
    images = album.photos.all().values_list('image', flat=True)
    album.cover_url = instance.image_small_url
    album.count = len(images)
    album.save()