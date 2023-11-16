"""hook_Controller controller."""
import json

from controller import Supervisor
from controller import Receiver

robot = Supervisor()

timestep = int(robot.getBasicTimeStep())


receiver_device = robot.getDevice('hookReceiver')
receiver_device.enable(timestep)


# koukku_node = robot.getFromDef('koukkuRobotti')


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
      elif ohje == 1:
            kelaa(1)
      elif ohje == 2:
            kelaa(2)

def kelaa(suunta):
      nykyinen_translation = translation_field.getSFVec3f()
      nykyinen_korkeus = height.getSFFloat()
      koukun_nykyinen_translation = hook_translation_field.getSFVec3f()
      arvo = 0.06
      if suunta == 1:
            nykyinen_translation[2] = nykyinen_translation[2] - arvo/2  #Z = - (vaijeri laskee)
            translation_field.setSFVec3f(nykyinen_translation)
            koukun_nykyinen_translation[2] = koukun_nykyinen_translation[2] - arvo  #siirretään myös koukkua
            hook_translation_field.setSFVec3f(koukun_nykyinen_translation)
            height.setSFFloat(nykyinen_korkeus+arvo)  #Height lisääntyy (vaijeri pitenee)
      if suunta == 2:
            nykyinen_translation[2] = nykyinen_translation[2] + arvo/2  #Z = + (vaijeri nousee)
            translation_field.setSFVec3f(nykyinen_translation)
            koukun_nykyinen_translation[2] = koukun_nykyinen_translation[2] + arvo  #siirretään myös koukkua
            hook_translation_field.setSFVec3f(koukun_nykyinen_translation)
            height.setSFFloat(nykyinen_korkeus-arvo)  #Height pienenee (vaijeri lyhenee)

while robot.step(timestep) != -1:
  while receiver_device.getQueueLength() > 0:
            data = receiver_device.getString()
            ohje = json.loads(data)
            receiver_device.nextPacket()
            hook_cmd(ohje["koukku_ohjaus"])