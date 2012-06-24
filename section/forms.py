from draft import forms
from section.models import Section

class SectionForm(forms.CmsForm):

    class Meta:
        model = Section
        fields = ('menu_title', 'title', 'description', 'content')

    def __init__(self, *args, **kwargs):
        super(SectionForm, self).__init__(*args, **kwargs)
        self.instance.user_updated = self.user
