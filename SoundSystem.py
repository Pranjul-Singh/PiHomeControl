import CloudLog
from subprocess import call

def play(file_name):
  try:
    if file_name is not None:
      cmd = "mplayer -ao alsa -really-quiet -noconsolecontrols "
      call(cmd+file_name, shell=True)
  except Exception, e:
    CloudLog.error("SoundSystem.Play", "Error playing sound", e)
