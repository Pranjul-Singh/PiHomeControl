from subprocess import Popen, PIPE
import json

try:
	output = Popen(['lynx', '-source', 'https://www.google.com/voice/request/unread'], stdout=PIPE)
	p = output.stdout.read()
	print "completed"
	print p
except Exception, e:
	print "error"
	print str(e)