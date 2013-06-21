import json
import logging
from subprocess import Popen, PIPE


def getMessageCount():
    try:
        output = Popen(['lynx', '-source', 'https://www.google.com/voice/request/unread'], stdout=PIPE)
        resp = output.stdout.read()
        data = json.loads(resp)
        return data
    except Exception, e:
        logging.error("Unable to get Google Voice message data: " + str(e) + "\n")
        return json.loads('{"error": "' + str(e) + '"}')
