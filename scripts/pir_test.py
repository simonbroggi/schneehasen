import time
import RPi.GPIO as io

io.setmode(io.BCM)

pir_pin_1 = 23
pir_pin_2 = 24

io.setup(pir_pin_1, io.IN)
io.setup(pir_pin_2, io.IN)

def pir_callback(channel):
	if io.input(channel):
		print("PIR %i say's there's movement %f" %(channel, time.time()))
	else:
		print("PIR %i say's it's calm %f" %(channel, time.time()))


io.add_event_detect(pir_pin_1, io.BOTH, callback=pir_callback)
io.add_event_detect(pir_pin_2, io.BOTH, callback=pir_callback)

print("listening for pir input on pin %i and %i" % (pir_pin_1, pir_pin_2))

time.sleep(60)

print("that's it")

io.cleanup()