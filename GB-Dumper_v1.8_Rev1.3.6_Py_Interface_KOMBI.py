# GBCartRead - Arduino Interface Version: 1.8
# orig. Author: Alex from insideGadgets (http://www.insidegadgets.com)
# Created: 18/03/2011, Last Modified: 21/03/2016
# GB-Dumperv 1.8 Rev1.3.6 by wodowiesel
# Optimized: 14/11/2024
#------------------
import os
import sys
import time
import string
import struct
import serial
import atexit
import signal
#import socket #for link cable  / eth
#------------------
nintendoLogo = [
                          0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
                          0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E, 0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
                          0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E
                          ] #48 byte
                          
old_licensee_map = [ #// 256
          "NONE", "NINTENDO R&D1", "\0", "\0", "\0", "\0", "\0", "\0", 
          "CAPCOM", "HOT-B", "JALECO", "COCONUTS", "EILTE SYSTEMS", "\0", "\0", "\0",
          "\0", "\0", "\0", "ELECTRONIC ARTS", "\0", "\0", "\0", "\0", 
          "HUDSONSOFT", "ITC ENTERTAINMENT", "YANOMAN", "\0", "\0", "CLARY", "\0", "VIRGIN",
          "\0", "\0", "\0", "\0", "PCM COMPLETE", "SAN-X", "\0", "\0", 
          "KOTOBUKI SYSTEMS", "SETA", "\0", "\0", "\0", "\0", "\0", "\0",
          "INFOGRAMES", "NINTENDO", "BANDAI", "SEE NEW LICENSE CODE", "KONAMI", "HECTOR", "\0", "\0", 
          "CAPCOM", "BANPRESTO", "\0", "\0", "*ENTERTAINMENT I", "\0", "GREMLIN", "\0",
          "\0", "UBI SOFT", "ATLUS", "\0", "MALIBU", "\0", "ANGEL", "SPECTRUM HOLOBY", 
          "\0", "IREM", "VIRGIN", "\0", "\0", "MALIBU", "\0", "U.S. GOLD",
          "ABSOLUTE", "ACCLAIM", "ACTIVISION", "AMERICAN SAMMY", "GAMETEK", "PARK PLACE", "LJN", "MATCHBOX", 
          "\0", "MILTON BRADLEY", "MINDSCAPE", "ROMSTAR", "NAXAT SOFT", "TRADEWEST", "\0", "\0",
          "TITUS", "VIRGIN", "\0", "\0", "\0", "\0", "\0", "OCEAN", 
          "\0", "ELECTRONIC ARTS", "\0", "\0", "\0", "\0", "ELITE SYSTEMS", "ELECTRO BRAIN",
          "INFOGRAMES", "INTERPLAY", "BRODERBUND", "SCULPTURED SOFT", "\0", "THE SALES CURVE", "\0", "\0", 
          "T*HQ", "ACCOLADE", "TRIFFIX ENTERTAINMENT", "\0", "MICROPROSE", "\0", "\0", "KEMCO",
          "MISAWA ENTERTAINMENT", "\0", "\0", "LOZC", "\0", "\0", "*TOKUMA SHOTEN I", "\0", 
          "\0", "\0", "\0", "BULLET_PROOF SOFTWARE", "VIC TOKAI", "\0", "APE", "I'MAX",
          "\0", "CHUN SOFT", "VIDEO SYSTEM", "TSUBURAVA", "\0", "VARIE", "YONEZAWA/S'PAL", "KANEKO", 
          "\0", "ARC", "NIHON BUSSAN", "TECMO", "IMAGINEER", "BANPRESTO", "\0", "NOVA",
          "\0", "HORI ELECTRIC", "BANDAI", "\0", "KONAMI", "\0", "KAWADA", "TAKARA", 
          "\0", "TECHNOS JAPAN", "BRODERBUND", "\0", "TOEI ANIMATION", "TOHO", "\0", "NAMCO",
          "ACCLAIM", "ASCII OR NEXOFT", "BANDAI", "\0", "ENIX", "\0", "HAL", "SNK", 
          "\0", "PONY CANYON", "*CULTURE BRAIN O", "SUNSOFT", "\0", "SONY IMAGESOFT", "\0", "SAMMY",
          "TAITO", "\0", "KEMCO", "SQUARESOFT", "*TOKUMA SHOTEN I", "DATA EAST", "TONKIN HOUSE", "\0", 
          "KOEI", "UFL", "ULTRA", "VAP", "USE", "MELDAC", "*PONY CANYON OR", "ANGEL",
          "TAITO", "SOFEL", "QUEST", "SIGMA ENTERPRISES", "ASK KODANSHA", "\0", "NAXAT SOFT", "COPYA SYSTEMS", 
          "\0", "BANPRESTO", "TOMY", "LJN", "\0", "NCS", "HUMAN", "ALTRON",
          "JALECO", "TOWACHIKI", "UUTAKA", "VARIE", "\0", "EPOCH", "\0", "ATHENA", 
          "ASMIK", "NATSUME", "KING RECORDS", "ATLUS", "EPIC/SONY RECORDS", "\0", "IGS", "\0",
          "A WAVE", "\0", "\0", "EXTREME ENTERTAINMENT", "\0", "\0", "\0", "\0", 
          "\0", "\0", "\0", "\0", "\0", "\0", "\0", "LJN"
        ]

