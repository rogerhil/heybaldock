# -*- coding: utf-8; Mode: Python -*-

from django.utils.translation import ugettext as _


class ChoicesBase:

    @classmethod
    def choices(cls):
        exclude = ['choices', 'display']
        choices = [(getattr(cls, k), k.title()) for k in dir(cls)
                                                if not k.startswith('__') and
                                      not hasattr(getattr(cls, k), '__call__')]
        choices.sort(lambda a, b: 1 if a[0] > b[0] else -1)
        return choices

    @classmethod
    def display(cls, t):
        return dict(cls.choices()).get(t)

    @classmethod
    def length(cls):
        return len(cls.choices())


class Tempo:
    @classmethod
    def choices(cls):
        return [(i, i) for i in range(10, 241)]

    @classmethod
    def display(cls, t):
        return dict(cls.choices()).get(t)


class SongMode(ChoicesBase):
    slow = 1
    medium = 2
    fast = 3


class DocumentType(ChoicesBase):
    image = 1
    other = 2


class Rating(ChoicesBase):
    bad = 1
    regular = 2
    good = 3
    excelent = 4
    awesome = 5


class Tonality(ChoicesBase):
    # majors
    A = 'A'
    Bb = 'Bb'
    B = 'B'
    C = 'C'
    Csharp = 'C#'
    D = 'D'
    Dsharp = 'D#'
    E = 'E'
    F = 'F'
    Fsharp = 'F#'
    G = 'G'
    Gsharp = 'G#'
    # minors
    Am = 'Am'
    Bmb = 'Bmb'
    Bm = 'Bm'
    Cm = 'Cm'
    Cmsharp = 'Cm#'
    Dm = 'Dm'
    Dmsharp = 'Dm#'
    Em = 'Em'
    Fm = 'Fm'
    Fmsharp = 'Fm#'
    Gm = 'Gm'
    Gmsharp = 'Gm#'

    Atonal = 'Atonal'

    @classmethod
    def major_choices(cls):
        return [(k, v) for k, v in cls.choices() if cls.is_major(v)]

    @classmethod
    def minor_choices(cls):
        return [(k, v) for k, v in cls.choices() if cls.is_minor(v)]

    @classmethod
    def is_atonal(cls, note):
        return note == Tonality.Atonal

    @classmethod
    def is_minor(cls, note):
        return not cls.is_atonal(note) and len(note) > 1 and note[1] == 'm'

    @classmethod
    def is_major(cls, note):
        return not cls.is_atonal(note) and not cls.is_minor(note)

    @classmethod
    def tonality_type(cls, note):
        if cls.is_atonal(note):
            return 'atonal'
        elif cls.is_minor(note):
            return 'minor'
        elif cls.is_major(note):
            return 'major'

    @classmethod
    def html_display(cls, note, original=True):
        if not note:
            return ('<span class="tonality_undefined tonality_block">'
                    'N/A</span>')
        t = note
        ttype = cls.tonality_type(note)
        changed = "tonality_changed" if not original else ""
        args = (ttype, changed, t)
        return '<span class="tonality_%s tonality_block %s">%s</span>' % args
