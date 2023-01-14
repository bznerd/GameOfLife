#!/usr/bin/env python3
import mechanics as mech
from graphics import GameOfLifeGUI
import time
import threading


#Global variables/configurations
debug = False 

#Create game and GUI objects with starting configurations
game = mech.GameOfLifeInfinite(startConfig = [[0,0], [-1,0], [0, -1], [-1, -1]])
game.debug = debug
GUI = GameOfLifeGUI()

#Main function only runs if this is the main script
def main():
    #Intialize timers 
    gameTimer = time.time()
    game.enabled = False
    frameCount = 0
    timer = time.time()

    #Initialize GUI with speed, population, generation, play pause bind, toggle bind, and live cell bind
    GUI.init(8, game.getPop(), game.getGen(), game.toggleEnabled, game.toggleEvent, game.getLiveCells)
    #Pull frequency from GUI
    if(GUI.speedEntry.get() != '' and GUI.speedEntry.get().isnumeric()): gameFrequency = 1/float(GUI.speedEntry.get())

    #Main loop
    while True:
        #Graphics event runs at unrestrained speeds
        GUI.frame()
        frameCount += 1
        #30 frame average displayed to the user
        if frameCount == 30:
            GUI.displayFrameRate(frameCount/(time.time()-timer))
            timer = time.time()
            frameCount = 0

        #Game update timing
        if gameTimer + gameFrequency < time.time():
            gameTimer = time.time()
            #Run an iteration
            game.iterate()
            #Update labels and frequency
            GUI.updateStats(game.getPop(), game.getGen())
            if(GUI.speedEntry.get() != '' and GUI.speedEntry.get().isnumeric()): gameFrequency = 1/float(GUI.speedEntry.get())

if __name__ == "__main__":
    main()
