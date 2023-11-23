"""hook_Controller controller."""
import json
import time

from controller import Supervisor
from controller import Receiver
from controller import Emitter

robot = Supervisor()

timestep = int(robot.getBasicTimeStep())

receiver_device = robot.getDevice('hookReceiver')
receiver_device.enable(timestep)

hookLidar = robot.getDevice('hookLidar')
hookLidar.setPosition(float('+inf'))
hookLidar.setVelocity(20.0)


emitter_device = robot.getDevice('hookEmitter')

ds1 = robot.getDevice('hookDs1')
ds2 = robot.getDevice('hookDs2')

ds1.enable(timestep)
ds2.enable(timestep)

# koukku_node = robot.getFromDef('koukkuRobotti')
go_time = 0

vaijeri = robot.getFromDef('vaijeri')
height = vaijeri.getField('height')

vaijeri_solid = robot.getFromDef('vaijeriSolid')
translation_field = vaijeri_solid.getField('translation')

hook_pose = robot.getFromDef('koukku')
hook_translation_field = hook_pose.getField('translation')
#0.14 = koukun vaijerin (sylinterin) minimi height eli kun se on yläasennossa
#5.3 on sit alaasento
# tee tänne rajaarvot tonne kelaa funktioon
height.setSFFloat(5.3) 

def hook_cmd(ohje):
      if ohje == 0:
            pass
      elif ohje == 1: # Alaspäin
            kelaa(1)
      elif ohje == 2: # Ylöspäin
            kelaa(2)

def kelaa(suunta):
      nykyinen_translation = translation_field.getSFVec3f()
      nykyinen_korkeus = height.getSFFloat()
      koukun_nykyinen_translation = hook_translation_field.getSFVec3f()
      arvo = 0.06
      if suunta == 1 and nykyinen_korkeus < 5.3:
            nykyinen_translation[2] = nykyinen_translation[2] - arvo/2  #Z = - (vaijeri laskee)
            translation_field.setSFVec3f(nykyinen_translation)
            koukun_nykyinen_translation[2] = koukun_nykyinen_translation[2] - arvo  #siirretään myös koukkua
            hook_translation_field.setSFVec3f(koukun_nykyinen_translation)
            height.setSFFloat(nykyinen_korkeus+arvo)  #Height lisääntyy (vaijeri pitenee)
      if suunta == 2 and nykyinen_korkeus > 0.14:
            nykyinen_translation[2] = nykyinen_translation[2] + arvo/2  #Z = + (vaijeri nousee)
            translation_field.setSFVec3f(nykyinen_translation)
            koukun_nykyinen_translation[2] = koukun_nykyinen_translation[2] + arvo  #siirretään myös koukkua
            hook_translation_field.setSFVec3f(koukun_nykyinen_translation)
            height.setSFFloat(nykyinen_korkeus-arvo)  #Height pienenee (vaijeri lyhenee)

while robot.step(timestep) != -1:
      if ds1.getValue() < 1000 or ds2.getValue() < 1000:
            # Pysähdy jos huomataan
            go_time = time.time() + 0.1
            message = {"halt": 1}
            emitter_device.send(json.dumps(message))
      elif go_time < time.time():
            # Saa liikkua automaatiolla
            message = {"halt": 0}
            emitter_device.send(json.dumps(message))
      
      while receiver_device.getQueueLength() > 0:
            data = receiver_device.getString()
            ohje = json.loads(data)
            receiver_device.nextPacket()
            hook_cmd(ohje["koukku_ohjaus"])