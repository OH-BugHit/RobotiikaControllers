"""hook_Controller controller."""

from controller import Robot


robot = Robot() 

timestep = int(robot.getBasicTimeStep())

#vaijeri_node = robot.getDevice('vaijeri')
#vaijeri = vaijeri_node.getValue("height")


while robot.step(timestep) != -1:
  #print(vaijeri)
  pass