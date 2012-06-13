from django.conf import settings

def content_draft_post_save(instance, **kwrags):
    ContentDraftClass = type(instance)
    qs = ContentDraftClass.objects.filter(content_type=instance.content_type,
                    object_id=instance.object_id).order_by('-content_date')
    result = qs[settings.MAX_DRAFTS_PER_OBJECT:]
    if result.count():
        ids = result.values_list('id', flat=True)
        ContentDraftClass.objects.filter(id__in=ids).delete()