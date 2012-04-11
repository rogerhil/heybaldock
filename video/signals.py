
def video_post_save(instance, **kwargs):
    album = instance.album
    urls = album.videos.all().values_list('thumbnail_small', flat=True)
    if album.cover_url not in urls:
        album.cover_url = instance.thumbnail_small
    album.count = len(urls)
    album.save()