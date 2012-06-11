
def photo_post_save(instance, **kwargs):
    album = instance.album
    images = album.photos.all().values_list('image', flat=True)
    album.cover_url = instance.image_small_url
    album.count = len(images)
    album.save()

def photo_post_delete(instance, **kwargs):
    album = instance.album
    AlbumClass = type(album)
    try:
        AlbumClass.objects.get(id=album.id)
    except AlbumClass.DoesNotExist:
        return
    images = album.photos.all().values_list('image', flat=True)
    album.cover_url = instance.image_small_url
    album.count = len(images)
    album.save()

def photo_album_post_delete(instance, **kwargs):
    handler = instance.handler()
    handler.delete_path()
