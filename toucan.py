
# -*- coding: utf-8 -*-

#------------------------------------------
# Toucan Network Defender
# 
# Author: Collin Sullivan
#-----------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------
# Monitors a LAN and will protect against spoofing attacks for MITM purposes
# 1. Scans Network for Active Hosts
# 2. Scans hosts for Layer 2 Addresses and can "attack back" when a MITM is discovered by correcting poisoned hosts
# 3. Monitors for gratuitous NDP packets
# 4. Monitors for SYN Scans on a network

# Needs to be run as ROOT
#--------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------
#                    GNU GENERAL PUBLIC LICENSE
#                      Version 3, 29 June 2007

# Copyright (C) William Collin Sullivan <wcsullivan@oru.edu>
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#--------------------------------------------------------------------------------------------------------------------------------




import logging
import socket
from scapy.error import Scapy_Exception
from scapy.all import sr1,IP,ICMP
from scapy.all import srp
from scapy.all import Ether, ARP, conf
from scapy.all import IPv6
from scapy.all import *
import os
import sys
import threading
from threading import Thread
from optparse import OptionParser
import signal
from struct import *
import time
from twilio.rest import Client

#//////////////////////////////////////////////////
# Your Account SID from twilio.com/console
account_sid = "x"
# Your Auth Token from twilio.com/console
auth_token  = "y"
client = Client(account_sid, auth_token)
#/////////////////////////////////////////////////

logging.basicConfig(filename='toucan.log',level=logging.DEBUG)

os.system('cls' if os.name == 'nt' else 'clear')
print "\033[31m'                                                                                                        ............ "
print "\033[33m'                                                                                                ..............-.-----. "
print "\033[32m'                                         .-.                                               ..--.........:---:-------:- "
print "\033[31m'                                           .--                                          .-:-........:-:-:---....``````. "
print "\033[32m'                                            `.-.`````````.-:-.                     .-//:-.....--:::----.. "
print "\033[31m'                                            `..--..`````.-:+:-..-//:.           -+sdmmo-..-.--/::----. "
print "\033[32m'                                            .-///.--:/-.`..-:+///-.:/:.        +hm   h/.--+::-----. "
print "\033[31m'                                            .--/:::-.``-:+-.--/-/+/-----      hmdhssysy/://:::::."
print "\033[31m'                                                    ````....-:---.``.``````+mddhddddmd//+oyds."
print "\033[32m'                                            ..::--...-````....---...```````ommmmddmmmmmsdmmNs"
print "\033[31m'                                            ..-.-:-...``````..-::-:-`.````ommdddmmmmmdddmmmh."
print "\033[31m'                                            ...-::...```````:--:/::```-+hmmddhdmmdyhhhhmmm+`"
print "\033[31m'                                           .---.-:...```````-.-::+--/sdmmdhhhyyddddhhddmmm-"
print "\033[31m'                                            -.`.--...``````.:/oshdddmddddhhyyyssdmdddddmmm."
print "\033[37m'                                                .....````-+ydmmNmmmmddddmmhyyyssosydmdmmmmd."
print "\033[32m'                                                `...```.+hmmmmmmmddddddmNNmhyyyssooosyhdmNNh`"
print "\033[33m'                                                .````.odddddddhdddddmmmNNNmdyyysosoosyyhddh/"
print "\033[33m'                                                   +dmdddddhddddhdddmmNNNmdyyysoossyyhddh+"
print "\033[31m'                                                 -ydddddddddddddmddhdmmdddddhyyyyyyhhddh+"
print "\033[31m'                              ``.`.`            dddddddddddddddhdhydmhhyhmmdhyyyhhddhy:"
print "\033[32m'                                .-:-..`.       dddddhdddddyssyhhyyyyddyhhhmmmmdddddds.```.----...````.-.."
print "\033[33m'                                 .-:+/:..    /dddddhdddho///osyyssssydddddmNNNNNNNms....:::--------.--:-."
print "\033[35m'                                         /:-. :oyhhhhhhs+//:://ossssssyhdmmNNNNNNNd+---://:::----//-----:."
print "\033[33m'                                            +::::++oss/ss+:::-:osysssssydmmNNNmds:-:/++o:-:::.-:--.-...."
print "\033[31m'                                            -yyyo++//+/+/ssy++/--:oossyyyhhdmmhss:...+o+/:::-.---........"
print "\033[34m'                                            ddhyyysysso+ysh:-:::::/+syhhhdhy+-`-:.`.s+/:----.........."
print "\033[37m'                                           +mdhhhyymyhshy+o+/:-.-:///+oss+:.`````::-s/::::+:::-"
print "\033[33m'                                           ymddhyhhdssy+:-:+ys/:..-/+/:---````````.:+/:---/---."
print "\033[32m'                                           ddh+hdmhs+s+----/hhssoo+-://oyyo.````````-//:-:--.."
print "\033[31m'                                           dy+.hmdy+//::-:-ohhyyyoso+::yssy:..````````-/++:-.."
print "\033[32m'                                          :y+.-ydhs+---::.`:ooo++/:/sooh+yy/+::::-----:-+so+::-:-....``.........`"
print "\033[32m'                                          :/:`--/ys+-.-:.````....``.--:/sh+/::::-....-----...........`.-.-.-:```...```.-````--"
print "\033[32m'                                          ./.````ss/---/+-             :o/+o+o++/::::--::--.--..:--//-:-:::--...-.````..````.`"
print "\033[32m'                                                 oy+---::+-            ...-:/-://oooooos+ooo+/+//+//::/:--."
print "\033[32m'                                                 .hs:-:+::+-            ....-.-````````....-..-..---..."
print "\033[32m'                                                  sy://so/:+-"
print "\033[32m'                                                  -h/ososo///.  "
print "\033[32m'                                                   oo+yyo/so/.``````.--...........-----.-.......`"
print "\033[32m'                                                   -s+yyso:+o-```````````````"
print "\033[32m'                                                    osssyoo:/o.               "
print "\033[32m'                                                    :o+osys+:o/                        .....-://oo/---////:.////:.////:."
print "\033[31m'                                                    .s/oyyyo+/o-                        ``..-.          TOUCAN "
print "\033[32m'                                                     -+/+yho+o++.                            `+o///---////:.////:.////:."
print "\033[32m'                                                     .+/+hhs//s:`                             "
print "\033[32m'                                                      //ohyys:oo`"
print "\033[32m'                                                      .s:ssyys:s:"
print "\033[32m'                                                        //+oyyy+/+"
print "\033[32m'                                                       `-o/oyyo+s+"
print "\033[32m'                                                        /ooshs:/s-  "                             
print "\033[32m'                                                        .o:oyho/oo   "                            
print "\033[32m'                                                        `//oshss+o    "                          
print "\033[32m'                                                         ./+ys++os"
print "\033[32m'                                                          `.+/os++                              The world is a jungle in general, and the"
print "\033[32m'                                                           `-//:-.                              networking game contributes many animals."
print "\033[32m'                                                                                                - RFC 826"
print "\033[32m'Written by: Collin Sullivan, a.k.a Splithor1zon\033[0m"

os.system("espeak 'Welcome to Toucan'")

class colors:

    Red ='\033[31m'

    Green ='\033[32m'

    Yellow ='\033[33m'

    Blue ='\033[34m'

    Pink ='\033[35m'

    Cyan ='\033[36m'

    White ='\033[37m'

    ENDC = '\033[0m'


