"""bridge_Controller controller."""
import json

# Ladataan hallikartta...
with open('hallikartta.json') as tiedosto:
    data = json.load(tiedosto)
    print(data["tp1"]["x"])
    
# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Keyboard
from controller import Emitter
from controller import Receiver

# create the Robot instance.
robot = Robot()
keyboard = Keyboard()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

keyboard.enable(timestep)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
emitter_device = robot.getDevice('bridgeEmitter')

receiver_device = robot.getDevice('bridgeReceiver')
receiver_device.enable(timestep)

bridgeMotorO = robot.getDevice('bridgeMotorO')
bridgeMotorV = robot.getDevice('bridgeMotorV')


bridgeMotorO.setPosition(float('+inf'))
bridgeMotorV.setPosition(float('+inf'))

bridgeMotorO.setVelocity(0.0)
bridgeMotorV.setVelocity(0.0)

ds1 = robot.getDevice('dsLaser1')
ds2 = robot.getDevice('dsLaser2')
ds1.enable(timestep)
ds2.enable(timestep)
y = 0
x = 0
mene = 0
bridgeBusy = 0
trolleyBusy = 0

#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
def trolley_cmd(key):
    if key == ord("A"):
        message = {'laite': -1, 'mene': 0}
        emitter_device.send(json.dumps(message))
    elif key == ord("D"):
        message = {'laite': -2, 'mene': 0}
        emitter_device.send(json.dumps(message))

def bridge_cmd(key):
    if key == ord("W"): 
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        print(val1,val2)
        if (val1 > val2-0.2):
            bridgeMotorO.setVelocity(10.0)
            bridgeMotorV.setVelocity(5.0)
        elif (val2 > val1-0.2):
            bridgeMotorO.setVelocity(5.0)
            bridgeMotorV.setVelocity(10.0)
        else:
            bridgeMotorO.setVelocity(10.0)
            bridgeMotorV.setVelocity(10.0)
    elif key == ord("S"): 
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        if (val1 < val2-0.2):
            bridgeMotorO.setVelocity(-10.0)
            bridgeMotorV.setVelocity(-5.0)
        elif (val2 < val1-0.2):
            bridgeMotorO.setVelocity(-5.0)
            bridgeMotorV.setVelocity(-10.0)
        else:
            bridgeMotorO.setVelocity(-10.0)
            bridgeMotorV.setVelocity(-10.0)

def bridge_automation(x,mene):
    val1 = ds1.getValue()
    val2 = ds2.getValue()
    print(val1)
    if (val1 + 0.1 > x and val1 < x):
        return 0
    elif (x < val1):
        if (val1 > val2-0.1):
            bridgeMotorO.setVelocity(10.0)
            bridgeMotorV.setVelocity(7.0)
        elif (val2 > val1-0.1):
            bridgeMotorO.setVelocity(7.0)
            bridgeMotorV.setVelocity(10.0)
        else:
            bridgeMotorO.setVelocity(10.0)
            bridgeMotorV.setVelocity(10.0)
        return mene
    elif (x > val1):
        if (val1 < val2-0.1):
            bridgeMotorO.setVelocity(-10.0)
            bridgeMotorV.setVelocity(-7.0)
        elif (val2 < val1-0.1):
            bridgeMotorO.setVelocity(-7.0)
            bridgeMotorV.setVelocity(-10.0)
        else:
            bridgeMotorO.setVelocity(-10.0)
            bridgeMotorV.setVelocity(-10.0)
        return mene

def trolley_automation(y):
    message = {"laite": 0,'mene': y}
    emitter_device.send(json.dumps(message))

def automatio(mene):
        match mene:
            case 0:
                return 0
            case 1:
                trolley_automation(data["tp1"]["y"])
                return bridge_automation(data["tp1"]["x"],mene)
            case 2:
                trolley_automation(data["tp2"]["y"])                
                return bridge_automation(data["tp2"]["x"],mene)
            case 3:
                trolley_automation(data["tp3"]["y"])
                return bridge_automation(data["tp3"]["x"],mene)
            case 4:
                trolley_automation(data["tp4"]["y"])
                return bridge_automation(data["tp4"]["x"],mene)       

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    key = keyboard.getKey()
    
    # trolleyn vastaus onko perillä työpisteessä
    while receiver_device.getQueueLength() > 0:
        data = receiver_device.getString()
        trolleyVastaus = json.loads(data)
        receiver_device.nextPacket()
        trolleyBusy = trolleyVastaus["valmis"]
            
    if key == ord("1"):
        mene = 1
        bridgeBusy = 1
        trolleyBusy = 1
    elif key == ord("2"):
        mene = 2
        bridgeBusy = 1
        trolleyBusy = 1
    elif key == ord("P"):
        mene = 0
        bridgeBusy = 0
        trolleyBusy = 0
    elif key == ord("W") or key == ord("S"):
        bridge_cmd(key)
    else :
        bridgeMotorO.setVelocity(0.0)
        bridgeMotorV.setVelocity(0.0)
        trolley_cmd(key)
    if (bridgeBusy == 0 and trolleyBusy == 0):
        mene = 0
        # ONGELMA ON VASTAUKSESSA NYT CHANNEL ON VÄÄRÄ, VAIHDA SE 2
    if (mene != 0): 
        bridgeBusy = automatio(mene)
        
# Enter here exit cleanup code.
