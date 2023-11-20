"""bridge_Controller controller."""
import json
# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Receiver
from controller import Emitter

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
receiver_device = robot.getDevice('trolleyReceiver')
receiver_device.enable(timestep)

from_hook_receiver_device = robot.getDevice('hook_to_trolley_receiver')
from_hook_receiver_device.enable(timestep)


emitter_device = robot.getDevice('trolleyEmitter')

trolleyMotorO = robot.getDevice('trolleyMotorO')
trolleyMotorO2 = robot.getDevice('trolleyMotorO2')
trolleyMotorV = robot.getDevice('trolleyMotorV')
trolleyMotorV2 = robot.getDevice('trolleyMotorV2')

trolleyMotorO.setPosition(float('+inf'))
trolleyMotorO2.setPosition(float('+inf'))
trolleyMotorV.setPosition(float('+inf'))
trolleyMotorV2.setPosition(float('+inf'))

trolleyMotorO.setVelocity(0.0)
trolleyMotorO2.setVelocity(0.0)
trolleyMotorV.setVelocity(0.0)
trolleyMotorV2.setVelocity(0.0)


ds1 = robot.getDevice('dsLaserTrolley1')
ds2 = robot.getDevice('dsLaserTrolley2')
ds1.enable(timestep)
ds2.enable(timestep)

y = 0
mene = 0
halt = 0

def trolley_cmd(ohje):
    if ohje == -1: # Trolleyn liikutus
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        if (val1 < val2-0.2):
            trolleyMotorO.setVelocity(-8.0)
            trolleyMotorO2.setVelocity(-8.0)
            trolleyMotorV.setVelocity(-10.0)
            trolleyMotorV2.setVelocity(-10.0)
        elif (val2 > val1-0.2):
            trolleyMotorO.setVelocity(-10.0)
            trolleyMotorO2.setVelocity(-10.0)
            trolleyMotorV.setVelocity(-8.0)
            trolleyMotorV2.setVelocity(-8.0)
        else:
            trolleyMotorO.setVelocity(-10.0)
            trolleyMotorO2.setVelocity(-10.0)
            trolleyMotorV.setVelocity(-10.0)
            trolleyMotorV2.setVelocity(-10.0)
    elif ohje == -2: # Trolleyn liikutus
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        print(val1,val2)
        if (val1 < val2-0.2):
            trolleyMotorO.setVelocity(8.0)
            trolleyMotorO2.setVelocity(8.0)
            trolleyMotorV.setVelocity(10.0)
            trolleyMotorV2.setVelocity(10.0)
        elif (val2 < val1-0.2):
            trolleyMotorO.setVelocity(10.0)
            trolleyMotorO2.setVelocity(10.0)
            trolleyMotorV.setVelocity(8.0)
            trolleyMotorV2.setVelocity(8.0)
        else:
            trolleyMotorO.setVelocity(10.0)
            trolleyMotorO2.setVelocity(10.0)
            trolleyMotorV.setVelocity(10.0)
            trolleyMotorV2.setVelocity(10.0)

def trolley_automation(y):
    val1 = ds1.getValue()
    val2 = ds2.getValue()
    print(val1)
    if (val1 + 0.1 > y and val1 < y):
        return 0
    elif (y < val1):
        if (val1 < val2-0.2):
            trolleyMotorO.setVelocity(8.0)
            trolleyMotorO2.setVelocity(8.0)
            trolleyMotorV.setVelocity(10.0)
            trolleyMotorV2.setVelocity(10.0)
        elif (val2 < val1-0.2):
            trolleyMotorO.setVelocity(10.0)
            trolleyMotorO2.setVelocity(10.0)
            trolleyMotorV.setVelocity(8.0)
            trolleyMotorV2.setVelocity(8.0)
        else:
            trolleyMotorO.setVelocity(10.0)
            trolleyMotorO2.setVelocity(10.0)
            trolleyMotorV.setVelocity(10.0)
            trolleyMotorV2.setVelocity(10.0)
        return y
    elif (y > val1):
        if (val1 < val2-0.2):
            trolleyMotorO.setVelocity(-8.0)
            trolleyMotorO2.setVelocity(-8.0)
            trolleyMotorV.setVelocity(-10.0)
            trolleyMotorV2.setVelocity(-10.0)
        elif (val2 > val1-0.2):
            trolleyMotorO.setVelocity(-10.0)
            trolleyMotorO2.setVelocity(-10.0)
            trolleyMotorV.setVelocity(-8.0)
            trolleyMotorV2.setVelocity(-8.0)
        else:
            trolleyMotorO.setVelocity(-10.0)
            trolleyMotorO2.setVelocity(-10.0)
            trolleyMotorV.setVelocity(-10.0)
            trolleyMotorV2.setVelocity(-10.0)
        return y

#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    trolleyMotorO.setVelocity(0.0)
    trolleyMotorO2.setVelocity(0.0)
    trolleyMotorV.setVelocity(0.0)
    trolleyMotorV2.setVelocity(0.0)
    
    while receiver_device.getQueueLength() > 0:
            data = receiver_device.getString()
            ohje = json.loads(data)
            receiver_device.nextPacket()
            trolley_cmd(ohje["laite"])
            y = ohje["mene"]

    while from_hook_receiver_device.getQueueLength() > 0:
            data2 = from_hook_receiver_device.getString()
            ohje2 = json.loads(data2)
            from_hook_receiver_device.nextPacket()
            halt = ohje2["halt"]
            
    if (y != 0 and halt < 1): 
        y = trolley_automation(y)
    
    # Lähetetään bridgelle ollaanko valmiina    
    message = {"valmis": y}
    emitter_device.send(json.dumps(message))