time_current = time.strftime("%I:%M:%S")
logging.info('%s' % time_current)


date_current = time.strftime("%d/%m/%Y")
logging.info('%s' % date_current)


print colors.Yellow + """
Toucan is an Intrusion Detection System. Capabilities include scanning and defending hosts on a network by actively 
monitoring traffic for different types of known attacks by maleficent users. This program is not to be used on an
unauthorized network and the creator is not responsible for any damage done. Using this program means you understand 
and agree to these conditions.
\n""" + colors.ENDC

print time_current
print date_current


def print_toucan_1():

    print"""\033[32m                                                                                                                                                  
                                                                                                                                                                                                        
                                                                                                                                                                                                        
                                                                         ````````````                                                                                                                   
                                                              ``.....,,::;:::::::::::,,,......``                                                                                                        
                                                       `.,:,.,,,::;;;::,,::::::::::::::,,,,,,...,,..``                                                                                                  
                                                 ``,,:,,,:;::,,.....`.............,,,,,,,,,,,,,,,,,,,,,.`   ..,::`.                                                                                     
                                             `,,,,.,:;:::,,.....................``.......,,,,,,,,,,,,,,,,.'##+++'''++#:.                                                                                
                                         `.,,,,:;;:,,,,,,,,,.........,,,,...`````````````...,,,,,,,,,,,,,''++++++++++++++.                                                                              
                                      `,,,:;;;:,,,,,,,,,,,,,,,,,,,,,..............``````````....,,,,,,,:;'++#####++++'''+++`                                                                            
                                    .::;;;:,,,,,,,,,,:::::::::::,,,,,,,,,,,,,...........`````````...,,:;'++######+++++''++++,                                                                           
                                  ,:;;;;,,,,,,:::::::::::::::::::,,,,,,,,,,,,,,,,,,,,..........`````.,;;'.:########+++++''+++;                                                                          
                                .:;;;;:,,,,,,:::::::::::,,,,,,::,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.......:;'.`:#########+++++++'++;                                                                         
                               ;;;;::::,,,,,::,,,,,:::::::::::::,:,:::::::,,,,,,,,,,,,,,,,,,,,,,,,,,:';'``.;#########++++++'+++;                                                                        
                             .';;'+#######;,,,,,,,::,,,,:::::::::::::::::::::::::::,,,,,,,,,,,,,,,,,+++,.`..:'#########+++++'+++.                                                                       
                            ,''+##########+#,,,:,:,:::::::::::::::::::::::::::::::::::::::::::::::::+++.....,,;#########+++++++++                                                                       
                           ,+######@@@#####++,:,:::::::::::::::::::::::::::::::::::::::::::::::::::,+#+,.::;;,,:+########++++++++'                                                                      
                          .+##@@@###@#@#####+::,:::::::::::::::::::::::::::::::::::::::::::::::::::,##;,;'+++',::##########+++++++.                                                                     
                         .'###@##@@#########++:::::::::::::::::::::::::::::::;::::::::::::::::::::::##,,+';+'':,:###########+#+++++                                                                     
                        .+#@####@@########++++::::::;:::::;:::;:::;:::;:::::;;:::::::::::::::::::::;##,:+'#+++'::'########+#++++++#,                                                                    
                        +##@##@@##########++'':::::;;::::;;::;;:::;:::;:::::;;:::::;;:::;::::::::::;##,;+#+''#'::;+##########+#++++#                                                                    
                       ++#@#@@@#####@####++++;:::::;;;::;;;::;;::;;;;;;;;;;;;;;::::;::::;:::::;::::;##:'+'@@@';,:;+#############++++#`                                                                  
                      `+##@#@#####@#####+#+++;:::;;;;;;:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;::::::::::;#+:;+;'+'+,,,,+################++'                                                                  
                      +##########@##++++#++#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:;;;;;##:,+++++:..```;###############++#,                                                                 
                      +####################;;;;;;;;;;;;;;;;;;;;;::::::;;;;;;;;;;;;;;;;;;;;;;;;;;;;:;##;,,:;:,..`````.###############+++                                                                 
                     `+@@####@########+++;;;;;;;;;::::::,,,:::::::;;:::::::::::::::::::::;;;;;;;;;;;##':::,..````````,+##############+#;                                                                
                     ;#@###########+++''';;;;;'''+++++++++++'++'+++'++'+++'+++++++++'';;;;;;;;:::;;;+#;,..``..````````:+#############+##`                                                               
                     +#@#######+##+;;''++++++++++''+++'+++++'++'+'++''+++'''''''''''''''''''''''''''+#..``.````````  `.++#############+#+                                                               
                     ######++#';'+++++++++++++++++'++++'++++''+''+'+''+++''''''''''''''''';;;;'';:'###````````````` ```:+#############++#.                                                              
                     @###+''''+++++++++++++++++++++++++++++++'++++'+''+++'''+''''''''''''''''';;#####+``..`````````````.++#############+##                                                              
                     ###'''++++++++++++++++++++++++++++++++++++++++++++++'''++'++''''''''''';'#######:``````````````````;+################;                                                             
                    `@#''++';;;;;;''''+++++++++++++++#+#####+++++++++++++++'++'+++''''''''''+########```````````````````,+#################                                                             
                    ,@;+;`                             ```,:;'++++++++++++++++++++++'''''''+########````````````````````,+#################                                                             
                    `';.                                          `..,;'++++++++++++++++++++###@###..``````````````.````'+#################'                                                            
                     `                                                       ```..,;'+++++###@###'...```````````.`.`.,'++###################                                                            
                                                                                       ``,####+,,:,.`````````````,'++++++###################                                                            
                                                                                                ,:,.`````````.'++++++++#####################`                                                           
                                                                                                :,.```````.#++++++++#+#+#########+++++######:                                                           
                                                                                                ,,.`.:+##+++++++++++++##########++++++++++##'                                                           
                                                                                                `;+##+++++++++++++++++######+++++++++++++#+#+                                                           
                                                                                              ,++++++++++++++++++#++########+++++++++++++#+##                                                           
                                                                                           ,+++++++#++++++++++++++#########+++#++++++#++##+##`                                                          
                                                                                         ;++++++++++++++++++++++##########+++++++++++#+#+###+                                                           
                                                                                       `+++++++'++++++++#+##+###+#########+++#++##+++######+'                                                           
                                                                                      '#++'++++++++++++#++#################+##++############.                                                           
                                                                                     ++++'+++++++++####################################+####                                                            
                                                                                   `#+''+++##++#++#########################################.                                                            
                                                                                  .#++'++++#+++++#######+#+++#############################;                                                             
                                                                                 .#++'+++#+#++++#####+++##+++++##########################'   

                                                            TOUCAN SNIFFING WILL NOW COMMENSE (IPv4)                                        
                                                                                                                                                    
    \033[0m"""