#//https://gbdev.gg8.se/wiki/articles/The_Cartridge_Header#0144-0145_-_New_Licensee_Code
new_licensee_map = [ #// 100
          "NONE", "NINTENDO R&D1", "\0", "\0", "\0", 
          "\0", "\0", "\0", "CAPCOM", "HOT-B",
          "JALECO", "COCONUTS", "ELITE SYSTEMS", "ELECTRONIC ARTS", "\0", 
          "\0", "\0", "\0", "HUDSONSOFT", "B-AI",
          "KSS", "\0", "POW", "\0", "PCM COMPLETE", 
          "SAN-X", "\0", "\0", "KEMCO JAPAN", "SETA",
          "VIACOM", "NINTENDO", "BANDIA", "OCEAN/ACCLAIM", "KONAMI", 
          "HECTOR", "\0", "TAITO", "HUDSON", "BANPRESTO",
          "\0", "UBI SOFT", "ATLUS", "\0", "MALIBU", 
          "\0", "ANGEL", "BULLET-PROOF", "\0", "IREM",
          "ABSOLUTE", "ACCLAIM", "ACTIVISION", "AMERICAN SAMMY", "KONAMI", 
          "HI TECH ENTERTAINMENT", "LJN", "MATCHBOX", "MATTEL", "MILTON BRADLEY",
          "TITUS", "VIRGIN", "\0", "\0", "LUCASARTS", 
          "\0", "\0", "OCEAN", "\0", "ELECTRONIC ARTS",
          "INFOGRAMES", "INTERPLAY", "BRODERBUND", "SCULPTURED", "\0", 
          "SCI", "\0", "\0", "THQ", "ACCOLADE",
          "MISAWA", "\0", "\0", "LOZC", "\0", 
          "\0", "TOKUMA SHOTEN I*", "TSUKUDA ORI*", "\0", "\0",
          "\0", "CHUN SOFT", "VIDEO SYSTEM", "OCEAN/ACCLAIM", "\0", 
          "VARIE", "YONEZAWA/S'PAL", "KANEKO", "\0", "PACK IN SOFT"
        ]
        
#-------------
print('\nGB-Dumper v1.8 Rev1.3.6b by wodowiesel\n')
print('###################################\n')
sys.stdout.flush()
#------------------
# Change COM to the port the Arduino is on.
# You can lower the baud rate of 400 kBit if you have issues connecting to the Arduino or the ROM has checksum errors
port = 'COM4'
baud = 115200 #9600 #57600  #19200
to = 1
print('Serial connection on: '+ str(port) +' with baudrate: ' + str(baud) + ' with timeout: ' + str(to) +'\n')
#16 lines = 1 kB and every 1 kB a # is written in before output
time.sleep(1)
waitInput = 1
userInput = '0'
gameTitle= ''
saveInput = '0'
data = bytes(b'')
suffix_sav = '.sav'
#----------------
try:
    # /dev/ttyACM0 (old) or ttyS0 (newer via usb) for linux-based systems
    ser = serial.Serial(port=port, baudrate=baud, timeout=to) # timeout in seconds
    
except serial.SerialException: #https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    print('\nSerial error, exiting...\n')
    waitInput = 1
    
    #atexit.register(cleanup_serial)
    signal.signal(signal.SIGINT, sys.exit(1))
    
    
except ValueError:
    print('\nValue error, exiting...\n')
    waitInput = 1
    sys.exit(1)
#------------------

while (waitInput == 1):
    print('\nWhich Cartridge do you use?\n0. GB Classic\n1. GB Advance\n2. Exit\n')
    print('>')
    userInput = input()
    sys.stdout.flush()
