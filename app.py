#!/usr/bin/python

import os
import Cloud
import Config
import Keypad
import System
import CloudLog


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
      cloud = Cloud.Manager(controller, config)
      Keypad.listen(controller)

    except Exception, e:
      CloudLog.error("App", "System Error", e)
    finally:
      CloudLog.track(appName, "EXITED")


if __name__ == "__main__":
    main()
