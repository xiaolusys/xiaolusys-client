# coding: utf8
from __future__ import absolute_import, unicode_literals


def decode(barcode):
    codes = [s for s in barcode.split('-') if s]
    return len(codes) > 1 and codes[0:2] or (codes[0], '')