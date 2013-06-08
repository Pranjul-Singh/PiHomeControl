import logging



isDoorOpen = False

def doorCallback(gpio_id, val):
    global isDoorOpen
    if val == 1:
        isDoorOpen = True
        print "Door Opened"
    else:
        isDoorOpen = False 
        print "Door Closed"

try:
    import RPIO
    RPIO.setwarnings(False)
    RPIO.setup(24, RPIO.OUT)
    RPIO.output(24, True)
    print "Starting Door Watcher"
    RPIO.add_interrupt_callback(23, doorCallback, pull_up_down=RPIO.PUD_UP, threaded_callback=True)
    print "Door Watcher Running"
    RPIO.wait_for_interrupts()
except:
    print "Error occured"