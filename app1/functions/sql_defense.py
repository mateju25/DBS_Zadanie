import re


# ak je string zo spravnymi znakmi vrati ho, inak vrati None
def is_string(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("(.*[\"'#=].*)|(.*-{2}.*)")
    if prog.match(pa_string):
        return None
    else:
        return pa_string


# ak je string zo spravnymi znakmi vrati ho skonvertovany na cislo, inak vrati None
def is_number(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9]+$")
    if prog.match(pa_string):
        return int(pa_string)
    else:
        return None