def print_toucan_2():

    print"""\33[32m
                                                                                                                                                                                                        
                                                                                                                                                                                                        
                                                                                                                                                                                                        
                                                                                                                                                                                                        
                                                                         ````````````                                                                                                                   
                                                              ``.....,,::;:::::::::::,,,......``                                                                                                        
                                                       `.,:,.,,,::;;;::,,::::::::::::::,,,,,,...,,..``                                                                                                  
                                                 ``,,:,,,:;::,,.....`.............,,,,,,,,,,,,,,,,,,,,,.`   ..,::`.                                                                                     
                                             `,,,,.,:;:::,,.....................``.......,,,,,,,,,,,,,,,,.'##+++'''++#:.                                                                                
                                         `.,,,,:;;:,,,,,,,,,.........,,,,...`````````````...,,,,,,,,,,,,,''++++++++++++++.                                                                              
                                      `,,,:;;;:,,,,,,,,,,,,,,,,,,,,,..............``````````....,,,,,,,:;'++#####++++'''+++`                                                                            
                                    .::;;;:,,,,,,,,,,:::::::::::,,,,,,,,,,,,,...........`````````...,,:;'++######+++++''++++,                                                                           
                                  ,:;;;;,,,,,,:::::::::::::::::::,,,,,,,,,,,,,,,,,,,,..........`````.,;;'.:########+++++''+++;                                                                          
                                .:;;;;:,,,,,,:::::::::::,,,,,,::,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.......:;'.`:#########+++++++'++;                                                                         
                               ;;;;::::,,,,,::,,,,,:::::::::::::,:,:::::::,,,,,,,,,,,,,,,,,,,,,,,,,,:';'``.;#########++++++'+++;                                                                        
                             .';;'+#######;,,,,,,,::,,,,:::::::::::::::::::::::::::,,,,,,,,,,,,,,,,,+++,.`..:'#########+++++'+++.                                                                       
                            ,''+##########+#,,,:,:,:::::::::::::::::::::::::::::::::::::::::::::::::+++.....,,;#########+++++++++                                                                       
                           ,+######@@@#####++,:,:::::::::::::::::::::::::::::::::::::::::::::::::::,+#+,.::;;,,:+########++++++++'                                                                      
                          .+##@@@###@#@#####+::,:::::::::::::::::::::::::::::::::::::::::::::::::::,##;,;'+++',::##########+++++++.                                                                     
                         .'###@##@@#########++:::::::::::::::::::::::::::::::;::::::::::::::::::::::##,,+';+'':,:###########+#+++++                                                                     
                        .+#@####@@########++++::::::;:::::;:::;:::;:::;:::::;;:::::::::::::::::::::;##,:+'#+++'::'########+#++++++#,                                                                    
                        +##@##@@##########++'':::::;;::::;;::;;:::;:::;:::::;;:::::;;:::;::::::::::;##,;+#+''#'::;+##########+#++++#                                                                    
                       ++#@#@@@#####@####++++;:::::;;;::;;;::;;::;;;;;;;;;;;;;;::::;::::;:::::;::::;##:'+'@@@';,:;+#############++++#`                                                                  
                      `+##@#@#####@#####+#+++;:::;;;;;;:;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;::::::::::;#+:;+;'+'+,,,,+################++'                                                                  
                      +##########@##++++#++#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:;;;;;##:,+++++:..```;###############++#,                                                                 
                      +####################;;;;;;;;;;;;;;;;;;;;;::::::;;;;;;;;;;;;;;;;;;;;;;;;;;;;:;##;,,:;:,..`````.###############+++                                                                 
                     `+@@####@########+++;;;;;;;;;::::::,,,:::::::;;:::::::::::::::::::::;;;;;;;;;;;##':::,..````````,+##############+#;                                                                
                     ;#@###########+++''';;;;;'''+++++++++++'++'+++'++'+++'+++++++++'';;;;;;;;:::;;;+#;,..``..````````:+#############+##`                                                               
                     +#@#######+##+;;''++++++++++''+++'+++++'++'+'++''+++'''''''''''''''''''''''''''+#..``.````````  `.++#############+#+                                                               
                     ######++#';'+++++++++++++++++'++++'++++''+''+'+''+++''''''''''''''''';;;;'';:'###````````````` ```:+#############++#.                                                              
                     @###+''''+++++++++++++++++++++++++++++++'++++'+''+++'''+''''''''''''''''';;#####+``..`````````````.++#############+##                                                              
                     ###'''++++++++++++++++++++++++++++++++++++++++++++++'''++'++''''''''''';'#######:``````````````````;+################;                                                             
                    `@#''++';;;;;;''''+++++++++++++++#+#####+++++++++++++++'++'+++''''''''''+########```````````````````,+#################                                                             
                    ,@;+;`                             ```,:;'++++++++++++++++++++++'''''''+########````````````````````,+#################                                                             
                    `';.                                          `..,;'++++++++++++++++++++###@###..``````````````.````'+#################'                                                            
                     `                                                       ```..,;'+++++###@###'...```````````.`.`.,'++###################                                                            
                                                                                       ``,####+,,:,.`````````````,'++++++###################                                                            
                                                                                                ,:,.`````````.'++++++++#####################`                                                           
                                                                                                :,.```````.#++++++++#+#+#########+++++######:                                                           
                                                                                                ,,.`.:+##+++++++++++++##########++++++++++##'                                                           
                                                                                                `;+##+++++++++++++++++######+++++++++++++#+#+                                                           
                                                                                              ,++++++++++++++++++#++########+++++++++++++#+##                                                           
                                                                                           ,+++++++#++++++++++++++#########+++#++++++#++##+##`                                                          
                                                                                         ;++++++++++++++++++++++##########+++++++++++#+#+###+                                                           
                                                                                       `+++++++'++++++++#+##+###+#########+++#++##+++######+'                                                           
                                                                                      '#++'++++++++++++#++#################+##++############.                                                           
                                                                                     ++++'+++++++++####################################+####                                                            
                                                                                   `#+''+++##++#++#########################################.                                                            
                                                                                  .#++'++++#+++++#######+#+++#############################;                                                             
                                                                                 .#++'+++#+#++++#####+++##+++++##########################'  

                                                                    TOUCAN SNIFFING WILL NOW COMMENSE (IPv6)                                                            
                                                             
    """


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):

    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '\033[32m■\033[0m' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def get_mac_address(ip_address):

    response, unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address), \
        timeout=2, retry=2)
    for s, r in response:
        return r[Ether].src
    return None
    logging.info('Gateway Layer 2 address is: %s' % r[Ether].src)
    GATEWAY_MAC = "%s" % r[Ether].src

    
def get_mac_address_v6(ip_address):

    response, unanswered = srp(Ether(dst='33:33:00:00:00:02')/IPv6(dst="FF02::2")/ICMPv6ND_RS(code = 133), \
        timeout = 2, retry = 2)
    for s, r in response:
        return r[Ether].src
    return None
    logging.info('Gateway Layer 2 address is: %s' % r[Ether].src)
    GATEWAY_MAC = "%s" % r[Ether].src


def detect_unauth_arp(unauthorized_arp_packet):

    if unauthorized_arp_packet.haslayer(ARP) and unauthorized_arp_packet[Ether].src not in open('toucan_accept_list_arp.txt').read():

      print time.strftime("%I:%M:%S") + " " + "[!]Warning: Host not in ARP allowed group send an ARP packet"
      print time.strftime("%I:%M:%S") + " " + "Unauthorized ARP address: %s" % (unauthorized_arp_packet[Ether].src)


