"""bridge_Controller controller."""
import json

from queue import Queue

kutsu_jono = Queue()
kutsu_setti = set()

# Ladataan hallikartta...
with open('hallikartta.json') as tiedosto:
    data = json.load(tiedosto)
    print("Testataan tiedoston latausta hakemalla arvo tp1, x... :", data["tp1"]["x"])
    
# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Keyboard
from controller import Emitter
from controller import Receiver
from controller import Supervisor

# create the Robot instance.
robot = Supervisor()
keyboard = Keyboard()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep()) # Default 32, nyt 24

keyboard.enable(timestep)

emitter_device = robot.getDevice('bridgeEmitter')
to_hook_emitter_device = robot.getDevice('bridge_to_hook_emitter')

receiver_device = robot.getDevice('from_hook_receiver')
receiver_device.enable(timestep)

from_trolley_receiver = robot.getDevice('from_trolley_receiver')
from_trolley_receiver.enable(timestep)

#Työpisteiden kutsuttu-valo
tyovalo1 = robot.getFromDef('tyovalo1')
tyovalo2 = robot.getFromDef('tyovalo2')
tyovalo3 = robot.getFromDef('tyovalo3')
tyovalo4 = robot.getFromDef('tyovalo4')
tyovalo5 = robot.getFromDef('tyovalo5')
tyovalo6 = robot.getFromDef('tyovalo6')
tyovalo7 = robot.getFromDef('tyovalo7')
tyovalo8 = robot.getFromDef('tyovalo8')
tyovalo9 = robot.getFromDef('tyovalo9')
tyovaloV = robot.getFromDef('tyovalo_vapaa')
tv1Valo = tyovalo1.getField('on')
tv2Valo = tyovalo2.getField('on')
tv3Valo = tyovalo3.getField('on')
tv4Valo = tyovalo4.getField('on')
tv5Valo = tyovalo5.getField('on')
tv6Valo = tyovalo6.getField('on')
tv7Valo = tyovalo7.getField('on')
tv8Valo = tyovalo8.getField('on')
tv9Valo = tyovalo9.getField('on')
tvVihrValo = tyovaloV.getField('on')

def nollaa_valot(): # Kutsuvalojen lähtötilanne kun jono tyhjä
    tv1Valo.setSFBool(False)
    tv2Valo.setSFBool(False)
    tv3Valo.setSFBool(False)
    tv4Valo.setSFBool(False)
    tv5Valo.setSFBool(False)
    tv6Valo.setSFBool(False)
    tv7Valo.setSFBool(False)
    tv8Valo.setSFBool(False)
    tv9Valo.setSFBool(False)
    tvVihrValo.setSFBool(True)

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
halt = 0
mene = 0
bridgeBusy = 0
trolleyBusy = 0
kaytossa = 0
tallennus = 0
trolley_sijainti = 0
perilla = True
nollaa_valot()

# Funktiot
def tallenna(tyopiste,x,y):
    tp = "tp"+str(tyopiste)
# 194 on max value ettei törmää bridgeen 13.7: #
    if y < 13.71:
        y = 13.75
    if y > 193.99:
        y = 193.25
    if x < 4.62:
        x = 4.8
    if x > 194.7:
        x = 193.9
    data[tp]["x"] = x
    data[tp]["y"] = y
    with open("hallikartta.json", "w") as kirjoitettava:
        json.dump(data, kirjoitettava)
    print("tallennettu työpiste", tp, " X:", data[tp]["x"], " Y: ", data[tp],["y"])

def trolley_cmd(key):
    if key == ord("A"): # trolley 'vasen'
        message = {'laite': -1, 'mene': 0}
        emitter_device.send(json.dumps(message))
    elif key == ord("D"): # trolley 'oikea'
        message = {'laite': -2, 'mene': 0}
        emitter_device.send(json.dumps(message))
    elif key == ord("F"): #Kaapeli sisään
        message = {'laite': -3, 'mene': 0}
        emitter_device.send(json.dumps(message))
    elif key == ord("V"): #Kaapeli ulos
        message = {'laite': -4, 'mene': 0}
        emitter_device.send(json.dumps(message))

