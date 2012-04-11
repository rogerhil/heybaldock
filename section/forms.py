
from draft import forms
from section.models import Section

class SectionForm(forms.CmsForm):

    class Meta:
        model = Section
        fields = ('menu_title', 'title', 'description', 'content')

  