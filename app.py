#!/usr/bin/python

import os
import Cloud
import Config
import Keypad
import System
import CloudLog


def main():
    print "Homemade Pi"
    try:

      if os.getlogin() == "pi":
        log_file = "../public_html/pi-automate.log"
      else:
        log_file = 'pi-automate.log'
      CloudLog.init(log_file)
      CloudLog.log("App", "Start")
      CloudLog.track("APP", "STARTED")

      config = Config.Config()
      
      controller = System.Controller(config)
      cloud = Cloud.Manager(controller, config)
      Keypad.listen(controller)

    except Exception, e:
      CloudLog.error("App", "System Error", e)
    finally:
      CloudLog.log("App", "Exited.")
      CloudLog.track("APP", "EXITED")


if __name__ == "__main__":
    main()
