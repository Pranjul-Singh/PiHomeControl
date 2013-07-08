from subprocess import call

def _say(speech):
    cmd = "mplayer -ao alsa -really-quiet -noconsolecontrols "
    url = '"http://translate.google.com/translate_tts?tl=en&q=' + speech + '"'
    call(cmd+url, shell=True)



def welcomeHome():
    _say("Hello Sir, welcome home.")


def away():
    _say("Armed. Away. Exit now.")


def goodNight():
    _say("Good night. Sleep well.")


def ready():
    _say("Number five, is alive!")