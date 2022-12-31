import mechanics as mech
from graphics import GameOfLifeGUI
import time
import threading


#Global variables/configurations
debug = False
mech.GameOfLifeGridScan.debug = False

#Create game and GUI objects with starting configurations
game = mech.GameOfLifeGridScan(sizeX = 60, sizeY = 20, startConfig=[[17,2],[18,2],[19,2],[18,0],[19,1],[30,16],[31,16],[29,16]])
GUI = GameOfLifeGUI()

#Create and event handler for clicks to toggle cells
def toggleCellClickEvent(x,y):
    game.toggleCells([[x+30,-1*y+9]])


#Main function only runs if this is the main script
def main():
    #Intialize start stop behavior, timers, labels, start speed, and bind click eventhandler
    gameTimer = time.time()
    GUI.speedEntry.set(8)
    if(GUI.speedEntry.get() != '' and GUI.speedEntry.get().isnumeric()): gameFrequency = 1/float(GUI.speedEntry.get())
    GUI.popLabel.set(f'Current cell population: {game.getPop()}')
    GUI.genLabel.set(f'Current generation: {game.getGen()}')
    game.enabled = False
    GUI.playPause.configure(command=game.toggleEnabled)
    GUI.bindClickEvent(toggleCellClickEvent)
    frameCount = 0
    timer = time.time()

    #Main loop
    while True:
        #Graphics event runs at unrestrained speeds
        GUI.drawAll([[square[0]-30,square[1]-10] for square in game.getLiveCells()])
        GUI.update()
        frameCount += 1
        #20 frame average displayed to the user
        if frameCount == 20:
            GUI.fpsLabel.configure(text=f'FPS: {frameCount/(time.time()-timer):.0f}')
            timer = time.time()
            frameCount = 0

        #Game update timing
        if gameTimer + gameFrequency < time.time():
            gameTimer = time.time()
            #Run an iteration
            game.iterate()
            #Update labels and speed
            GUI.popLabel.set(f'Current cell population: {game.getPop()}')
            GUI.genLabel.set(f'Current generation: {game.getGen()}')
            if(GUI.speedEntry.get() != '' and GUI.speedEntry.get().isnumeric()): gameFrequency = 1/float(GUI.speedEntry.get())

if __name__ == "__main__":
    main()