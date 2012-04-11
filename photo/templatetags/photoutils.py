from django import template

register = template.Library()

@register.simple_tag()
def img_url(photo, size='list_triplet'):
    url = photo.image_url(size)
    if not url:
        url = photo.image_url(size='list_triplet')
    return url