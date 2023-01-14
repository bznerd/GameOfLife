import numpy as np
from abc import ABC, abstractmethod

#Parent class for implementation of the Game Of Life Logic
class GameOfLifeParent(ABC):
    #Init attributes with passed parameters
    def __init__(self, startConfig=[]):
        self.liveCells = startConfig
        self.gen = 0
        self.enabled = True
        self.debug = False
    
     ########## Abstract methods to be implemented by subclass ##########

    #Perform a game iteration step
    @abstractmethod
    def iterate(self, iterations=1):
        pass

    #Toggle a selection of cells
    @abstractmethod
    def toggleCells(self,cells):
        pass

    #Toggle wrapper for binding to events
    @abstractmethod
    def toggleEvent(self, x, y):
        pass

    ########## Basic methods shared by all implemenations ##########

    #Get the current living cell population
    def getPop(self):
        return len(self.liveCells)

    #Get the current generation
    def getGen(self):
        return self.gen

    #Get the coordinates of all live cells
    def getLiveCells(self): 
        return self.liveCells

    #Disables iterations
    def toggleEnabled(self):
        self.enabled = not self.enabled


#Implements GameOfLifeParent with infinite gamespace
class GameOfLifeInfinite(GameOfLifeParent):
    def __init__(self, startConfig=[]):
        GameOfLifeParent.__init__(self, startConfig)
        
    #Run a game iteration
    def iterate(self, iterations=1):
        if not self.enabled: return
        self.gen += 1

        #List for changes
        changeList = []

        #Iterate over all living cells and run the update method on each
        for cell in self.liveCells:
            #Iterate over returned cell updates and add ones not already queued for updating
            for update in self.updateCell(cell):
                if update not in changeList: changeList.append(update)

        #Apply updates
        self.toggleCells(changeList)

    #Toggle a list of cells between live/dead
    def toggleCells(self, cells):
        for cell in cells:
            #Add a dead cell to the list of live cells
            if cell not in self.liveCells: self.liveCells.append(cell)
            #Remove a live cell from the list of live cells to make it dead
            else: self.liveCells.pop(self.liveCells.index([cell[0], cell[1]]))
        if self.debug: print(f"Toggled cells: {cells}")

    def toggleEvent(self, x, y):
        self.toggleCells([[x,y]])
        
    #Method to check a cell and its dead neighbors for their state in the next iteration
    def updateCell(self, checkCell):
        #Neighbor coordinates relative to current cell
        cellMap = [[-1,1], [0,1], [1,1], [-1,0], [1,0], [-1,-1], [0,-1], [1,-1]]

        #Cells that need to be toggled in next iteration
        changeList = []
        if not self.checkCell(checkCell, True):
            changeList.append(checkCell)
        
        #Create a list of dead neighbors to be checked for update
        unlitNeighbors = []
        for neighbor in cellMap:
            #If the neighbor is not in the liveCell list add it to unlitNeighbors
            if ([checkCell[0]+neighbor[0], checkCell[1]+neighbor[1]]) not in self.liveCells:
                unlitNeighbors.append([checkCell[0]+neighbor[0], checkCell[1]+neighbor[1]])

        #Add neighbors to change list if they should be toggled 
        for neighbor in unlitNeighbors:
            if self.checkCell(neighbor, False): changeList.append(neighbor)

        
        if self.debug: print(f"Updating Cell: {checkCell} Suggesting changes: {changeList}")

        #Return changes
        return changeList

    #Check a cell for if it should be dead or alive
    def checkCell(self, cell, living):
        #Neighbor coordinates relative to current cell
        cellMap = [[-1,1], [0,1], [1,1], [-1,0], [1,0], [-1,-1], [0,-1], [1,-1]]
       
        
        #Count number of living neighbors
        litCells = 0 
        for neighbor in cellMap:
            if [cell[0]+neighbor[0], cell[1]+neighbor[1]] in self.liveCells:
                litCells += 1

        if self.debug: print(f"Cell: {cell}\nLit cells: {self.liveCells}\nAdjacent lit cells: {litCells}")

        #Conditionals to return appropriate next state (see the four rules for the game and how they can be collapsed into three)
        if living and (litCells == 2 or litCells == 3): return True
        
        if not living and litCells == 3: return True

        else: return False

        


#Implementation scans a set sized grid to make game updates
class GameOfLifeGridScan(GameOfLifeParent):
    #Debug flag
    debug = False
    #Run parent init and specialized init
    def __init__(self,sizeX=100,sizeY=100,startConfig=[]):
        GameOfLifeParent.__init__(self, startConfig)
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.grid = np.zeros([sizeX, sizeY], dtype=int)
        if startConfig:
            for coord in startConfig:
                self.grid[coord[0], coord[1]] = True

    #Check a cell for number of surrounding lit cells
    def checkCell(self, x, y):
        litCells = 0
        #Surrounding cell map of coordinate deltas
        cellMap = [[-1,1],[0,1],[1,1],[-1,0],[1,0],[-1,-1],[0,-1],[1,-1]]
        #Iterate through map and check each cell adding the to litCells variable
        for cell in cellMap:
            if (x+cell[0] in range(0, self.sizeX) and y+cell[1] in range(0, self.sizeY)):
                if self.grid[x+cell[0], y+cell[1]]: litCells += 1
        return litCells

    #Run an iteration
    def iterate(self, iterations=1):
        #Do nothing if disabled
        if not self.enabled: return
        #Increment generation
        self.gen += 1
        changeList = []
        #Iterate through every cell on the grid
        for x in range(0,self.sizeX):
            for y in range(0, self.sizeY):
                #Check the number of surrounding lit cells
                check = self.checkCell(x, y)
                #Decide next state of the cell
                if self.grid[x,y] and check > 1 and check < 4:
                    pass
                elif not self.grid[x,y] and check == 3:
                    changeList.append([x, y, True])
                else:
                    changeList.append([x, y, False])
                if self.debug: print(f"Cell: {x}, {y} Lit cells: {check} Next State: {changeList[-1]}")
                
        #Update changed cells and change the population count
        for cell in changeList:
            self.grid[cell[0],cell[1]] = cell[2]
            if cell[2]:
                self.liveCells.append([cell[0],cell[1]])
            elif [cell[0],cell[1]] in self.liveCells:
                self.liveCells.pop(self.liveCells.index([cell[0], cell[1]]))

        #Recursively iterate for multiple iterations
        if iterations != 1:
            self.iterate(iterations=iterations-1)

    #Togle a selection of cells
    def toggleCells(self, cells):
        for cell in cells:
            if cell not in self.liveCells: self.liveCells.append(cell)
            else: self.liveCells.pop(self.liveCells.index([cell[0], cell[1]]))
            self.grid[cell[0],cell[1]] = not self.grid[cell[0],cell[1]]
        if self.debug: print(f"Toggled cells: {cells}")

    def toggleEvent(self, x, y):
        x, y = x+(self.sizeX//2), y+(self.sizeY//2)
        toggleCells([[x, y]])
