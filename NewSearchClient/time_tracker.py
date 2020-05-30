# -*- coding: utf-8 -*-
"""
Created on Sat May 30 09:26:49 2020

@author: magnu


HOW TO USE

import TimeTracker from time_tracker
into your file,
then to start a time use.
TimeTracker.startTimer("Planning") 
with a unique ID, (here it is "Planning")

and to stop the time use
TimeTracker.startTimer("Planning")

Finally to show your recorded times use either
TimeTracker.printTimes(), which takes all the recorded times and add the same ID's together or
TimeTracker.printIndividualTimes() which prints every recorded time under a tag
"""
import time
import sys

from collections import defaultdict


    
class TimeEntry:
    
        def __init__(self, tag):
            self.start_time = time.time()
            self.end_time = None
            self.tag = tag
        
        def stopTimer(self):
            self.end_time = time.time()
            self.time = self.end_time - self.start_time
            

class TimeTracker:
    runningTimers = []
    finishedTimers = defaultdict(list)
    
    @staticmethod
    def startTimer(tag):
        TimeTracker.runningTimers.append(TimeEntry(tag))
    
    @staticmethod
    def stopTimer(tag):
        for timer in TimeTracker.runningTimers:
            if(timer.tag == tag):
                timer.stopTimer()
                TimeTracker.runningTimers.remove(timer)
                TimeTracker.finishedTimers[tag].append(timer.time)
                
                break
    @staticmethod
    def printTimes():
        
        output =""
        for key, entries in TimeTracker.finishedTimers.items():
            output += key +": "
            output += str(sum(entries)) + "\n"
        
        print("========TOTAL TIMES========:\n"+str(output), file=sys.stderr, flush=True)

    @staticmethod
    def printIndividualTimes():
        print("========INDIVIDUAL TIMES========:\n"+str(TimeTracker.finishedTimers), file=sys.stderr, flush=True)
'''
Improvemt to do, make a heirachial graph that has keys as nodes, and time entries in each node. If a timer is started while another timer is running
It becomes a child of that timer, with this we can see what times are part of other times.

'''
class TimeGraphNode:
        
    def __init__(self, parent):
            self.parent = parent
            self.parent.addChild(self)
            self.children=[]
            
    def addChild(self, child):
        self.children.append(child)
    
class TimeGraph:
    parent = None
    children = []
    
    