def detect_unauth_na(unauthorized_na_packet):

    if unauthorized_na_packet.haslayer(ICMPv6ND_NA) and unauthorized_na_packet[Ether].src not in open('toucan_accept_list_neighbadv.txt').read():

      print time.strftime("%I:%M:%S") + " " + "[!]Warning: Host not in Neighbor Advertisement allowed group send a NA packet"
      print time.strftime("%I:%M:%S") + " " + "Unauthorized NA address: %s" % (unauthorized_na_packet[Ether].src)


def detect_unauth_ra(unauthorized_ra_packet):

    if unauthorized_ra_packet.haslayer(ICMPv6ND_RA) and unauthorized_ra_packet[Ether].src not in open('toucan_accept_list_routeradv.txt').read():

      print time.strftime("%I:%M:%S") + " " + "[!]Warning: Host not in Router Advertisement allowed group sent a Router Advertisement"
      print time.strftime("%I:%M:%S") + " " + "Unauthorized RA address: %s" % (unauthorized_ra_packet[Ether].src)
      increment_counter()


def arp_network_range(iprange):

    logging.info('Sending ARPs to network range')
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=iprange), timeout=5)
    ip_collection = []
    eth_collection = []
    for snd, rcv in ans:
        host_ip_address = rcv.sprintf(r"%ARP.psrc%")
        host_eth_address = rcv.sprintf(r"%Ether.src%")
        logging.info('%s' % host_ip_address)
        logging.info('%s' % host_eth_address)
        ip_collection.append(host_ip_address)
        eth_collection.append(host_eth_address)

    print "Host List IP Addresses:"
    for host_ip in ip_collection:
        print host_ip
    print "Host List Ethernet Addresses:"
    for host_eth in eth_collection:
        print host_eth
    with open("toucan_hosts.txt", "w") as output:
        output.write(str(ip_collection))
        output.write(str(eth_collection))

        
def arp_display(packet):

    global attacker_L2
    global attacker_L3
    global victim_L3
    global victim_MAC

    if packet.haslayer(ARP):
      if packet.haslayer(ARP) and '%s' % (packet[Ether].src) in open('toucan_deny_list.txt').read():

          print time.strftime("%I:%M:%S") + " " + "ARP Request discovered from unauthorized host (in deny list) at: %s , %s" % (packet[ARP].psrc, packet[Ether].src)
          logging.info('ARP Request discovered from unauthorized host (in deny list) at: %s , %s' % (packet[ARP].psrc, packet[Ether].src))

      if packet.haslayer(ARP) and '%s' % (packet[Ether].src) not in open('toucan_accept_list.txt').read():

          print time.strftime("%I:%M:%S") + " " + "ARP Request discovered from unauthorized host (not in accept list) at: %s , %s" % (packet[ARP].psrc, packet[Ether].src)
          logging.info('ARP Request discovered from unauthorized host (not in accept list) at: %s , %s' % (packet[ARP].psrc, packet[Ether].src))

      if packet[ARP].op == 1: 

          logging.info('[1] ARP Request- %s is asking for L2 of %s' % (packet[ARP].psrc, packet[ARP].pdst))
          print time.strftime("%I:%M:%S") + " " + "\033[31m[1] ARP Request Ethernet Info: [Source] = %s + [Destination] = %s\033[0m" % (packet[Ether].src, packet[Ether].dst)
          return time.strftime("%I:%M:%S") + " " + '\033[31m[1] ARP Request- %s is asking for L2 of %s\033[0m' % (packet[ARP].psrc, packet[ARP].pdst)

      if packet[ARP].op == 1 and packet[ARP].psrc == GATEWAY_IP and packet[Ether].src != GATEWAY_MAC:

          return "\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m" % (packet[ARP].hwsrc)
          attacker_L2 = packet[ARP].hwsrc
          victim_L3 = packet[ARP].dst
          victim_MAC = packet[Ether].dst

      if packet[ARP].op == 1 and packet[ARP].psrc == GATEWAY_IP and packet[ARP].hwsrc != GATEWAY_MAC:

          print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m" % (packet[ARP].hwsrc)
          attacker_L2 = packet[ARP].hwsrc
          victim_L3 = packet[ARP].dst
          victim_MAC = packet[Ether].dst

      if packet[ARP].op == 2: 

          logging.info('[2] ARP Response- %s has layer 2 address: %s' % (packet[ARP].psrc, packet[ARP].hwsrc))
          print time.strftime("%I:%M:%S") + " " + "\033[33m[2] Reponse Ethernet Info: [Source] = %s + [Destination] = %s\033[0m" % (packet[Ether].src, packet[Ether].dst)
          return '\033[33m[2] ARP Response- %s has layer 2 address: %s\033[0m' % (packet[ARP].psrc, packet[ARP].hwsrc)

      if packet[ARP].op == 2 and '%s' % (packet[Ether].src) in open('toucan_deny_list.txt').read():

          print time.strftime("%I:%M:%S") + " " + "ARP Reply discovered from unauthorized host at: %s , %s" % (packet[ARP].psrc, packet[ARP.pdst])
          logging.info('ARP Reply discovered from unauthorized host at: %s , %s' % (packet[ARP].psrc, packet[ARP.pdst]))

      if packet[ARP].op == 2 and '%s' % (packet[Ether].src) not in open('toucan_accept_list.txt').read():

          print time.strftime("%I:%M:%S") + " " + "ARP Response discovered from unauthorized host (not in accept list) at: %s , %s" % (packet[ARP].psrc, packet[Ether].src)
          logging.info('ARP Response discovered from unauthorized host at: %s , %s' % (packet[ARP].psrc, packet[Ether].src))

      if packet[ARP].op == 2 and packet[ARP].psrc == GATEWAY_IP and packet[Ether].src != GATEWAY_MAC:

          print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m" % (packet[ARP].hwsrc)
          os.system("espeak 'WARNING GATEWAY IMPERSONATION DETECTED from %s'" % (packet[ARP].hwsrc)) 
          attacker_L2 = packet[ARP].hwsrc
          victim_L3 = packet[ARP].dst
          victim_MAC = packet[Ether].dst

      if packet[ARP].op == 2 and packet[ARP].psrc == GATEWAY_IP and packet[ARP].hwsrc != GATEWAY_MAC:

          print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: GATEWAY IMPERSONTATION DETECTED. POSSIBLE MITM ATTACK FROM %s\033[31m" % (packet[ARP].hwsrc)
          attacker_L2 = packet[ARP].hwsrc
          victim_L3 = packet[ARP].dst
          victim_MAC = packet[Ether].dst
      

def na_packet_discovery(neighbor_adv_packet):

  if neighbor_adv_packet.haslayer(IPv6) and neighbor_adv_packet.haslayer(ICMPv6ND_NA):

    print time.strftime("%I:%M:%S") + " " + "[NA] Neighbor advertisement discovered: %s" % (neighbor_adv_packet.summary())
    print time.strftime("%I:%M:%S") + " " + "[NA-Ether] Neighbor advertisement layer 2 information: Source- %s, Destination- %s" % (neighbor_adv_packet[Ether].src, neighbor_adv_packet[Ether].dst)
    print time.strftime("%I:%M:%S") + " " + '[NA] Neighbor advertisement layer 3 information: Source- %s, Destination- %s ' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst)  
    logging.info('Neighbor advertisement source: %s, destination: %s' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst))

  if neighbor_adv_packet.haslayer(ICMPv6ND_NA) and neighbor_adv_packet[Ether].src in open('toucan_deny_list.txt').read():

      print time.strftime("%I:%M:%S") + " " + "Neighbor advertisement discovered from unauthorized host (in deny list) at: %s" % (neighbor_adv_packet[Ether].src)
      logging.info('Neighbor advertisement discovered from unauthorized host at: %s' % (neighbor_adv_packet[Ether].src))

  if neighbor_adv_packet.haslayer(ICMPv6ND_NA) and neighbor_adv_packet[Ether].src not in open('toucan_accept_list.txt').read():

      print time.strftime("%I:%M:%S") + " " + "Neighbor advertisement discovered from unauthorized host (not in accept list) at: %s" % (neighbor_adv_packet[Ether].src)
      logging.info('Neighbor advertisement discovered from unauthorized host at: %s' % (neighbor_adv_packet[Ether].src))