def bridge_cmd(key):
    if key == ord("W"): # Bridge 'eteen'
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        print(val1)
        if val1 > 4.62: # Kiskon pää
            if (val1 > val2-0.2):
                bridgeMotorO.setVelocity(10.0)
                bridgeMotorV.setVelocity(5.0)
            elif (val2 > val1-0.2):
                bridgeMotorO.setVelocity(5.0)
                bridgeMotorV.setVelocity(10.0)
            else:
                bridgeMotorO.setVelocity(10.0)
                bridgeMotorV.setVelocity(10.0)
        else:
            bridgeMotorO.setVelocity(0.0)
            bridgeMotorV.setVelocity(0.0)
    elif key == ord("S"): # Bridge 'taakse'
        val1 = ds1.getValue()
        val2 = ds2.getValue()
        if val1 < 194.7: # Kiskon pää
            if (val1 < val2-0.2):
                bridgeMotorO.setVelocity(-10.0)
                bridgeMotorV.setVelocity(-5.0)
            elif (val2 < val1-0.2):
                bridgeMotorO.setVelocity(-5.0)
                bridgeMotorV.setVelocity(-10.0)
            else:
                bridgeMotorO.setVelocity(-10.0)
                bridgeMotorV.setVelocity(-10.0)
        else:
            bridgeMotorO.setVelocity(0.0)
            bridgeMotorV.setVelocity(0.0)

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

def automaatio(mene, kaytossa):
    if kaytossa == 0:
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
            case 5:
                trolley_automation(data["tp5"]["y"])
                return bridge_automation(data["tp5"]["x"],mene)
            case 6:
                trolley_automation(data["tp6"]["y"])                
                return bridge_automation(data["tp6"]["x"],mene)
            case 7:
                trolley_automation(data["tp7"]["y"])
                return bridge_automation(data["tp7"]["x"],mene)
            case 8:
                trolley_automation(data["tp8"]["y"])
                return bridge_automation(data["tp8"]["x"],mene)
            case 9:
                trolley_automation(data["tp9"]["y"])
                return bridge_automation(data["tp9"]["x"],mene)

def lisaa_jonoon(tyopiste): # Asetetaan jonoon työpisteen tarve nosturista
    tvVihrValo.setSFBool(False)
    if tyopiste not in kutsu_setti:
        kutsu_jono.put(tyopiste)
        kutsu_setti.add(tyopiste)

