import os.path

from django import template
register = template.Library()

@register.simple_tag
def define(val=None):
    return val

@register.filter(name='file_icon')
def file_icon(a):
    _filename, ext = os.path.splitext(a)
    if ext in ['.txt', '.tex']:
        return 'bi-file-earmark-text'

    return 'bi-file-earmark-text'

@register.filter(name='range_diff')
def range_diff(a,b):
    if a < b:
        return range(a,b)
    return range(b, a)

@register.filter(name='get_child_layer')
def get_child_layer(cols,idx):
    return_cols = []
    iter = idx + 1
    while iter < len(cols) and cols[iter].layer > cols[idx].layer:
        return_cols.append(cols[iter])
        iter += 1

    return return_cols

@register.filter(name='increase')
def increase(a):
    return int(a) + 1