def na_packet_discovery_v6(neighbor_adv_packet):

  if neighbor_adv_packet.haslayer(IPv6) and neighbor_adv_packet.haslayer(ICMPv6ND_NA):

    print time.strftime("%I:%M:%S") + " " + "[NA] Neighbor advertisement discovered: %s" % (neighbor_adv_packet.summary())
    print time.strftime("%I:%M:%S") + " " + "[NA-Ether] Neighbor advertisement layer 2 information: Source- %s, Destination- %s" % (neighbor_adv_packet[Ether].src, neighbor_adv_packet[Ether].dst)
    print time.strftime("%I:%M:%S") + " " + '[NA] Neighbor advertisement layer 3 information: Source- %s, Destination- %s ' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst)  
    logging.info('Neighbor advertisement source: %s, destination: %s' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[IPv6].dst))

  if neighbor_adv_packet[IPv6].src == GATEWAY_IP and neighbor_adv_packet["ICMPv6NDOptDstLLAddr"].lladdr != GATEWAY_MAC:

    print time.strftime("%I:%M:%S") + " " + '\033[31m[!]WARNING: IPv6 GATEWAY IMPERSONATION DETECTED. POSSIBLE MITM ATTACK FROM: %s (L2): %s\033[0m' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[Ether].src)

  if neighbor_adv_packet[IPv6].src == host_ip_address in ip_collection and neighbor_adv_packet["ICMPv6NDOptDstLLAddr"].lladdr != host_eth_address in eth_collection:

    print time.strftime("%I:%M:%S") + " " + '\033[31m[!]WARNING: IPv6 GATEWAY IMPERSONATION DETECTED. POSSIBLE MITM ATTACK FROM: %s (L2): %s\033[0m' % (neighbor_adv_packet[IPv6].src, neighbor_adv_packet[Ether].src)

  if neighbor_adv_packet.haslayer(ICMPv6ND_NA) and neighbor_adv_packet[ICMPv6NDOptDstLLAddr].lladdr in open('toucan_deny_list.txt').read():

    print time.strftime("%I:%M:%S") + " " + "Neighbor Advertisement disovereed from host in deny list: %s " % (["ICMPv6NDOptDstLLAddr"].lladdr)
    logging.info('ARP Request discovered from unauthorized host at: %s ' % (["ICMPv6NDOptDstLLAddr"].lladdr))

  if neighbor_adv_packet.haslayer(ICMPv6ND_NA) and neighbor_adv_packet[Ether].src in open('toucan_deny_list.txt').read():

    print time.strftime("%I:%M:%S") + " " + "Neighbor advertisement discovered from unauthorized host (in deny list) at: %s" % (neighbor_adv_packet[Ether].src)
    logging.info('Neighbor advertisement discovered from unauthorized host at: %s' % (neighbor_adv_packet[Ether].src))

  if neighbor_adv_packet.haslayer(ICMPv6ND_NA) and neighbor_adv_packet[Ether].src not in open('toucan_accept_list.txt').read():

    print time.strftime("%I:%M:%S") + " " + "Neighbor advertisement discovered from unauthorized host (not in accept list) at: %s" % (neighbor_adv_packet[Ether].src)
    logging.info('Neighbor advertisement discovered from unauthorized host at: %s' % (neighbor_adv_packet[Ether].src))


def ns_packet_discovery(neighbor_sol_packet):

  if neighbor_sol_packet.haslayer(IPv6) and neighbor_sol_packet.haslayer(ICMPv6ND_NS):

    print time.strftime("%I:%M:%S") + " " + "\033[35m[NS] Neighbor solicitation discovered: %s\033[0m" % (neighbor_sol_packet.summary())
    print time.strftime("%I:%M:%S") + " " + "[NS-Ether] Neighbor solicitation layer 2 information: Source- %s, Destination- %s" % (neighbor_sol_packet[Ether].src, neighbor_sol_packet[Ether].dst)    
    print time.strftime("%I:%M:%S") + " " + '\033[35m[NS] Neighbor solicitation source: %s, destination: %s\033[0m' % (neighbor_sol_packet[IPv6].src, neighbor_sol_packet[IPv6].dst)  
    logging.info('Neighbor solicitation source: %s, destination: %s' % (neighbor_sol_packet[IPv6].src, neighbor_sol_packet[IPv6].dst))

  if neighbor_sol_packet.haslayer(ICMPv6ND_NS) and neighbor_sol_packet[Ether].src in open('toucan_deny_list.txt').read():

    print time.strftime("%I:%M:%S") + " " + "Neighbor solicitation discovered from unauthorized host at: %s" % (neighbor_sol_packet[Ether].src)
    logging.info('Neighbor solicitation discovered from unauthorized host at: %s' % (neighbor_sol_packet[Ether].src))

  if neighbor_sol_packet.haslayer(ICMPv6ND_NS) and neighbor_sol_packet[Ether].src not in open('toucan_accept_list.txt').read():

    print time.strftime("%I:%M:%S") + " " + "Neighbor solicitation discovered from unauthorized host (not in accept list) at: %s" % (neighbor_sol_packet[Ether].src)
    logging.info('Neighbor solicitation discovered from unauthorized host at: %s' % (neighbor_sol_packet[Ether].src))


