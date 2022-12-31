import numpy as np

#Parent class for implementation of the Game Of Life Logic
class GameOfLifeParent:
    #Init attributes with passed parameters
    def __init__(self,sizeX=100,sizeY=100,startConfig=[]):
        self.liveCells = startConfig
        self.gen = 0
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.enabled = True
    
    #Basic iteration method (More of an example or debugging feature)
    def iterate(self, iterations=1):
        if not self.enabled: return
        self.gen += 1

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

    #Toggle a selection of cells
    def toggleCells(self,cells):
        for cell in cells:
            if cell not in self.liveCells: self.liveCells.append(cell)
            else: self.liveCells.pop(self.liveCells.index([cell[0], cell[1]]))

#Implementation scans a set sized grid to make game updates
class GameOfLifeGridScan(GameOfLifeParent):
    #Debug flag
    debug = False
    #Run parent init and specialized init
    def __init__(self,sizeX=100,sizeY=100,startConfig=[]):
        GameOfLifeParent.__init__(self,sizeX, sizeY, startConfig)
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
                if GameOfLifeGridScan.debug: print(f"Cell: {x}, {y} Lit cells: {check} Next State: {changeList[-1]}")
                
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
        if GameOfLifeGridScan.debug: print(f"Toggled cells: {cells}")