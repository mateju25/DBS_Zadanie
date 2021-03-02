import re


# ak je string zo spravnymi znakmi vrati ho, inak vrati None
def is_string(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9a-zA-Z_., :-]+$")
    if prog.match(pa_string):
        return pa_string
    else:
        return None


# ak je string zo spravnymi znakmi vrati ho skonvertovany na cislo, inak vrati None
def is_number(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9]+$")
    if prog.match(pa_string):
        return int(pa_string)
    else:
        return None
