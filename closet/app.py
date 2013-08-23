#!/usr/bin/python

import os
import CloudLog
import ClosetDoor

def main():
    appName = "PiCloset"
    try:

      if os.getlogin() == "pi":
        log_file = "/home/pi/public_html/pi-automate.log"
      else:
        log_file = 'pi-automate.log'
      CloudLog.init(log_file)
      CloudLog.track(appName, "START")

      ip_address = "192.168.1.201"
      port = 9557
      closet_door = ClosetDoor.Monitor(ip_address, port)
      if closet_door.state == "READY":
        closet_door.run()


    except Exception, e:
      CloudLog.error("App", "System Error", e)
    finally:
      CloudLog.track(appName, "EXITED")


if __name__ == "__main__":
    main()
