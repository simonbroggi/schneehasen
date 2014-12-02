import time
import RPi.GPIO as io

relais = [7, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38]

io.setmode(io.BOARD)

print('testing relais ' + relais)

#for r in relais:
#    print('setting %i' %r)
#    io.setup(r, io.OUT)
io.setup(relais, io.OUT, initial=False)

# loop through all of them
rON = relais[0]
for r in relais:
    io.output(rON, False)
    rON = r
    io.output(r, True)
    time.sleep(1)

io.cleanup()
print('byebye')