def detect_deauth(deauth_packet):

    if deauth_packet.haslayer(Dot11) and deauth_packet.haslayer(Dot11Deauth):

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!] DEAUTH DETECTED: %s\033[0m" % (deauth_packet.summary())
        print time.strftime("%I:%M:%S") + " " + "\033[31m[!] Deauthentication Detected from: %s through default gateway at %s\033[0m" % (deauth_packet[Dot11].addr1, deauth_packet[Dot11].addr2)
        logging.warning('Deauth detected from %s' % (deauth_packet[Dot11].addr1))
        logging.warning('Sending option to repond to deauthentication...')

    if deauth_packet.haslayer(Dot11Deauth) and deauth_packet[Dot11Deauth].addr1 not in open('toucan_accept_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!]Deauthenticaion packet detected from host not in accept group. Address: %s" % (deauth_packet[Dot11Deauth].addr1)
        logging.warning('Deauthenticaion packet detected from host not in accept group. Address: %s' % (deauth_packet[Dot11Deauth].addr1))

    if deauth_packet.haslayer(Dot11Deauth) and deauth_packet[Dot11Deauth].addr1 in open('toucan_deny_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!]Deauthenticaion packet detected from host not in deny group. Address: %s" % (deauth_packet[Dot11Deauth].addr1)
        logging.warning('Deauthenticaion packet detected from host not in deny group. Address: %s' % (deauth_packet[Dot11Deauth].addr1))


def detect_router_advertisement_flood(ra_packet_flood):

    global ra_counter

    if ra_counter > 10 and ra_packet_flood[Ether].src not in open('toucan_accept_list'):

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: Over 10 router advertisements from unauthorized hosts have been detected. Possible Flood...\033[0m"
        logging.warning('[!]WARNING: Over 10 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')

    if ra_counter > 200 and ra_packet_flood[Ether].src not in open('toucan_accept_list'):

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: Over 200 router advertisements from unauthorized hosts have been detected. Flood WARNING...\033[0m"
        logging.warning('[!]WARNING: Over 200 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')

    if ra_counter > 500 and ra_packet_flood[Ether].src not in open('toucan_accept_list'):

        print time.strftime("%I:%M:%S") + " " + "\033[31m[!]WARNING: Over 500 router advertisements from unauthorized hosts have been detected. Flood WARNING...\033[0m"
        logging.warning('[!]WARNING: Over 500 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')


    if ra_packet_flood.haslayer(IPv6) and ra_packet_flood.haslayer(ICMPv6ND_RA):

        print time.strftime("%I:%M:%S") + " " + "\033[32m[RA]Router advertisement discovered: %s\033[0m" % (ra_packet_flood.summary())   
        print time.strftime("%I:%M:%S") + " " + '[RA] Router advertisement discovered from %s with Layer 2 address: %s' % (ra_packet_flood[IPv6].src, ra_packet_flood[Ether].src) 
        logging.info('Router advertisement from %s with Layer 2 address: %s' % (ra_packet_flood[IPv6].src, ra_packet_flood[Ether].src))

    if ra_packet_flood.haslayer(ICMPv6ND_RA) and ra_packet_flood[Ether].src in open('toucan_deny_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Router advertisement discovered from unauthorized host (in deny list) at: %s" % (neighbor_sol_packet[Ether].src)
        logging.info('Router advertisement discovered from unauthorized host at: %s' % (neighbor_sol_packet[Ether].src))
        increment_counter()

    if ra_packet_flood.haslayer(ICMPv6ND_RA) and ra_packet_flood[Ether].src not in open('toucan_accept_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Router advertisement discovered from unauthorized host (not in accept list) at: %s" % (neighbor_sol_packet[Ether].src)
        logging.info('Router advertisement discovered from unauthorized host at: %s' % (neighbor_sol_packet[Ether].src))
        increment_counter()

    if ra_packet_flood[Ether].src != GATEWAY_MAC:

        print """\033[31m
        [RA] POSSIBLE MALICIOUS ROUTER ADVERTISEMENT DISCOVERED: 
        Layer 2 Source: %s
        Layer 3 Source: %s 
        Prefix: %s
        lladdr: %s
        \033[0m""" % (ra_packet_flood[Ether].src, ra_packet_flood[IPv6].src, ra_packet_flood[ICMPv6NDOptPrefixInfo].prefix, ra_packet_flood[ICMPv6NDOptSrcLLAddr].lladdr)


def detect_router_advertisement_packet(ra_packet):

    global ra_counter

    if ra_counter > 10 and ra_packet[Ether].src not in open('toucan_accept_list.txt'):

        print "\033[31m[!]WARNING: Over 10 router advertisements from unauthorized hosts have been detected. Flood warning initiated...\033[0m"
        print "meep moop"
        logging.warning('[!]WARNING: Over 10 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')

    if ra_counter > 200 and ra_packet[Ether].src not in open('toucan_accept_list.txt'):

        print "\033[31m[!]WARNING: Over 200 router advertisements from unauthorized hosts have been detected. Flood warning initiated...\033[0m"
        logging.warning('[!]WARNING: Over 200 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')

    if ra_counter > 500 and ra_packet[Ether].src not in open('toucan_accept_list.txt'):

        print "\033[31m[!]WARNING: Over 500 router advertisements from unauthorized hosts have been detected. Flood warning initiated...\033[0m"
        logging.warning('[!]WARNING: Over 500 router advertisements from unauthorized hosts have been detected. Flood warning initiated...')

    if ra_packet.haslayer(IPv6) and ra_packet.haslayer(ICMPv6ND_RA):

        print time.strftime("%I:%M:%S") + " " + "\033[32m[RA]Router advertisement discovered: %s\033[0m" % (ra_packet.summary())   
        print time.strftime("%I:%M:%S") + " " + '\033[33m[RA] Router advertisement discovered from %s with Layer 2 address: %s\033[0m' % (ra_packet[IPv6].src, ra_packet[Ether].src) 
        logging.info('Router advertisement from %s with Layer 2 address: %s' % (ra_packet[IPv6].src, ra_packet[Ether].src))  

    if ra_packet.haslayer(ICMPv6ND_RA) and ra_packet[Ether].src in open('toucan_deny_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Router advertisement discovered from unauthorized host at: %s" % (ra_packet[Ether].src)
        logging.info('Router advertisement discovered from unauthorized host at: %s' % (ra_packet[Ether].src))
        increment_counter()

    if ra_packet.haslayer(ICMPv6ND_RA) and ra_packet[Ether].src not in open('toucan_accept_list.txt').read():

        print time.strftime("%I:%M:%S") + "" + "Router advertisement discovered from unauthorized host (not in accept list) at: %s" % (ra_packet[Ether].src)
        logging.info('Router advertisement discovered from unauthorized host (not in accept list) at: %s' % (ra_packet[Ether].src))
        increment_counter()


def detect_router_solicitation(rs_packet):

    if rs_packet.haslayer(IPv6) and rs_packet.haslayer(ICMPv6ND_RS):

      print time.strftime("%I:%M:%S") + " " + "\033[34m[RS]Router solicitation discovered: %s\033[0m" % (rs_packet.summary())
      print time.strftime("%I:%M:%S") + " " + '\033[34m[RS] Router solicitation discovered from %s with Layer 2 address: %s\033[0m' % (rs_packet[IPv6].src, rs_packet[Ether].src) 
      logging.info('Router solicitation from %s with Layer 2 address: %s' % (rs_packet[IPv6].src, rs_packet[Ether].src))

    if rs_packet.haslayer(ICMPv6ND_RS) and rs_packet[Ether].src in open('toucan_deny_list.txt').read():

      print time.strftime("%I:%M:%S") + " " + "\033[34m[!]Router solicitation discovered from unauthorized host (in deny list) at: %s" % (rs_packet[Ether].src)
      logging.info('Router solicitation discovered from unauthorized host at: %s' % (rs_packet[Ether].src))

    if rs_packet.haslayer(ICMPv6ND_RS) and rs_packet[Ether].src not in open('toucan_accept_list.txt').read():

      print time.strftime("%I:%M:%S") + " " + "\033[34m[!]Router solicitation discovered from unauthorized host (not in accept list) at: %s" % (rs_packet[Ether].src)
      logging.info('Router solicitation discovered from unauthorized host (not in accept list) at: %s' % (rs_packet[Ether].src))  


def detect_syn_scan(syn_packet):

    if syn_packet.haslayer(TCP) and syn_packet[TCP].flags == "S":

        print "________________________________________________"
        print"\n"
        print "------------------------------------------------"
        print "Syn discovered"
        print "------------------------------------------------"
        print "\n"
        print "L2 Address: %s" % (syn_packet[Ether].src)
        print "------------------------------------------------"
        print "Source Port: %s" % (syn_packet[TCP].sport)
        print "Destination Port: %s" % (syn_packet[TCP].dport)
        print "------------------------------------------------"
        print "Source L3: %s" % (syn_packet[IP].src)
        print "Destination L3: %s" % (syn_packet[IP].dst) 
        print "------------------------------------------------"
        print "________________________________________________"

    if syn_packet.haslayer(TCP) and syn_packet[TCP].flags == "S" and syn_packet[TCP].dport == "22" or syn_packet[Ether].src in open('toucan_deny_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Possible SYN scan discovered from %s, host is probing SSH" % (syn_packet[IP].src)
        print syn_packet.summary()

    if syn_packet.haslayer(TCP) and syn_packet[TCP].flags == "S" and syn_packet[TCP].dport == "23" or syn_packet[Ether].src in open('toucan_deny_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Possible SYN scan discovered from %s, host is probing Telnet" % (syn_packet[IP].src)
        print syn_packet.summary()

    if syn_packet.haslayer(TCP) and syn_packet[TCP].flags == "S" and syn_packet[TCP].dport == "22" or syn_packet[Ether].src not in open('toucan_accept_list.txt').read():

        print time.strftime("%I:%M:%S") + " " + "Possible SYN scan discovered from %s, host is probing SSH" % (syn_packet[IP].src)
        print syn_packet.summary()

    if syn_packet.haslayer(TCP) and syn_packet[TCP].flags == "S" and syn_packet[TCP].dport == "23" or syn_packet[Ether].src not in open('toucan_accept_list.txt').read():

        print "Possible SYN scan discovered from %s, host is probing Telnet" % (syn_packet[IP].src)
        print syn_packet.summary()


def defensive_arps(GATEWAY_IP, GATEWAY_MAC, victim_L3, victim_MAC):

    un_poison_victim = ARP()
    un_poison_victim.op = 2
    un_poison_victim.psrc = GATEWAY_IP
    un_poison_victim.pdst = victim_L3
    un_poison_victim.hwsrc = GATEWAY_MAC

    un_poison_gateway = ARP()
    un_poison_gateway.op = 2
    un_poison_gateway.psrc = victim_L3
    un_poison_gateway.pdst = GATEWAY_IP
    un_poison_gateway.hwsrc = victim_MAC

    send(un_poison_victim)
    send(un_poison_gateway)

    time.sleep(2)

    print "Sent defensive ARP to restore %s" % victim_L3
    print "Sent defensive ARP to restore %s" % GATEWAY_IP


def un_poison_range(n_range, GATEWAY_IP, GATEWAY_MAC):

    logging.info('Restoring whole subnet')
    un_poison_range = ARP()
    un_poison_range.op = 2
    un_poison_range.psrc = GATEWAY_IP
    un_poison_range.hwsrc = GATEWAY_MAC
    un_poison_range.pdst = n_range
    send(un_poison_range)
    time.sleep(2)


def increment_counter():

  global ra_counter
  ra_counter += 1


def defensive_deauth(GATEWAY_MAC, Attacker_Deauth_Layer2, deauth_interface):

  conf.iface = deauth_interface
  bssid = GATEWAY_MAC 
  count = 20
  conf.verb = 0 
  packet = RadioTap()/Dot11(type=0, subtype=12, addr1=Attacker_Deauth_Layer2, addr2=bssid, addr3=bssid)/Dot11Deauth(reason=7) 
  logging.info('Intruder at %s is being kicked off network' % Attacker_Deauth_Layer2)

  for n in range(int(count)):

    sendp(packet)
    print '\033[32mRemoving malicious host at with Layer 2 address:' + Attacker_Deauth_Layer2 + ' off of network.\033[0m'

def scan_network_bssids(pkt) :

  ap_list = []
  if pkt.haslayer(Dot11) :
        if pkt.type == 0 and pkt.subtype == 8 :
            if pkt.addr2 not in ap_list :
                ap_list.append(pkt.addr2)
                print "\033[33mAP MAC:\033[0m\033[31m %s \033[0m\033[33mBSSID:\033[31m %s " %(pkt.addr2, pkt.info)

                
#For Multithreading

#These all use prn to use the proper above function on trigger

def detect_bad_arps():

  sniff(iface="%s" % interface, prn = detect_unauth_arp, count = 0)


def detect_bad_na():

  sniff(iface="%s" % interface, prn = detect_unauth_na)


def detect_bad_ra():

  sniff(iface="%s" % interface, prn = detect_unauth_ra)


def sniff_arps():

  sniff(iface = "%s" % interface, prn = arp_display, count = 0)


def sniff_networks():

    sniff(iface="%s" % wifi_interface, prn = scan_network_bssids)


def sniff_deauth():

  sniff(iface="%s" % wifi_interface, prn = detect_deauth)


def sniff_ns():

  sniff(iface="%s" % interface, prn = ns_packet_discovery) 


def sniff_na():

  sniff(iface="%s" % interface, prn = na_packet_discovery)


def sniff_na_ipv6():

  sniff(iface="%s" % interface, prn = na_packet_discovery_v6)


def sniff_ra():

  sniff(iface="%s" % interface, prn = detect_router_advertisement_packet)

  global ra_counter


def sniff_ra_v6_detect_flood():

  sniff(iface="%s" % interface, prn = detect_router_advertisement_flood)  


def sniff_syn_scan():

    sniff(iface = "%s" % interface, prn = detect_syn_scan)


def sniff_router_sol():

  sniff(iface = "%s" % interface, prn = detect_router_solicitation)


if __name__ == '__main__':

    l2_deny_list = []
    l3_deny_list = []
    ra_counter = 0
    attacker_L2 = ''    
    attacker_L3 = ''    
    victim_MAC = '' 
    victim_L3 = ''  
    RA_attacker_L3 = '' 
    RA_attacker_L2 = '' 

    GATEWAY_IP = raw_input("\033[33mEnter your Gateway Layer 3 Address: \033[0m")   

    logging.info('Gateway IP: %s' % GATEWAY_IP) 

    interface = raw_input("\033[32m\nEnter your Network Interface: \033[0m")    

    logging.info('Interface: %s' % interface)   

    n_range = raw_input("\033[31m\nEnter your network range to defend (in format 10.0.0.1/24): \033[0m")    

    logging.info('Network range to defend: %s' % n_range)

    print "\n"
    
    input_one = raw_input("""\033[35m
____________________________________________________________
____________________________________________________________
-                                                          -
- Fellow Toucan, are you defending an IPv4 or IPv6 network?-
-                                                          -
-                                                          -
- 1. IPv4                                                  -
- 2. IPv6                                                  -
____________________________________________________________
____________________________________________________________
\033[0m\n""")


    input_two = raw_input("""\033[35m
____________________________________________________________
____________________________________________________________
-                                                          -
Fellow Toucan, are you sniffing for deauthentication frames?
- 
-                                                          - 
-                                                          -
- 1. Yes                                                   -
- 2. No                                                    -
____________________________________________________________
____________________________________________________________
\033[0m\n""")


    if input_one == "1" or "yes" or "Yes" or "Y" or "y":
        GATEWAY_MAC = get_mac_address(GATEWAY_IP)

    if input_one == "2" or "no" or "No" or "N" or "n":
        GATEWAY_MAC = get_mac_address_v6(GATEWAY_IP)

    elif answer !="":
    
        print("\033[35m[!]Not Valid Option...\033[0m") 

        print("exiting...")

        sys.exit()

    if input_two == "1":

        wifi_interface = raw_input("Please enter your wireless interface to sniff on: ")    
        subprocess.Popen(['sudo','ifconfig',wifi_interface,'down']) 
        print "Shut %s down...\n" % wifi_interface 
        subprocess.Popen(['sudo','iwconfig',wifi_interface,'mode','monitor'])
        print "Placing %s into monitor mode...\n" % wifi_interface
        subprocess.Popen(['sudo','ifconfig',wifi_interface,'up']) 
        print "%s is now up and in monitor mode...\n" % wifi_interface

    elif input_two == "2":
        print "Ok"
    
    print colors.Red + "[*] Gateway Locked in..." 
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)

    print colors.Yellow + "[*] Interface configured..."
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)  

    print colors.Green +"[*] Network Range set..."
    print_progress(iteration = 100, total = 100)
    time.sleep(.4)

    print colors.Pink +"[*] Commensing..." + colors.ENDC
    print_progress(iteration = 100, total = 100)

    GATEWAY_MAC = get_mac_address(GATEWAY_IP)

    print colors.Red + "\n [*] Gateway %s is locked in at %s" % (GATEWAY_IP, GATEWAY_MAC) + colors.ENDC

    answer = True
    
    while answer:
        
    
        answer =raw_input("""\033[33m
        ____________________________________
        ____________________________________
         -           TOUCAN MENU           -
         It's a menu... but not for toucans
        ____________________________________
        ____________________________________
        - [1] Scan for hosts to protect    -
        - [2] Start Monitoring (IPv4)      -
        - [3] Start Monitoring (IPv6)      -
        - [4] Deauthenticate Attacker      -
        - [5] Send Defensive ARPs          -
        - [6] Send Def ARPs to Subnet      -
        - [7] Monitor for networks         -   
        - [8] Create Deny List             -      
        - [9] Create Accept List           -
        - [10] Create ARP List             -
        - [11] Create NA List              -
        - [12] Create RA List              -
        - [13] Exit                        -
        ____________________________________
        ____________________________________
        
        Please select an option: \033[0m""") 
    
        if answer =="1": 
          
          print "\033[35m[*]Sending ARPs to scan network range...\033[0m"
          network_range = arp_network_range(n_range)


        elif answer =="2":

            os.system('cls' if os.name == 'nt' else 'clear')
            try:

                Thread(target = print_toucan_1).start()
                Thread(target = sniff_arps).start()                            
                Thread(target = sniff_ns).start()           
                Thread(target = sniff_na).start()           
                Thread(target = sniff_ra).start() 
                Thread(target = sniff_router_sol).start()
                Thread(target = detect_bad_arps).start()
                Thread(target = detect_bad_na).start()
                Thread(target = detect_bad_ra).start()


            except KeyboardInterrupt:

                 thread.exit()


        elif answer =="3":

            os.system('cls' if os.name == 'nt' else 'clear')
            try:

                Thread(target = print_toucan_2).start()
                Thread(target = sniff_arps).start()                            
                Thread(target = sniff_ns).start()           
                Thread(target = sniff_na_ipv6).start()           
                Thread(target = sniff_ra_v6_detect_flood).start()
                Thread(target = sniff_syn_scan).start() 
                Thread(target = sniff_router_sol).start()
                Thread(target = detect_bad_arps).start()
                Thread(target = detect_bad_na).start()
                Thread(target = detect_bad_ra).start()

            except KeyboardInterrupt:

                sys.exit()
                
    
        elif answer =="4":
            
            deauth_interface = raw_input("Enter the interface you want to use (must be in monitor mode): ")
            GATEWAY_MAC = raw_input("Enter L2 of Dfeault Gateway: ")
            DeauthAttacker = raw_input("Please enter attacker's layer 3 address: ")
            Attacker_Deauth_Layer2 = get_mac_address(DeauthAttacker)
            print "Sending Deauthentication Packets to %s " % (Attacker_Deauth_Layer2)
            defensive_deauth(GATEWAY_MAC, Attacker_Deauth_Layer2, deauth_interface)


        elif answer == "5":

            defensive_arps()


        elif answer == "6":

            n_range = raw_input("Enter subnet to unpoison (in format 10.0.0.1/24): \n")
            GATEWAY_MAC = raw_input("Enter gateway mac address: ")
            un_poison_range(n_range, GATEWAY_IP, GATEWAY_MAC)


        elif answer == "7":

            wifi_interface = raw_input("Please enter your wireless interface to sniff on: ")    
            subprocess.Popen(['sudo','ifconfig',wifi_interface,'down'])
            print "Shut %s down...\n" % wifi_interface 
            subprocess.Popen(['sudo','iwconfig',wifi_interface,'mode','monitor'])
            print "Placing %s into monitor mode...\n" % wifi_interface
            subprocess.Popen(['sudo','ifconfig',wifi_interface,'up']) 
            print "%s is now up and in monitor mode...\n" % wifi_interface
            sniff_networks()


        elif answer == "8":

                while True:
                    l2_deny_list = raw_input("Layer 2 Adresses you want to monitor for: (type exit to escape) ")
                    fd = open("toucan_deny_list.txt","a")
                    fd.write(l2_deny_list + "\n")
                    logging.info("Populating deny list...")
                    if l2_deny_list == "exit":
                      break


        elif answer == "9":

                  while True:

                    l2_accept_list = raw_input("Enter all L2 Addresses you want to allow: (type exit to escape)")
                    fd = open("toucan_accept_list.txt","a")
                    fd.write(l2_accept_list+ "\n")
                    logging.info("Populating accept list...")
                    if l2_accept_list == "exit":

                      break

                        
        elif answer == "10":

                  while True:

                    l2_accept_list = raw_input("Enter all L2 Addresses you want to allow: (type exit to escape)")
                    fd = open("toucan_accept_list_arp.txt","a")
                    fd.write(l2_accept_list+ "\n")
                    logging.info("Populating accept list...")
                    if l2_accept_list == "exit":
                      
                      break
                        
        elif answer == "11":

                  while True:

                    l2_accept_list = raw_input("Enter all L2 Addresses you want to allow: (type exit to escape)")
                    fd = open("toucan_accept_list_neighbadv.txt","a")
                    fd.write(l2_accept_list+ "\n")
                    logging.info("Populating accept list...")
                    if l2_accept_list == "exit":
                      
                      break
                        
        elif answer == "12":

                  while True:

                    l2_accept_list = raw_input("Enter all L2 Addresses you want to allow: (type exit to escape)")
                    fd = open("toucan_accept_list_routeradv.txt","a")
                    fd.write(l2_accept_list+ "\n")
                    logging.info("Populating accept list...")
                    if l2_accept_list == "exit":
                      
                      break
                      
        elif answer =="13":

          print("\n\033[35m Exiting...\033[0m") 
          answer = None
          sys.exit()

    
        elif answer !="":
    
          print("\033[35m[!]Not Valid Option...\033[0m") 
          print("exiting...")
          sys.exit()

