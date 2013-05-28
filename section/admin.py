# -*- coding: utf-8; Mode: Python -*-

from django.contrib import admin

from section.models import Section


class SectionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Section, SectionAdmin)
