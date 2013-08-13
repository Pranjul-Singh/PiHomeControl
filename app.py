#!/usr/bin/python

import os
import Cloud
import Config
import System
import CloudLog
import Door
import GVoice
import Keypad

def main():
    appName = "PiHomeControl"
    try:

      if os.getlogin() == "pi":
        log_file = "../public_html/pi-automate.log"
      else:
        log_file = 'pi-automate.log'
      CloudLog.init(log_file)
      CloudLog.track(appName, "START")

      config = Config.Config()
      
      controller = System.Controller(config)
      controller.addHandler(Cloud.Monitor)
      controller.addHandler(Door.Monitor)
      controller.addHandler(GVoice.Monitor)
      Keypad.listen(controller)

    except Exception, e:
      CloudLog.error("App", "System Error", e)
    finally:
      CloudLog.track(appName, "EXITED")


if __name__ == "__main__":
    main()
