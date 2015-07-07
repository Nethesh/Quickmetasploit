#!/usr/bin/python2.7
from collections import defaultdict
import cmd 
import subprocess
import sys
import time
import socket
import fcntl
import struct

DEFAULT_MODULE = 'multi_handler'

###########################################################################################################################################################################Adding Colours 
class colours:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
#########################################################################################################################################################################################
########################################################################################################################################################Used for getting local ip address
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
#######################################################################################################################################################################################
default_variables = frozenset('iface module'.split())
module_variables = defaultdict(lambda : default_variables)
module_variables.update({module: default_variables | other_variables for module, other_variables in
    {'exploit/multi/handler': {'payload', 'lhost', 'lport'},
    'auxiliary/scanner/smb/smb_login': {'rhosts', 'rport'},
    'auxiliary/scanner/rservices/rlogin_login': {'rhosts', 'rport', 'username', 'fromuser'},
    'auxiliary/scanner/snmp/snmp_enum': {'rhosts', 'rport', 'snmpversion', 'community'}
    }.items()})

short_module_names = {'smb_login': 'auxiliary/scanner/smb/smb_login',
                      'multi_handler': 'exploit/multi/handler',
                      'rlogin_login': 'auxiliary/scanner/rservices/rlogin_login',
                      'snmp_enum': 'auxiliary/scanner/snmp/snmp_enum'
                     }
class Handler(cmd.Cmd):
    lport = ''
    payload = ''
    lhost = ''
    iface = 'eth0'
    module = short_module_names[DEFAULT_MODULE]
    rhosts = ''
    rhost = ''
    rport = ''
    username = ''
    fromuser = 'root'
    community = 'public'
    snmpversion = '1'
#####################################################################################################################################################Possible strings for tab completetion
    possible_modules = short_module_names.keys()
    possible_snmpversion = ('1' ,'2c')
    possible_community = ('public' , 'private' , 'admin' , 'CISCO' , 'system' , 'switch' , 'secret')
    possible_usernames = ('foobar' , 'root' , 'admin' , 'sysadmin')
    possible_payloads = ('windows/meterpreter/reverse_tcp' , 'linux/shell/revserse_tcp')
#########################################################################################################################################################################################
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.lhost = get_ip_address(self.iface)
        self.variables = module_variables[self.module]

    def do_set(self, line):
        """Use Tab To Show Variables You Can Set"""
        try:
            firstvalue, secondvalue = line.split()
            if firstvalue == 'module':
                module = secondvalue = short_module_names[secondvalue]
                self.variables = module_variables[module]
            setattr(self, firstvalue, secondvalue)
        except ValueError:
            print colours.RED + "==========================================" + colours.WHITE
            print colours.BLUE + "Please choose a option and a value to set!" + colours.WHITE
            print colours.RED + "==========================================" + colours.WHITE
            
###################################################################################################################################################################Autocompletion shitt
    def complete_set(self, text, line, begidx, endidx):
        cmdtokens = line.split(' ')[:-1]
        if cmdtokens == ['set']:
            return [v for v in self.variables if v.startswith(text)]
        elif cmdtokens == ['set', 'module']:
            return [m for m in self.possible_modules if m.startswith(text)]
        elif cmdtokens == ['set', 'snmpversion']:
            return [g for g in self.possible_snmpversion if g.startswith(text)]
        elif cmdtokens == ['set', 'community']:
            return [f for f in self.possible_community if f.startswith(text)]
        elif cmdtokens == ['set', 'username'] or cmdtokens == ['set', 'fromuser']:
            return [t for t in self.possible_usernames if t.startswith(text)]
        elif cmdtokens == ['set', 'payload']:
            return [e for e in self.possible_payloads if e.startswith(text)]
        else:
            return []