def ota_jonosta(): # Otetaan kutsujonosta seuraava työpiste
    if kutsu_jono.empty():
        tvVihrValo.setSFBool(True)
        return 0 # palauttaa 0 kun jono tyhjä. (Mene = 0)
    
    seuraava = kutsu_jono.get()
    kutsu_setti.remove(seuraava)
    match seuraava:
        case 1:
            tv1Valo.setSFBool(False)
        case 2:
            tv2Valo.setSFBool(False)
        case 3:
            tv3Valo.setSFBool(False)
        case 4:
            tv4Valo.setSFBool(False)
        case 5:
            tv5Valo.setSFBool(False)
        case 6:
            tv6Valo.setSFBool(False)
        case 7:
            tv7Valo.setSFBool(False)
        case 8:
            tv8Valo.setSFBool(False)
        case 9:
            tv9Valo.setSFBool(False)
    return seuraava

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Otetaan vastaan koukun emitterin arvo
    
    while from_trolley_receiver.getQueueLength() > 0: # Vastaanotetaan trolleyltä sijainti (y)
            from_trolley_data = from_trolley_receiver.getString()
            trolley_data = json.loads(from_trolley_data)
            from_trolley_receiver.nextPacket()
            trolley_sijainti = trolley_data["sijainti"]    
    
    while receiver_device.getQueueLength() > 0: # Vastaanotetaan koukulta tietoa esteistä (pyynnöstä pysähtyä)
            vastaanotettuData = receiver_device.getString()
            haltOhjaus = json.loads(vastaanotettuData)
            receiver_device.nextPacket()
            halt = haltOhjaus["halt"]
    # Tarkistetaan näppäimistösyöte
    key = keyboard.getKey()

    if key == ord("T"): # Työkutsujonon printti
        print("Työkutsujonossa seuraavat työpisteet (ei järjestyksessä): ", kutsu_setti)
    if key == ord("O"): # Tallenna uusi työpiste painamalla tämän jälkeen sitten työpisteen numeroa
        if tallennus == 0:
            print("\nTallenna työpiste painamalla haluttua numeroa...\nTai paina \"L\" poistuaksesi")
            tallennus = 1
    if key == ord("L") and tallennus == 1: # Lopetetaan tallennus
        tallennus = 0
        print("\nPoistuit tallennustilasta\n")
    if key == ord("1"): #Työpiste 1
        if tallennus == 0:
            lisaa_jonoon(1)
            tv1Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 1")
            tallenna(1,ds1.getValue(),trolley_sijainti)
            tallennus = 0
    elif key == ord("2"): #Työpiste 2
        if tallennus == 0:
            lisaa_jonoon(2)
            tv2Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 2")
            tallenna(2, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("3"): #Työpiste 3
        if tallennus == 0:
            lisaa_jonoon(3)
            tv3Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 3")
            tallenna(3, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("4"): #Työpiste 4
        if tallennus == 0:
            lisaa_jonoon(4)
            tv4Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 4")
            tallenna(4, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("5"): #Työpiste 5
        if tallennus == 0:
            lisaa_jonoon(5)
            tv5Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 5")
            tallenna(5, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("6"): #Työpiste 6
        if tallennus == 0:
            lisaa_jonoon(6)
            tv6Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 6")
            tallenna(6, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("7"): #Työpiste 7
        if tallennus == 0:
            lisaa_jonoon(7)
            tv7Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 7")
            tallenna(7, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("8"): #Työpiste 8
        if tallennus == 0:
            lisaa_jonoon(8)
            tv8Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 8")
            tallenna(8, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("9"): #Työpiste 9
        if tallennus == 0:
            lisaa_jonoon(9)
            tv9Valo.setSFBool(True)
        else:
            print("Uusi sijainti tallennettu työpisteeseen 9")
            tallenna(9, ds1.getValue(), trolley_sijainti)
            tallennus = 0
    elif key == ord("P"): #Pysäytys!
        kutsu_jono = Queue() # Tyhjennetään jono ja setti
        kutsu_setti = set() # Odottamaton automaatio on estetty
        nollaa_valot()
        mene = 0
        trolley_automation(0)
        bridgeBusy = 0
        trolleyBusy = 0
    elif key == ord("W") or key == ord("S"): # Bridgen käsiohjaus
        bridge_cmd(key)
    else :
        bridgeMotorO.setVelocity(0.0)
        bridgeMotorV.setVelocity(0.0)
        trolley_cmd(key)
    if key == ord("R") and perilla: # Vapauta (release), työpisteen käytöltä mahdollisille seuraaville
        kaytossa = 0

    if (bridgeBusy == 0):
        if kaytossa != 1:
            mene = ota_jonosta() # Mikäli automaatio on valmis, otetaan jonosta seuraava työpiste
            if (mene != 0): # Jos jonossa oli jotain, asetetaan bridge ja trolley kiireiseksi
                print("Automaatio käynnistyy!")
                perilla = False
                bridgeBusy = 1
                trolleyBusy = 1
            else: # Jos jono oli tyhjä, asetetaan bridge ja trolley odottamaan
                bridgeBusy = 0
                trolleyBusy = 0

    if halt < 1:
        if (mene != 0):
            bridgeBusy = automaatio(mene, kaytossa)
            if bridgeBusy == 0:
                perilla = True
                kaytossa = 1
    elif bridgeBusy != 0 and kaytossa == 0 and not perilla: # Jos koukulta vastaanotettiin havainto esteestä, keskeytetään automaation suorittaminen ja pyydetään nostamaan koukkua
        message = {"koukku_ohjaus": 2}
        to_hook_emitter_device.send(json.dumps(message))

    if key == ord("F"): #Vaijeri sisään (koukku ylöspäin)
        message = {"koukku_ohjaus": 2}
        to_hook_emitter_device.send(json.dumps(message))
    if key == ord("V"): #Vaijeri sisään (koukku ylöspäin)
        message = {"koukku_ohjaus": 1}
        to_hook_emitter_device.send(json.dumps(message))