#------
    if (userInput == '0'):
        #------
        # set directly in ardu the gb_volt (nr 14) to 1 high (5V) 
        while (waitInput == 1):
            print('\n==> GB Classic <==\n')
            
            print('\n0. Header Read\n1. ROM Dump\n2. RAM Dump\n3. RAM Write\n4. AUDIO Check\n5. CLK Check\n6. Exit\n') #4. SD Check\n5. CLK Test
            print('>')
            sys.stdout.flush()
            userInput = input()
        
            #-------
            if (userInput == '0'):
                ser.write('HEADER'.encode('ascii')) 
                # standard is utf_8 if nothig is specified or use option encoding="ascii", byte same for decode
                # Die Methode .decode(), um ein Objekt vom Typ bytes in ein Objekt vom Typ str (String) zu dekodieren. 
                # https://docs.python.org/3/library/codecs.html#standard-encodings
                
        #--------------------
        # normal gb # https://gbdev.gg8.se/wiki/articles/Gameboy_ROM_Header_Info
                gsl2 = ascii(ser.readline())
                try:
                   gslv2 = gsl2[2:(len(gsl2)-5)]
                   ep2 = str(gslv2).replace("\\x", "")
                   
                except ValueError:
                    print ('\nGSL/EP Error\n')
                
                gsl1 = ascii(ser.readline())
                try:
                   gslv1 = gsl1[2:(len(gsl1)-5)]
                   ep1 = str(gslv1).replace("\\x", "")
                   
                except ValueError:
                    print ('\nGSL/EP Error\n')

                ep = ep2 + ep1
                ep_hex = "0x"
                ep_new = ep_hex + ep.upper()
                print('\nGame starting location/entry point adress: '+ str(ep_new) +'\n')

                    
        #-------
        #004h..09Fh - Nintendo Logo, 156 Bytes
                logoCheck = ascii(ser.readline())
                try:
                    logoCheck = int(logoCheck[2:(len(logoCheck)-5)])
                    
                    print('Logo Check: ')
                    if (logoCheck == 1):
                        print('1 OK\n')
                    elif (logoCheck == 0):
                        print ('0 Failed\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('Logo Error\n')

        #------------------------
        #0A0h - Game Title, Uppercase Ascii, max 12 characters, Space for the game title, padded with 00h (if less than 12 chars)
        #Every Gameboy ROM header starts off at the HEX offset 0134.
        #The title of a ROM is 15 or 16 bytes,the 16th byte denotes CGB features. This is then confirmed by reading a HEX value of 80 (dec 128)
                gameTitle = ascii(ser.readline())
                try:
                    gameTitle = gameTitle[2:(len(gameTitle)-5)] 
                    if (gameTitle != None):
                        print('Gametitle: '+ str(gameTitle) +'\n') # maybe str()
                    else:
                        gameTitle = 'unknown'
                        print ('Gametitle not found or none, using "unknown"\n')
                        
                except ValueError: 
                        print('Gametitle Error\n')
        #--------------            
                manufTitle = ascii(ser.readline())
                try:
                    manufTitle = manufTitle[2:(len(manufTitle)-5)] 
                    if (manufTitle != None):
                        print('Manufacturer title: '+ str(manufTitle) +'\n') # maybe str()
                    else:
                        manufTitle = 'unknown'
                        print ('Manufacturer title not found or none, using "unknown"\n')
                        
                except ValueError: 
                        print('Manufacturer title Error\n')
                        
        #-------------------           
                #if 1 / true -> save rom as gbc, 0 as gb
                cgbflag = ascii(ser.readline()) #0143
                try:
                    cgbflags = int(cgbflag[2:(len(cgbflag)-5) ])
                    print ('CGB (Color) Flag Compatibiity: '+ str(cgbflags)+'\n')
                    if (cgbflags == 128): # 80h
                        print ('CGB supported & works on old gameboys also\n')
                    elif (cgbflags == 192): # C0h
                        print ('CGB only on Color [exclusive] (physically the same)\n')
                    elif (cgbflags == 0): # C0h
                        print ('CGB unsupported, normal Game b/w\n') 
                    else:
                        print ('CGB unknown\n')
                        
                except ValueError: 
                    print ('CGB Flag type Error\n')
        #-------------------------            
                sgbflag = ascii(ser.readline()) #0146 supergameboy
                try:
                    sgbflags = int(sgbflag[2:(len(sgbflag)-5) ] )
                    print ('SGB (Super) Flag Compatibiity: '+ str(sgbflags)+'\n')
                    if (sgbflags == 0): # 80h
                        print ('SGB unsupported (Normal Gameboy or CGB only game)\n')
                    elif (sgbflags == 3): # 03h
                        print ('SGB supported (Snes)\n')
                    else:
                        print ('SGB unknown\n')
                        
                except ValueError: 
                    print ('SGB Flag type Error\n')
         #---------------------           
        # https://problemkaputt.de/gbatek.htm#gbacartridges
        # https://problemkaputt.de/gbatek.htm
        # https://en.wikipedia.org/wiki/Game_Boy_Advance_Video External Memory (Game Pak) 
                cartridgeType = ascii(ser.readline()) #0147
                try:
                    cartridgeType = int(cartridgeType[2:(len(cartridgeType)-5)])
                    print ('Cartridge type: '+str(cartridgeType) +'\n')
                    
        #--------------------            
        # http://gameboy.mongenel.com/dmg/asmmemmap.html
        # https://gbdk-2020.github.io/gbdk-2020/docs/api/docs_rombanking_mbcs.html

                    print('MBC type: ')
                    if (cartridgeType == 0):
                        print ('ROM ONLY\n')
                    elif (cartridgeType == 1):
                        print ('ROM+MBC1\n')
                    elif (cartridgeType == 2):
                        print ('ROM+MBC1+RAM\n')
                    elif (cartridgeType == 3):
                        print ('ROM+MBC1+RAM+BATTY\n')
                    elif (cartridgeType == 5):
                        print ('ROM+MBC2\n')
                    elif (cartridgeType == 6):
                        print ('ROM+MBC2+BATT\n')
                    elif (cartridgeType == 8):
                        print ('ROM+RAM\n')
                    elif (cartridgeType == 9): 
                        print ('ROM+RAM+BATT\n')
                    elif (cartridgeType == 11): #0x0B
                        print ('ROM+MMM01\n')
                    elif (cartridgeType == 12): #0x0C
                        print ('ROM+MMM01+SRAM\n')
                    elif (cartridgeType == 13): #0x0D
                        print ('ROM+MMM01+SRAM+BATT\n4 in 1 (Europe) (Sachen)\n')
                    elif (cartridgeType == 15): #0x0F
                        print ('ROM+MBC3+RTC+BATT\n')
                    elif (cartridgeType == 16): #0x10
                        print ('ROM+MBC3+RTC+RAM+BATT\n')
                    elif (cartridgeType == 17): #0x11
                        print ('ROM+MBC3\n')
                    elif (cartridgeType == 18): #0x12
                        print ('ROM+MBC3+RAM\n')
                    elif (cartridgeType == 19): #0x13
                        print ('ROM+MBC3+RAM+BATT\n')
                    elif (cartridgeType == 21): #0x15
                        print ('MBC4\n')
                    elif (cartridgeType == 22): #0x16
                        print ('MBC4+RAM')
                    elif (cartridgeType == 23): #0x17
                        print ('MBC4+RAM+BATT\n')
                    elif (cartridgeType == 25): #0x19
                        print ('ROM+MBC5\n')
                    elif (cartridgeType == 26): #0x1A
                        print ('ROM+MBC5+RAM\n')
                    elif (cartridgeType == 27): #0x1B
                        print ('ROM+MBC5+RAM+BATT\n')
                    elif ((cartridgeType == 27) and (regions == 225)): #0x1B
                        print ('EMS MULTICARD \n')
                    elif (cartridgeType == 28): #0x1C
                        print ('ROM(8 MB)+MBC5+RUMBLE\n')
                    elif (cartridgeType == 29): #0x1D
                        print ('ROM(8 MB)+MBC5+RUMBLE+SRAM\n')
                    elif (cartridgeType == 30): #0x1E
                        print ('ROM+MBC5+RUMBLE+SRAM+BATT\n')
                    elif (cartridgeType == 31): #0x1F
                          print ('Camera\n')
                    elif (cartridgeType == 32): #0x20
                          print ('MBC6\n')
                    elif (cartridgeType == 34): #0x22
                          print ('MBC7+SRAM+BATT+RUMBLE+SENSOR\n')
                    elif (cartridgeType == 99 or cartridgeType == 209): #0x63
                        print ('Special-WISDOM TREE MAPPER Multi\n') 
                        #ROM contains "WISDOM TREE" or "WISDOM\x00TREE" (the space can be $20 or $00), $0147 = $00, $0148 = $00, size > 32k. 
                        #This method works for the games released by Wisdom Tree, Inc. $0147 = $C0, $014A = $D1. 
                        #These are the values recommended by beware for 3rd party developers to indicate that the ROM is targeting Wisdom Tree mapper hardware. (See below.)
                    elif (cartridgeType == 190): #0xBE
                        print ('Pocket Voice or BUNG Multi-cartridge\n') 
                    elif (cartridgeType == 252): #0xFC
                        print ('MBC Gameboy Pocket Camera\n')
                    elif (cartridgeType == 253): #0xFD
                        print ('RTC+Bandai TAMA5 Mapper\n')
                    elif (cartridgeType == 254): #0xFE
                        print ('RTC+ IR Hudson HuC-3 (MBC3)+Speaker\n')
                    elif (cartridgeType == 255): #0xFF
                        print ('ROM+SRAM+BATT+IR Hudson HuC-1 (MBC1) or Pro Action Replay (Europe)\n')
                    elif (cartridgeType == None):
                        print ('is None\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('Cartridge type Error\n')
        #--------------------------       
                romSize = ascii(ser.readline())
                try:
                    romSize = int(romSize[2:(len(romSize)-5)])
                    print ('ROM type: '+ str(romSize)+'\n')
                
                    print('ROM size: ')
                    if (romSize == 0):
                        print ('32 KByte (2 banks)\n') # or 16 KByte (1 Bank)
                    elif (romSize == 1):
                        print ('64 KByte (4 banks)\n')
                    elif (romSize == 2):
                        print ('128 KByte (8 banks)\n')
                    elif (romSize == 3):
                        print ('256 KByte (16 banks)\n')
                    elif (romSize == 4):
                        print ('512 KByte (32 banks)\n')
                    elif ((romSize == 5) and ((cartridgeType == 1) or (cartridgeType == 2) or (cartridgeType == 3))):
                        print ('1008 KByte (63 banks)\n')
                    elif (romSize == 5): 
                        print ('1 MByte (64 banks)\n')
                    elif ((romSize == 6) and ((cartridgeType == 1) or (cartridgeType == 2) or (cartridgeType == 3))):
                        print ('2 MByte (125 banks)\n')
                    elif (romSize == 6):
                        print ('2 MByte (128 banks)\n')
                    elif (romSize == 7):
                        print ('4 MByte (256 banks)\n')
                    elif (romSize == 8):
                        print ('8 MByte (512 banks)\n')
                    elif (romSize == 13): #0D
                        print ('256 KByte (16 banks), 4 in 1 (Europe) (Sachen) \n') 
                        #MBC1M uses the MBC1 IC, but not connect the MBC1's A18 to the ROM. allows  multiple 2 Mbit (16 bank) games, with SRAM bank select ($4000) to select which of up to four game
                    elif (romSize == 82): # 0x52
                        print ('1.1 MByte (72 banks)\n')
                    elif (romSize == 83): #0x53
                        print ('1.2 MByte (80 banks)\n')
                    elif (romSize == 84): #0x54
                        print ('1.5 MByte (96 banks)\n')
                    elif (romSize == 255): #FF
                        print ('32 KByte (2 banks), Action Replay Pro(Europe)\n') # special
                    elif (romSize == None):
                        print ('is None, 0 KByte (0 Banks)\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('ROM size Error\n')
                    
                    
                #-------------------------------
                romBank = ascii(ser.readline())
                try:
                    romBanks = int(romBank[2:(len(romBank)-5)])
                    print ('ROM banks: '+ str(romBanks)+'\n') 
                    
                except ValueError:
                    print ('ROM bank Error\n') 
                #-------------------------------
                romEndAddr = ascii(ser.readline())
                try:
                    romEndAddress = romEndAddr[2:(len(romEndAddr)-5)]
                    print ('ROM end address: '+ str(romEndAddress)+'\n') 
                    
                except ValueError:
                    print ('ROM end asdress Error\n') 
                    
                #-------------------------------
                ramSize = ascii(ser.readline())
                try:
                    ramSize = int(ramSize[2:(len(ramSize)-5)])
                    print ('RAM type: '+ str(ramSize)+'\n')

                    print('RAM size: ')
                    if (ramSize == 0):
                        print ('is 0 (empty)\n')
                    elif ((ramSize == 0) and (cartridgeType == 6)):
                        print ('512 byte (1 bank, nibbles)\n')
                    elif (ramSize == 1):
                        print ('2 KByte (1 bank)\n')
                    elif (ramSize == 2):
                        print ('8 KByte (1 bank)\n')
                    elif (ramSize == 3):
                        print ('32 KByte (4 banks)\n')
                    elif (ramSize == 4):
                        print ('128 KByte (16 banks) / Camera\n')
                    elif (ramSize == 5):
                        print ('64 KByte (8 banks)\n') 
                    elif (ramSize == 56): #0x38
                        print ('? KByte (? banks), Beast Fighter (Taiwan) (Sachen)\n')
                    elif (ramSize == 255):
                        print ('? KByte (? banks), Action Replay Pro (Europe)\n')
                    elif (ramSize == None):
                        print ('is None, 0 KByte (0 Banks)\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('RAM size Error\n')
                    
            #-------------------------------
                ramBank = ascii(ser.readline())
                try:
                    ramBanks = ramBank[2:(len(ramBank)-5)]
                    print ('RAM banks: '+ str(ramBanks)+'\n') 
                    
                except ValueError:
                    print ('RAM bank Error\n') 
                
            #-------------------------------
                ramEndAddr = ascii(ser.readline())
                try:
                    ramEndAddress = ramEndAddr[2:(len(ramEndAddr)-5)]
                    print ('RAM end address: '+ str(ramEndAddress)+'\n') 
                    
                except ValueError:
                    print ('RAM end asdress Error\n') 
                    
            #-------------------------
                region = ascii(ser.readline()) #014A
                try:
                    regions = int(region[2:(len(region)-5)])
                    print ('Region type: '+ str(regions)+'\n')
                    if (regions == 0):
                        print ('Japan\n')
                    elif (regions == 1):
                        print ('NOT Japan, Rest of the World\n')
                    elif (regions == 209):
                        print ('WisdomTree Mapper\n')
                    elif (regions == 225):
                        print ('EMS Multicard\n')
                    else:
                        print ('region not ound or unknown\n')
                        
                except ValueError: 
                    print ('Region type Error\n')
        #---------------------------
                developer = ascii(ser.readline()) #014B & 0144 & 145 
                
                try:
                   
                    developers = int(developer[2:(len(developer)-5)])
                    print ('Developer Nr: '+ str(developers)+'\n')
                    
                    # kann nicht unterschieden werden, nur per nummer wenn es für neue nachgerechnet werden muss oder es wird per string abgleich gearbeitet, zb kombi
                    if (developers > 100):
                        licensee = old_licensee_map[developers]
                    elif (developers <= 100):
                        
                        licensee = old_licensee_map[developers]
                        licensee_new = new_licensee_map[developers] 
                        if (licensee == "SEE NEW LICENSE CODE"): # developers == 51 # for extra assurance
                            licensee_new = new_licensee_map[developers] #new
                            print ('developer/publisher new: '+ str(licensee_new)+'\n')
                        
                        elif (licensee != "SEE NEW LICENSE CODE"): #old
                            print ('developer/publisher old: '+ str(licensee)+' or new: '+ str(licensee_new) +'\n')
                        else:
                            print ('developer not found or unknown\n')
                            
                    else:
                        print ('developer not found or unknown\n')
                    
                    
                    """
                    if ((developers != 51) and (developers != None)): # old should it be 0x33 -> dec 51???
                        print ('developer/publisher old: '+ str(licensee)+'\n')
                    elif (developers == 51): #new
                        print ('developer/publisher new: '+ str(licensee_new)+'\n')
                    else:
                        print ('developer unknown\n')
                     """   
                    """
                     developer_name = developer[2:(len(developer)-5)]
                     if (developer_name != None):
                        print ('Developer Nr: '+ str(developers)+'\n')
                    else:
                        print ('developer unknown\n')
                    
                    """
                except ValueError: 
                    print ('Developer type Error\n')
                    
                    
        #----------------------           
                romver = ascii(ser.readline()) #014C
                try:
                    romversion = int(romver[2:(len(romver)-5)])
                    print ('ROM version: '+ str(romversion)+'\n')
                    
                except ValueError: 
                    print ('ROM version Error\n')
        #------------------------       
                headerCS = ascii(ser.readline())
                
                try:
                    headerCS = int(headerCS[2:(len(headerCS)-5)])
                    print('Header complentary CS: '+ str(headerCS)+'\n')
                    
                except ValueError:
                    print ('Header checksum Error\n')
            
        #-------
                headerCheck = ascii(ser.readline())
                
                try:
                    headerChecker = int(headerCheck[2:(len(headerCheck)-5)])
                    
                    print('Header CRC Check: ')
                    if (headerChecker == 1):
                        print('1 OK\n')
                    elif (headerChecker == 0):
                        print ('0 Failed\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('Header validation Error\n')

        #-------------------------
                
                globalCheck = ascii(ser.readline())
                try:
                    globalChecker = int(globalCheck[2:(len(globalCheck)-5)])
                    print(str(globalChecker))
                    
                    print('global CRC32 Check: ')
                
                    if (globalChecker == 1):
                        print('1 OK\n')
                    elif (globalChecker == 0):
                        print ('0 Failed\n')
                    else:
                        print('not found or unknown\n')
                    
                except ValueError:
                    print ('global CRC32 checksum Error\n')

        #------------
                sys.stdout.flush()

            #-------------------
            elif (userInput == '1'):
                #if 1 / true - and 5v high 1 -> save rom as gbc, 0 as gb
                if ((cgbflags ==128) or (cgbflags == 192)): 
                    suffix = '.gbc'
                elif (cgbflags ==0):
                    suffix = '.gb'
                else:
                    suffix = '.gb'
                
                gameTitle_gb = gameTitle + suffix
                print('\nDumping ROM (game) to ' + str(gameTitle_gb) +'\n')
                readBytes = 0
                inRead = 1
                Kbytesread = 0
                
                print('\nPlease select where to save: \n0. PC\n1. SDCard (SPI)\n')
                print('>')
                saveInput =  input()

                if (saveInput == '0'):
                    print('0. Dumping to PC...\n')
                    ser.write('READROM'.encode('ascii'))
                    f = open(gameTitle_gb, 'wb')
                    while 1:
                        if inRead == 1:
                            line = ser.read(64) # note sure if 64 for gba
                            print(line.hex())
                            #print(line) #raw utf8
                            #sys.stdout.flush()
                            if (len(line) == 0):
                                break
                            readBytes += 64
                            f.write(line)
                        if ((readBytes % 1024 == 0) and (readBytes != 0)):
                            print('#')
                            sys.stdout.flush()
                        if ((readBytes % 32768 == 0) and (readBytes != 0)):
                            Kbytesread = Kbytesread + 1
                            Kbytesprint = Kbytesread * 32
                            print('%sK' % Kbytesprint)
                            sys.stdout.flush()
                    sys.stdout.flush()
                    f.close()
                    print('\nFinished\n')
                
                elif (saveInput == '1'):
                    print('1. Dumping to SDCard (SPI) [FAT/32]...\n') # directly von i2c to spi!!! 
                    ser.write('READROM2'.encode('ascii'))
                    print('\nNot ready yet wip\n')
                    #print('\nFinished\n')
                    
                else:
                    print('\nOption not recognised, please try again!\n')
                sys.stdout.flush()
            #----------------
            elif (userInput == '2'):
                print('\nDumping RAM (save) to ' + str(gameTitle) + str(suffix_sav)+'\n')
                readBytes = 0
                inRead = 1
                Kbytesread = 0
                ser.write('READRAM'.encode('ascii'))
                f = open(gameTitle+suffix_sav, 'wb')
                while 1:
                    if (inRead == 1):
                        line = ser.read(64)
                        print(line.hex())
                        #print(line) #raw utf8
                        #sys.stdout.flush()
                        if (len(line) == 0):
                            break
                        readBytes += 64
                        f.write(line)
                    if ((readBytes % 256 == 0) and (readBytes != 0)):
                        print('#')
                        sys.stdout.flush()
                    if ((readBytes % 1024 == 0) and (readBytes != 0)):
                        Kbytesread = Kbytesread + 1
                        print('%sK' % Kbytesread)
                        sys.stdout.flush()
                
                sys.stdout.flush()
                f.close()
                print('\nFinished\n')
                
            #-------------------
            elif (userInput == '3'):
                print('\nGoing to write to RAM (save) from ' + str(gameTitle) + '.usffix3n')
                print('Press y to continue or any other key to abort\n')
                userInput2 = input()

                if (userInput2 == 'y'):
                    print('\nWriting to RAM from ' + str(gameTitle) + str(suffix_sav)+'\n')
                    fileExists = 1
                    doExit = 0
                    printHash = 0
                    Kbyteswrite = 0
                    try:
                        print('*** This will erase the save game from your Gameboy Cartridge ***\n')
                        f = open(gameTitle+suffix_sav, 'rb')
                    except IOError:
                        print('\nNo save file found, aborted\n')
                        fileExists = 0
                    if (fileExists == 1):
                        ser.write('WRITERAM'.encode('ascii'))
                        time.sleep(1); # Wait for Arduino to setup
                        while 1:
                            line1 = f.read(64) # Read 64bytes of save file
                            print(line1.hex())
                            #print(line1) #raw utf8
                            #sys.stdout.flush()
                            if not line1:
                                break
                            ser.write(line1)
                            time.sleep (1); # Wait for Arduino to process the 64 bytes
                            
                            if ((printHash % 4 == 0) and (printHash != 0)): # 256 / 64 = 4
                                print('#')
                                sys.stdout.flush()
                            if ((printHash % 16 == 0) and (printHash != 0)):
                                Kbyteswrite = Kbyteswrite + 1
                                print('%sK' % Kbyteswrite)
                                sys.stdout.flush()
                            printHash += 1

                    sys.stdout.flush()
                    f.close()
                    print('\nFinished\n')

                else:
                    print('\n n=Aborted! binary decode....\n')
                    data += byte
                    dc = data.decode('ascii')
                    print(dc.hex())
                    sys.stdout.flush()
            
            elif (userInput == '4'):
                print('\nAUDIO Check\n')
                ser.write('AUDIO'.encode('ascii'))
                #line = ascii(ser.read())
                #print(line.hex())
                #print(line)
                print("\nAudio done\n")
                sys.stdout.flush()
                
            #------------------
            elif (userInput == '5'):
                print('\nCLK Check\n')
                ser.write('CLOCK'.encode('ascii'))
                #line = ascii(ser.read())
                print("\nClock done\n")
                
                sys.stdout.flush()
            #-----------
            elif (userInput == '6'):
                print('\nPreparing Exit...\n')
                ser.write('EXIT'.encode('ascii'))
                #line = ascii(ser.read(64))
                #print(line)
                print('\nAll connections terminated!\n')
                sys.stdout.flush()
                waitInput = 0
                break
            #---------    
            else:
                print('\nOption not recognised, please try again!\n')
                sys.stdout.flush()
    #-----

    elif (userInput == '1'):

        # set directly in ardu the gb_volt (nr 14) to 0 low (3V3) 
        while (waitInput == 1):
            print('\n==> GBA <==\n')
            
            print('\n0. GBA Header Read\n1. GBA ROM Dump\n2. GBA RAM Dump\n3. GBA RAM Write\n4. CLK Check \n5. SD Check\n6. Exit\n')
            print('>')
            sys.stdout.flush()
            userInput = input()
            # https://problemkaputt.de/gbatek-gba-cartridge-header.htm only gba and gb is normal
            #The first 192 bytes at 8000000h-80000BFh in ROM are used as cartridge header. 
            #The same header is also used for Multiboot images at 2000000h-20000BFh (plus some additional multiboot entries at 20000C0h and up).
            
            if (userInput == '0'):
                ser.write('HEADERGBA'.encode('ascii')) 

        #---------------
                gsla2 = ascii(ser.readline())
                try:
                    gep2 = int(gsla2[2:(len(gsla2)-5)])
                    print('\nGSL2: '+ str(gep2))
                    epa2 = str(gep2).replace("\\x", "")
                    
                #except ValueError:
                #    print ('\nGSL2 Error\n')
                    
                    
                    gsla1 = ascii(ser.readline())
                #try:
                    gep1 = int(gsla1[2:(len(gsla1)-5)])
                    print('\nGSL1: ' + str(gep1))
                    epa1 = str(gep1).replace("\\x", "")
                
                #except ValueError:
                 #   print ('\nGSL1 Error\n')

                    epa = epa2 + epa1
                    epa_hex = "0x"
                    epa_new = epa_hex + epa.upper()
                    print('\nGame starting location/entry point adress: '+ str(epa_new) +'\n')
                    
                except ValueError:
                    print ('\nGSLA Error\n')
                
                #if (gsl1 == None and gsl2 == None):
                        #print ('0 boot Failed\n')
                #if (gsl1 != None and gsl2 != None):
                        #print ('1 boot ok\n')
                #else:
                        #print('unknown\n')
         
        #----
                logoChecker = ascii(ser.readline())
                try:
                    logoCheck2 = int(logoChecker[2:(len(logoChecker)-5)])
                    
                    print('Logo Check2: ')
                    if (logoCheck2 == 1):
                        print('1 OK\n')
                    elif (logoCheck2 == 0):
                        print ('0 Failed\n')
                    else:
                        print('not found or unknown\n')
                        
                except ValueError:
                    print ('Logo GBA Error\n')

        #----------
                dem = ascii(ser.readline())
                try:
                    dem2 = int(dem[2:(len(dem)-5)])
                    
                    print('dem: '+ str(dem2) +'\n')
                    
                except ValueError:
                    print ('dem Error\n')
        #--
                ckn = ascii(ser.readline())
                try:
                    ckn2 = int(ckn[2:(len(ckn)-5)])
                    
                    print('ckn: '+ str(ckn2)+'\n')
                    
                except ValueError:
                    print ('ckn Error\n')

        #----
                gameTitles = ascii(ser.readline())
                try:
                    gameTitle2 = gameTitles[2:(len(gameTitles)-5)] 
                    if (gameTitle2 != None):
                        print('Gametitle: '+ str(gameTitle2) +'\n') # maybe str()
                    else:
                        gameTitle2 = 'unknown'
                        print ('Gametitle not found or none, using "unknown"\n')
                        
                except ValueError: 
                        print('Gametitle Error\n')
        #------------
                gamecode = ascii(ser.readline()) #014A
                try:
                    gamecodes = gamecode[2:(len(gamecode)-5)]
                    print ('Game code: '+ str(gamecodes)+'\n')
                    """
                    if (gamecodes != None):
                        if (gamecodes[0] == 'A'):
                            print ('Normal game; Older titles (mainly 2001-2003)\n')
                        elif (gamecodes[0] == 'B'):
                            print ('Normal game; Newer titles (2003...)\n')
                        elif (gamecodes[0] == 'C'):
                            print ('Normal game; Not used yet, but might be used for even newer titles\n')
                        elif (gamecodes[0] == 'F'):
                            print ('Famicom/Classic NES Series (software emulated NES games)\n')
                        elif (gamecodes[0] == 'K'):
                            print ('Yoshi and Koro Koro Puzzle (acceleration sensor)\n') 
                        elif (gamecodes[0] == 'P'):
                            print ('e-Reader (dot-code scanner) (or NDS PassMe image when gamecode="PASS")\n')
                        elif (gamecodes[0] == 'R'):
                            print ('Warioware Twisted (cartridge with rumble and z-axis gyro sensor)\n')
                        elif (gamecodes[0] == 'U'):
                            print ('Boktai 1 and 2 (cartridge with RTC and solar sensor)\n')
                        elif (gamecodes[0] == 'V'):
                            print ('Drill Dozer (cartridge with rumble)\n')
                        else:
                            print('unknown\n')
                            
                        if (gamecodes[3] == 'J'):
                            print ('Japan\n')
                        elif (gamecodes[3] == 'P'):
                            print ('Europe\n')
                        elif (gamecodes[3] == 'E'):
                            print ('English\n')
                        elif (gamecodes[3] == 'F'):
                            print ('French\n')
                        elif (gamecodes[3] == 'D'):
                            print ('German\n')
                        elif (gamecodes[3] == 'S'):
                            print ('Spanish\n')
                        elif (gamecodes[3] == 'I'):
                            print ('Italian\n')
                        else:
                            print ('unknown\n')
                                    
                    else:
                        print ('None\n')
                    """
                        
                except ValueError: 
                    print ('Game code Error\n')
#---------                    
                manufcodes = ascii(ser.readline())
                try:
                    manufTitle2 = manufcodes[2:(len(manufcodes)-5)] 
                    if (manufTitle2 != None):
                        print('Manufacturer title: '+ str(manufTitle2) +'\n') # maybe str()
                    else:
                        manufTitle2 = 'unknown'
                        print ('Manufacturer title not found or none, using "unknown"\n')
                        
                except ValueError: 
                        print('Manufacturer title Error\n')         
                    
           #-----
                fv = ascii(ser.readline())
                try:
                    fv2 = int(fv[2:(len(fv)-5)])
                    
                    print('fv: '+ str(fv2))
                    
                except ValueError:
                    print ('fv Error\n')
           #--
                muc = ascii(ser.readline())
                try:
                    muc2 = int(muc[2:(len(muc)-5)])
                    
                    print('muc: '+ str(muc2))
                    
                except ValueError:
                    print ('muc Error\n')
            #--------
                dt = ascii(ser.readline())
                try:
                    dt2 = int(dt[2:(len(dt)-5)])
                    
                    print('dt: '+ str(dt2))
                    
                except ValueError:
                    print ('dt Error\n')
            #--

                rb = ascii(ser.readline())
                try:
                    rb2 = int(rb[2:(len(rb)-5)])
                    
                    print('rb: '+str(rb2))
                    
                except ValueError:
                    print ('rb Error\n')
                    
        #----
                svn = ascii(ser.readline())
                try:
                    svn2 = int(svn[2:(len(svn)-5)])
                    
                    print('svn: '+ str(svn2))
                    
                except ValueError:
                    print ('svn Error\n')

        #----
                cc = ascii(ser.readline())
                try:
                    cc2 = int(cc[2:(len(cc)-5)])
                    
                    print('cc: '+ str(cc2))
                    
                except ValueError:
                    print ('cc Error\n')
                    
          #-------          
                hgba = ascii(ser.readline())
                try:
                    hgba2 = int(hgba[2:(len(hgba)-5)])
                    
                    print('hgba: '+ str(hgba2))
                    
                except ValueError:
                    print ('hgba Error\n')
                    

        #----
                ra1 = ascii(ser.readline())
                try:
                    ra11 = int(ra1[2:(len(ra1)-5)])
                    print('ra1: '+ str(ra11))
                
                except ValueError:
                    print ('ra1 Error\n')
        #------            
                ra2 = ascii(ser.readline())
                try:
                    ra22 = int(ra2[2:(len(ra2)-5)])
                    print('ra2: '+ str(ra22))
                
                except ValueError:
                    print ('ra2 Error\n')

        #----
                nmm = ascii(ser.readline())
                try:
                    nmm2 = int(nmm[2:(len(nmm)-5)])
                    
                    print('nmm: '+ str(nmm2))
                    
                except ValueError:
                    print ('nmm Error\n')
        #------
                bm = ascii(ser.readline())
                try:
                    bm2 = int(bm[2:(len(bm)-5)])
                    
                    print('bm: '+ str(bm2))
                    
                except ValueError:
                    print ('bm Error\n')
        #-----
                sidn = ascii(ser.readline())
                try:
                    sidn2 = int(sidn[2:(len(sidn)-5)])
                    
                    print('sidn: '+ str(sidn2))
                    
                except ValueError:
                    print ('sidn Error\n')
                    
        #-------
                jb = ascii(ser.readline())
                try:
                    jb2 = int(jb[2:(len(jb)-5)])
                    
                    print('jb: '+str(jb2))
                    
                except ValueError:
                    print ('jb Error\n')
            #---
            elif (userInput == '1'):
                suffix_gba = '.gba'
                gameTitle_gba = gameTitle2 + suffix_gba
                print('\nDumping GBA ROM (game) to ' + str(gameTitle_gba) +'\n')
                readBytes = 0
                inRead = 1
                Kbytesread = 0
                ser.write('GBAROM'.encode('ascii'))
                f = open(gametitle_gba, 'wb')
                while 1:
                    if inRead == 1:
                        line = ser.read(64) # note sure if 64 for gba
                        print(line.hex())
                        #print(line)
                        sys.stdout.flush()
                        if (len(line) == 0):
                            break
                        readBytes += 64
                        f.write(line)
                    if ((readBytes % 1024 == 0) and (readBytes != 0)):
                        print('#')
                        sys.stdout.flush()
                    if ((readBytes % 32768 == 0) and (readBytes != 0)):
                        Kbytesread = Kbytesread + 1
                        Kbytesprint = Kbytesread * 32
                        print('%sK' % Kbytesprint)
                        sys.stdout.flush()
                
                sys.stdout.flush()
                f.close()                
                print('\nFinished\n')
                sys.stdout.flush()
             #---------------   
            elif (userInput == '2'):
                save_gba = gameTitle2 + suffix_sav       
                print('\nDumping RAM (save) to ' + str(save_gba)+'\n')
                readBytes = 0
                inRead = 1
                Kbytesread = 0
                ser.write('GBARAM'.encode('ascii'))
                f = open(save_gba, 'wb')
                while 1:
                    if (inRead == 1):
                        line = ser.read(64)
                        print(line.hex())
                        #print(line)
                        #sys.stdout.flush()
                        if (len(line) == 0):
                            break
                        readBytes += 64
                        f.write(line)
                    if ((readBytes % 256 == 0) and (readBytes != 0)):
                        print('#')
                        sys.stdout.flush()
                    if ((readBytes % 1024 == 0) and (readBytes != 0)):
                        Kbytesread = Kbytesread + 1
                        print('%sK' % Kbytesread)
                        sys.stdout.flush()
                
                sys.stdout.flush()
                f.close()
                print('\nFinished\n')
                sys.stdout.flush()
            #-----------------
            elif (userInput == '3'):
                print('\nGoing to write to RAM (save) from ' + str(gameTitle_gba)+'\n')
                print('Press y to continue or any other key to abort\n')
                userInput2 = input()

                if (userInput2 == 'y'):
                    print('\nWriting to RAM from ' + str(gameTitle_gba) +'\n')
                    fileExists = 1
                    doExit = 0
                    printHash = 0
                    Kbyteswrite = 0
                    try:
                        print('*** This will erase the save game from your Gameboy Cartridge ***\n')
                        f = open(gameTitle_gba, 'rb')
                    except IOError:
                        print('\nNo save file found, aborted\n')
                        fileExists = 0
                    if (fileExists == 1):
                        ser.write('GBAWRITE'.encode('ascii'))
                        time.sleep(1); # Wait for Arduino to setup
                        while 1:
                            line1 = f.read(64) # Read 64bytes of save file
                            print(line1.hex())
                            #print(line1)
                            #sys.stdout.flush()
                            if not line1:
                                break
                            ser.write(line1)
                            time.sleep (1); # Wait for Arduino to process the 64 bytes
                            
                            if ((printHash % 4 == 0) and (printHash != 0)): # 256 / 64 = 4
                                print('#')
                                sys.stdout.flush()
                            if ((printHash % 16 == 0) and (printHash != 0)):
                                Kbyteswrite = Kbyteswrite + 1
                                print('%sK' % Kbyteswrite)
                                sys.stdout.flush()
                            printHash += 1

                    sys.stdout.flush()
                    f.close()
                    print('\nFinished\n')
                sys.stdout.flush()
             #-------
            elif (userInput == '4'):
                print('\nSD Check\n')
                ser.write('SDCHECK'.encode('ascii'))
                line = ser.read()
                print(line.hex())
                #print(line)
                sys.stdout.flush()
                
                #------------------
            elif (userInput == '5'):
                print('\nCLK Check\n')
                ser.write('CLOCK'.encode('ascii'))
                #line = ser.read()
                #print(line.hex())
                #print(line)
                sys.stdout.flush()
                
                #------------------
            elif (userInput == '6'):
                print('\nPreparing Exit...\n')
                ser.write('EXIT'.encode('ascii'))
                #line = ser.read()
                #print(line.hex())
                #print(line)
                sys.stdout.flush()
                ser.close()
                waitInput = 0
                print('\nSerial terminated!\n')
                break   
            #-------
            else:
                print('\nOption not recognised, please try again!\n')
                sys.stdout.flush()

    #--------------
    elif (userInput == '2'):
        print('\nPreparing Exit...\n')
        ser.write('EXIT'.encode('ascii'))
        #line = ser.read()
        #print(line.hex())
        #print(line)
        sys.stdout.flush()
        ser.close()
        waitInput = 0
        print('\nSerial terminated!\n')

        break   
            
    #---
    else:
        print('\nOption not recognised, please try again!\n')
        sys.stdout.flush()
        
#--------------
print('\nClosing...\n')
sys.stdout.flush()
sys.exit(0)
#EOF