########################################################################################################################################################################################
    def do_showallpayloads(self, line):
        """Shows All The Avalible Payloads"""
        subprocess.call(["msfcli", "multi/handler", "P"])
        
    def do_exit(self, line):
        """Exits Program"""
        sys.exit()

    def do_showoptions(self, line):
        """Shows Options For Module"""
        self.lhost = get_ip_address(self.iface)
        if self.module == "exploit/multi/handler":
            print colours.RED +"========================================" + colours.WHITE
            print colours.BLUE + "--payload =", self.payload + colours.WHITE
            print colours.BLUE + "--lhost =", self.lhost + colours.WHITE
            print colours.BLUE + "--lport =", self.lport + colours.WHITE
            print colours.BLUE + "--module =", self.module + colours.WHITE
            print colours.RED + "========================================" + colours.WHITE
        elif self.module == "auxiliary/scanner/smb/smb_login":
            print colours.RED + "========================================" + colours.WHITE
            print colours.BLUE + "--rhosts =", self.rhosts + colours.WHITE
            print colours.BLUE + "--rport =", self.rport + colours.WHITE
            print colours.BLUE + "--module =", self.module + colours.WHITE
            print colours.RED + "========================================" + colours.WHITE
        elif self.module == "auxiliary/scanner/rservices/rlogin_login":
            print colours.RED + "========================================" + colours.WHITE
            print colours.BLUE + "--rhosts =", self.rhosts + colours.WHITE
            print colours.BLUE + "--rport =", self.rport + colours.WHITE
            print colours.BLUE + "--module =", self.module + colours.WHITE
            print colours.BLUE + "--username =", self.username + colours.WHITE
            print colours.BLUE + "--fromuser =", self.fromuser + colours.WHITE
            print colours.RED + "========================================" + colours.WHITE
        elif self.module == "auxiliary/scanner/snmp/snmp_enum":
            print colours.RED + "========================================" + colours.WHITE
            print colours.BLUE + "--rhosts =", self.rhosts + colours.WHITE
            print colours.BLUE + "--rport =", self.rport + colours.WHITE
            print colours.BLUE + "--module =", self.module + colours.WHITE
            print colours.BLUE + "--community =", self.community + colours.WHITE
            print colours.BLUE + "--snmpversion =", self.snmpversion + colours.WHITE
            print colours.RED + "========================================" + colours.WHITE
        else:
            print "The module (%s) isn't supported yet!" % self.module
########################################################################################################################################################################MSFCLI Subprocess
    def do_run(self, line):
        """Runs The Module With Settings"""
        if self.module == "exploit/multi/handler":
            subprocess.call(["msfcli", self.module, "payload=%s" %self.payload, "lhost=%s" %self.lhost, "lport=%s" %self.lport, "E"])
            
        elif self.module == "auxiliary/scanner/smb/smb_login":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "E"])
            
        elif self.module == "auxiliary/scanner/rservices/rlogin_login":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "username=%s" %self.username, "fromuser=%s" %self.fromuser, "E"])
            
        elif self.module == "auxiliary/scanner/snmp/snmp_enum":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "community=%s" %self.community, "version=%s" %self.snmpversion, "E"])
        else:
            print "The module (%s) isn't supported yet!" % self.module
#########################################################################################################################################################################################
################################################################################################################################################################Used for import as modules
if __name__ == '__main__':
    print colours.RED + "========================================" + colours.WHITE
    print colours.BLUE + "-- Quick Metasploit" + colours.WHITE
    print colours.BLUE + "-- Type Help To List All Commands" + colours.WHITE
    print colours.BLUE + "-- Type Help (Command) For Specific Help" + colours.WHITE
    print colours.BLUE + "-- Local Ip Will Be Automaticaly Set" + colours.WHITE
    print colours.BLUE + "-- CTRL + C To Exit" + colours.WHITE
    print colours.RED + "========================================" + colours.WHITE
    print colours.GREEN + "Default Module Is %s" %DEFAULT_MODULE+ colours.WHITE
##########################################################################################################################################################################################
#############################################################################################################################################Catches Ctrl C and asks user for confirmation
    while(True):
        try:
            prompt = Handler()
            prompt.prompt = '(>>)'
            prompt.cmdloop('')
        except (KeyboardInterrupt, SystemExit):
            while(True):
                try:
                    time.sleep(0.05)
                    exit = raw_input (colours.GREEN + "\n\nAre You Sure You Want To Quit? y/[n] (>>)" + colours.WHITE)
                    if exit and exit.lower()[0] == "y":
                        print colours.RED + "Exiting..." + colours.WHITE
                        sys.exit()
                    else:
                        prompt.cmdloop('')
                
                except KeyboardInterrupt:
                    pass
##########################################################################################################################################################################################
