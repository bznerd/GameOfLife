import tkinter as tk
from math import floor

#Instuctions text variable
INSTRUCTIONS = """The Game of Life was invented by British mathematician John Conway. It is an infinite grid of cells with four simple rules:
  1. Any live cell with fewer than two live neighbours dies, as if by underpopulation
  2. Any live cell with two or three live neighbours lives on to the next generation
  3. Any live cell with more than three live neighbours dies, as if by overpopulation
  4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction

This program implements the game with a simple interface.
  * The controls region is the panel at the bottom of the screen and presents the following stats: Framerate (FPS), Current
    population of cells, and Current game generation
    Along with these stats, there are two inputs: Play/Pause button to stop and start the game, and the Game Frequency input
    where a game frequency in generations per second (hertz) can be entered
  * The game region is the window above and visually displays the living cells on the grid as yellow squares.
    The window can be interacted with in three ways:
      1. Left Click: Toggle the clicked cell between alive and dead
      2. Drag Right Click: Move around the game window
      3. Mouse scroll: Zoom in and out of the grid

Have Fun!"""

#GUI class inherits tkinter root window
class GameOfLifeGUI(tk.Tk):
    #Initialize the main window in the center of the screen with min size and create various variables
    def __init__(self):
        tk.Tk.__init__(self)
        #Window configuration
        self.title("Conways Game of Life... but jank")
        self.rowconfigure(0, weight=1, minsize=100)
        self.columnconfigure(0,weight=1)
        self.minsize(width=500, height=350)
        positionRight = int(self.winfo_screenwidth()/2 - (800/2))
        positionDown = int(self.winfo_screenheight()/2 - (500/2))
        self.geometry(f"800x500+{positionRight}+{positionDown}")
        self.grid()

        #Grid sizing and movement variables
        self.gridSize = 20
        self.canvasCoords = [0,0]
        self.dragCoords = [0,0]
        self.lastLines = [0, 0, False, self.winfo_screenwidth(), self.winfo_screenheight()]

        #Callbacks and labels
        self.boundClickEvent = None
        self.boundSquareSupplier = None
        self.speedEntry = tk.StringVar()
        self.popLabel = tk.StringVar()
        self.genLabel = tk.StringVar()

        #Start frames in window
        self.initFrames()
    
    #Inititalize the main frames of the application
    def initFrames(self):
        #Gameregion contains the actual gamespace
        self.gameRegion = tk.Frame(self, bg='#525252', pady=12, padx=12)
        self.gameRegion.grid(row = 0, column = 0, sticky=tk.N+tk.S+tk.E+tk.W)
        #Init the internals of the game region
        self.initGameRegion()
        #Controlsregion is the wraper for the control bar (blue outline)
        self.controlsRegion = tk.Frame(self, bg='#0000ff', height=80)
        self.controlsRegion.grid(row = 1, column = 0, sticky=tk.E+tk.W)
        #Init the internals of the controls region
        self.initControlsRegion()

    #Init the internals of the controls region
    def initControlsRegion(self):
        #Configure controls region behavior
        self.controlsRegion.grid_propagate(0)
        self.controlsRegion.columnconfigure(0, weight=1)
        self.controlsRegion.rowconfigure(0, weight=1)
        #Controls frame the actual pane containing controls widgets
        self.controlsFrame = tk.Frame(self.controlsRegion, bg='#a1a1a1')
        self.controlsFrame.grid(row = 0, column = 0, sticky=tk.N+tk.S+tk.E+tk.W, padx=4, pady=4)
        self.controlsFrame.columnconfigure(0, weight=1)
        self.controlsFrame.columnconfigure(1, weight=7)
        self.controlsFrame.rowconfigure(0, weight=1)
        #All control widgets
        self.playPause = tk.Button(self.controlsFrame, text='Play/Pause')
        self.playPause.grid(row=0, column=1)
        self.fpsLabel = tk.Label(self.controlsFrame, text='FPS:')
        self.fpsLabel.grid(row=0, column=0)
        self.speedLabel = tk.Label(self.controlsFrame, text='Set the game frequency (Hz): ')
        self.speedLabel.grid(row=0, column=2, sticky=tk.E)
        self.speedControl = tk.Entry(self.controlsFrame, textvariable=self.speedEntry, width=4)
        self.speedControl.grid(row=0, column=3, sticky=tk.W)
        self.population = tk.Label(self.controlsFrame, textvariable=self.popLabel)
        self.population.grid(row=1, column = 0)
        self.generation = tk.Label(self.controlsFrame, textvariable=self.genLabel)
        self.generation.grid(row=1, column = 1)

    #Init the games region
    def initGameRegion(self):
        #Canvas frame is the drawable region of the games region
        self.CanvasFrame = tk.Frame(self.gameRegion, bg='#ffff00')
        self.CanvasFrame.grid(row = 0, column = 0, sticky=tk.N+tk.S+tk.E+tk.W)
        #Configure behavior of game region and canvas frame
        self.gameRegion.columnconfigure(0, weight=1)
        self.gameRegion.rowconfigure(0, weight=1)
        self.CanvasFrame.columnconfigure(0, weight=1)
        self.CanvasFrame.rowconfigure(0, weight=1)
        #Actual canvas object
        self.gameSpace = tk.Canvas(self.CanvasFrame, bg='#212121', bd=0)
        self.gameSpace.grid(row=0, column = 0, sticky=tk.N+tk.S+tk.W+tk.E, padx=2, pady=2)
        #Bind all controls
        self.gameSpace.bind('<Button-1>', self.clickEvent)
        self.gameSpace.bind('<B3-Motion>', self.moveDrag)
        self.gameSpace.bind('<Button-3>', self.beginDrag)
        self.gameSpace.bind('<Button-4>', self.scroll_in)
        self.gameSpace.bind('<Button-5>', self.scroll_out)

    #Setup and draw first game frame
    def init(self, speed, pop, gen, playPause, toggleCell, getCells):
        self.speedEntry.set(speed)
        self.updateStats(pop, gen)
        self.playPause.configure(command=playPause)
        self.bindClickEvent(toggleCell)
        self.bindSquareSupplier(getCells)
        self.update()
        self.drawLines()
        self.instructionsPopUp()

    #Display a new window with instructions
    def instructionsPopUp(self):
        #Window config
        window = tk.Toplevel()
        window.title("Instructions")
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        positionRight = int(window.winfo_screenwidth()/2 - (850/2))
        positionDown = int(window.winfo_screenheight()/2 - (375/2))
        window.geometry(f"850x375+{positionRight}+{positionDown}")
        window.resizable(False, False)

        #Instructions text
        instructions = tk.Label(window, text=INSTRUCTIONS, anchor=tk.W, justify=tk.LEFT)
        instructions.grid(row=0, column=0)
        #Close button
        close = tk.Button(window, text="Close", command=window.destroy)
        close.grid(row=1, column=0)

    #Draw the lines for the grid
    def drawLines(self):
        #Delete previous lines and get window dimensions
        self.gameSpace.delete('line')
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        #Draw red center dot
        x, y = self.canvasCoords
        xOffset, yOffset = x%self.gridSize, y%self.gridSize
        if (x > -width -10 and x < width + 10 and y > -height - 10 and y < height + 10): self.gameSpace.addtag_withtag('line', self.gameSpace.create_oval(width-3 + x,height-3 + y,width+3 + x,height+3 + y, fill='#f72aba', outline='#f72aba'))

        #Draw verticle lines starting in the middle
        for x in range(0, int(width/self.gridSize) + 2):
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(xOffset + width+x*self.gridSize,0,xOffset + width+x*self.gridSize,height*2, fill='#3b3b3b'))
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(xOffset + width-x*self.gridSize,0,xOffset + width-x*self.gridSize,height*2, fill='#3b3b3b'))

        #Draw horizontal lines starting in the middle
        for x in range(0, int(height/self.gridSize) + 2):
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(0,yOffset + height+x*self.gridSize,width*2,yOffset + height+x*self.gridSize, fill='#3b3b3b'))
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(0,yOffset + height-x*self.gridSize,width*2,yOffset + height-x*self.gridSize, fill='#3b3b3b'))

    #Draw the lit cells
    def drawSquares(self,squareCoords):
        #Delete previous cells and get window dimensions
        self.gameSpace.delete('square')
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        #Draw each passed square
        for square in squareCoords:
            self.gameSpace.addtag_withtag('square',self.gameSpace.create_rectangle((square[0]*self.gridSize)+width+1 + self.canvasCoords[0],-1*(square[1]*self.gridSize)+height-1 + self.canvasCoords[1],((square[0]+1)*self.gridSize)+width-1 + self.canvasCoords[0],-1*((square[1]+1)*self.gridSize)+height+1 + self.canvasCoords[1], fill='#ffff00', outline='#ffff00'))
    
    #Bind a new eventhandler function to the click event
    def bindClickEvent(self, eventHandler):
        self.boundClickEvent = eventHandler
    
    #Bind a supplier function for the squares to draw
    def bindSquareSupplier(self, supplier):
        self.boundSquareSupplier = supplier

    #Supply new game stats 
    def updateStats(self, pop, gen):
        self.popLabel.set(f'Current cell population: {pop}')
        self.genLabel.set(f'Current generation: {gen}')

    #Supply a new framerate
    def displayFrameRate(self, framerate):
        self.fpsLabel.configure(text=f'FPS: {framerate:.0f}')

    #On click call click event handler and pass grid coordinates
    def clickEvent(self, event):
        x, y = event.x - self.canvasCoords[0], event.y - self.canvasCoords[1]
        #modify coords to grid coords
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        x -= width
        y -= height
        x = floor(x/self.gridSize)
        y = floor(y/-self.gridSize)
        if(self.boundClickEvent is not None): self.boundClickEvent(x,y)

    #Begin drag event
    def beginDrag(self, event):
        self.dragCoords = [event.x, event.y]

    #Drag movement handler
    def moveDrag(self, event):
        x, y = event.x, event.y
        #Find change since last call
        xDelta = event.x - self.dragCoords[0]
        yDelta = event.y - self.dragCoords[1]
        #Apply movement to grid
        self.canvasCoords[0] += xDelta
        self.canvasCoords[1] += yDelta
        #Store new position for next call
        self.dragCoords = [event.x, event.y]

    #Scroll in event handler for zoom in
    def scroll_in(self, event):
        #Flag line redraw for next frame, increase grid size if its less than max zoom
        self.lastLines[2] = True
        if self.gridSize == 50: return
        self.gridSize += 1

    #Scroll out event handler for zoom out
    def scroll_out(self, event):
        #Flag line redraw for next frame, decrease grid size if its more than the min zoom
        self.lastLines[2] = True
        if self.gridSize == 6: return
        self.gridSize -= 1

    #Draw a frame
    def frame(self):
        #Only draw lines under the following conditions:
        # * Change in canvas location
        # * Change in zoom (lastLines[2])
        # * Change in window size
        if (self.canvasCoords[0] != self.lastLines[0] or self.canvasCoords[1] != self.lastLines[1] or self.lastLines[2]
            or self.lastLines[3] != self.winfo_screenwidth() or self.lastLines[3] != self.winfo_screenheight()):

            #Reset flags
            self.lastLines = [self.canvasCoords[0], self.canvasCoords[1], False, self.winfo_screenwidth(), self.winfo_screenheight()]
            #Draw new lines
            self.drawLines()


        #Draw the squares if a supplier is bound
        if (self.boundSquareSupplier == None):
            self.drawSquares([])
        else: self.drawSquares(self.boundSquareSupplier())
        #Push changes to screen
        self.update()
