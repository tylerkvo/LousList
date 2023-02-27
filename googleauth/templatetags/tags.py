from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

#register custom filter
@register.filter
def get_item(dictionary, key): #method to index into dict
    return dictionary.get(key)

@register.filter
def index(l, i): #method to index into list
    return l[i]

@register.simple_tag
def changeStatement(status):
    return not status

@register.simple_tag
def define(val=None):
  return val


@register.filter
@stringfilter
def convert_time(time): #method to convert luther's list time format to traditional hh:mm format
    x = time.split('.')
    ampm = "am"
    if x[0] != "":
        if int(x[0]) > 12: #if past 12 then we need to modulus by 12 to get pm time
            x[0] = int(x[0]) % 12
            ampm = "pm"
        elif int(x[0]) == 12: #handle case of noon (pm but no modulus)
            ampm = "pm"
        return str(x[0]) + ":" + str(x[1]) + ampm
    return time