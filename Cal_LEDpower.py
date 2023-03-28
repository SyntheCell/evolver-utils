from socketIO_client import SocketIO, BaseNamespace
import asyncio
from threading import Thread
import time
import argparse

EVOLVER_IP = ''
EVOLVER_PORT = 8081
evolver_ns = None
socketIO = None

class EvolverNamespace(BaseNamespace):
    data = []
    counter = 0
    def on_connect(self, *args):
        print("Connected to eVOLVER as client")

    def on_disconnect(self, *args):
        print("Discconected from eVOLVER as client")

    def on_reconnect(self, *args):
        print("Reconnected to eVOLVER as client")

    def on_broadcast(self, data):
        self.data.append(data['config']['od_led'])
        self.counter += 1

def changeLedPower(ns, msg):
    evolver_ns.emit('command', msg, namespace = '/dpu-evolver')
    print("Led power changed. Waiting for server confirmation")
    start = ns.counter
    while start >= ns.counter:
        time.sleep(2)
    else:
        print("This is the new led power list:")
        print(ns.data[-1]['value'])

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def run_client():
    global evolver_ns, socketIO
    socketIO = SocketIO(EVOLVER_IP, EVOLVER_PORT)
    evolver_ns = socketIO.define(EvolverNamespace, '/dpu-evolver')
    socketIO.wait()

if __name__ == '__main__':

    def errorMessage():
        print(f"error: argument -p/--power: expected 1 or 16 arguments, not {l}.")
        print('Try one of the following:')
        print('1.- Single power: python Cal_LEDpower.py -a <evolver-ip> -p 2060')
        print("2.- List of 16 powers separated by spaces: python Cal_LEDpower.py -a <evolver-ip>  -p 2060 2062 ... 2060")
        exit()


    # Argument handling
    parser = argparse.ArgumentParser(description="Change power of eVOLVER LEDs.")
    parser.add_argument("-a", "--address", type=str, required=True, help="IP address of your eVOLVER.")
    parser.add_argument("-p", "--power", type=int, required=True, nargs='+', help="Single LED power, eg. 2060\n or List of 16 powers separated by spaces, eg. 2060 2062 ... 2068")

    args = parser.parse_args()

    led_pow = args.power
    EVOLVER_IP = args.address

    # Check number of powers and compile message for server
    l = len(args.power)
    if l == 1:
        msg = {'param': 'od_led', 'value': [f'{led_pow[0]}'] * 16, 'immediate': True}
    
    elif l == 16:
        msg = {'param': 'od_led', 'value': [str(x) for x in led_pow], 'immediate': True}

    else:
        errorMessage()

    try:
        new_loop = asyncio.new_event_loop()
        t = Thread(target = start_background_loop, args = (new_loop,))
        t.daemon = True
        t.start()
        new_loop.call_soon_threadsafe(run_client)
        time.sleep(1)
        if evolver_ns is None:
            print("Error connecting to eVOLVER. Please check eVOLVER IP address")
            exit()
        
        print("Starting custom function")
        changeLedPower(evolver_ns, msg)

    except KeyboardInterrupt:
        socketIO.disconnect()
        print("Keyboard interrupt...exiting")
