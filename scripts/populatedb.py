# -*- coding: utf-8; Mode: Python -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings

from section.forms import SectionForm
from event.forms import EventForm, LocationForm

user = User.objects.get(username='rogerhil')

SECTIONS = [
    ('Home', '', 1),
    ('Eventos', '{% upcoming_events %}<br/>{% event_history_button %}', 2),
    ('Fotos', '{% photo_albums %}', 3),
    ('Videos', '{% video_albums %}', 4),
    ('Contato', '{% contact_form %}', 5),
]

LOCATIONS = [
    (
        'Stonehenge Rock Bar',
        '',
        '30190062',
        'Rua Tupis',
        1448,
        '',
        'Barro Preto',
        'Belo Horizonte',
        'MG',
        'Brasil',
        123,
        123,
        [32713476, 92472020, 92815239]
    ),
    (
        'Taberna Della Pizza',
        '',
        '30140062',
        'Rua Timbiras',
        3352,
        '',
        'Barro Preto',
        'Belo Horizonte',
        'MG',
        'Brasil',
        123,
        123,
        [25141414]
    )
]
EVENTS = [
    (
        'Primeiro Show',
        'Show junto com a banda The Doors Cover',
        '',
        datetime(2011, 12, 10),
        datetime(2011, 12, 10),
        1
    ),
    (
        'Rock Solidário',
        'Show junto com mais 5 bandas: Seu Madruga, The Doors Cover, ...',
        '',
        datetime(2012, 01, 29),
        datetime(2012, 01, 29),
        1
    ),
    (
        'Aniversário do Waldemar',
        'Show junto com Alexander Voz e Violão',
        '',
        datetime(2012, 03, 11),
        datetime(2012, 03, 11),
        2
    ),
    (
        'Especial Beatles',
        'Show junto com mais 2 bandas: Anthology e 3 of us',
        '',
        datetime(2012, 04, 20),
        datetime(2012, 04, 20),
        1
    ),
]

def populate_sections():
    for section in SECTIONS:
        section, content, order = section
        data = {
            'menu_title': section,
            'title': '%s title' % section,
            'description': '%s description' % section,
            'content': content or ' ',
            'order': order
        }
        form = SectionForm(user=user, data=data)
        form.is_valid()
        form.instance.order = order
        form.save()
        form.instance.slug = section.replace(' ', '').lower()
        form.publish()

def populate_locations():
    for l in LOCATIONS:
        data = {
            'name': l[0],
            'description': l[1],
            'zipcode': l[2],
            'street': l[3],
            'number': l[4],
            'complement': l[5] or None,
            'district': l[6],
            'city': l[7],
            'state': l[8],
            'country': l[9],
            'latitude': l[10],
            'longitude': l[11],
        }
        for i, phone in enumerate(l[12]):
            data['phone%d' % (i + 1)] = phone
        form = LocationForm(user=user, data=data)
        print form.is_valid()
        print form.errors
        form.save()
        form.publish()

def populate_events():
    for e in EVENTS:
        data = {
            'name': e[0],
            'description': e[1],
            'content': e[2],
            'starts_at': e[3],
            'ends_at': e[4],
            'location': e[5]
        }
        form = EventForm(user=user, data=data)
        form.is_valid()
        form.save()
        form.publish()

populate_sections()
populate_locations()
populate_events()
