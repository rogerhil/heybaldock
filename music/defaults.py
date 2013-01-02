# -*- coding: utf-8; Mode: Python -*-

from django.utils.translation import ugettext as _


class ChoicesBase:

    @classmethod
    def choices(cls):
        choices = [(getattr(cls, k), k.title()) for k in dir(cls)
                                                if not k.startswith('__')]
        return choices

    @classmethod
    def display(cls, t):
        return dict(cls.choices()).get(t)


class Tempo(ChoicesBase):
    adagio = 1
    andante = 2
    moderato = 3
    allegro = 4
    presto = 5


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

    @classmethod
    def major_choices(cls):
        return [(k, v) for k, v in self.choices() if cls.is_major(v)]

    @classmethod
    def minor_choices(cls):
        return [(k, v) for k, v in self.choices() if cls.is_minor(v)]

    @classmethod
    def is_minor(cls, note):
        return len(note) > 1 and note[1] == 'm'

    @classmethod
    def is_major(cls, note):
        return not cls.is_minor(note)
