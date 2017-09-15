#!/usr/bin/env python
# -*- coding:utf-8 -*-   
from os import system  
import curses  
#import locale
import os
   
def get_param(prompt_string,simulation_string):  
     screen.clear()  
     screen.border(0)  
#     screen.addstr(3, 60, "Satellite link simulator")
     screen.addstr(10,50, prompt_string)
     screen.addstr(12,50,"Press enter to return to menu.")
     screen.addstr(3,50, "========================================")  
     screen.addstr(4,58, simulation_string)
     screen.addstr(5,50, "========================================")
     screen.refresh()  
     input = screen.getstr(10,75,60)  
     return input  
   
def execute_cmd(cmd_string):  
     system("clear")  
     a = system(cmd_string)  
     print ""  
     if a == 0:  
          print "Simulation executed correctly"  
     else:  
          print "Simulation terminated"  
     raw_input("Press enter to return to menu")  
     print ""  

def file(filename):
    if filename == "":
#       print 'The filename can not be empty,please enter the csv file name'
#       screen.addstr(10, 50, "The filename can not be empty,please enter the csv file name")
       return 0
    elif os.path.exists(filename) == False: 
#       print 'The file does not exit'
#       screen.addstr(10, 50, "The file does not exit")
       return 0
    else:
       return 1
 
x = 0  
#setlocale(LC_ALL,"zh_CN")
while x != ord('5'):  
     screen = curses.initscr()  
     screen.clear()  
     screen.border(0)  
     screen.addstr(3,50, "========================================")
     screen.addstr(4, 56, "Satellite Link Simulator V1.0")  
     screen.addstr(5, 50, "========================================")
     screen.addstr(10, 50, "1 - Continuity Simulation")  
     screen.addstr(12, 50, "2 - Delay Simulation")  
     screen.addstr(14, 50, "3 - Bit Error Rate Simulation") 
     screen.addstr(16, 50, "4 - Real Simulation") 
     screen.addstr(18, 50, "5 - EXIT")  
     screen.refresh()   
     x = screen.getch()  
     if x == ord('1'):  
        filename = get_param("Enter the csv file name:","Continuity Simulation")    
#	curses.endwin()
	if file(filename) == 1:
		curses.endwin()
       		execute_cmd("python access.py "+ filename)  
#	else:
#		screen.clear()
#		system("clear")
#		print ""
#		print 'The filename can not be empty,please enter the csv file name'
#		print ""	
     if x == ord('2'): 
	filename = get_param("Enter the csv file name:","Delay Simulation")
	if file(filename) == 1:
		curses.endwin()
        	execute_cmd("python delay.py "+ filename)  
     if x == ord('3'):  
	filename = get_param("Enter the csv file name:","Bit Error Rate Simulation")
	if file(filename) == 1:
		curses.endwin()
        	execute_cmd("python ber.py "+ filename)  
     if x== ord('4'):
#	filename = get_param("Enter the csv file name:","Joint Simulation")
#	if file(filename) ==1:
	curses.endwin()
	execute_cmd("python link_simulator.pyc") 
curses.endwin() 
