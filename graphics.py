import tkinter as tk
from math import floor

#GUI class inherits tkinter root window
class GameOfLifeGUI(tk.Tk):
    #Initialize the main window in the center of the screen with min size and create various variables
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Conways Game of Life... but jank")
        self.rowconfigure(0, weight=1, minsize=100)
        self.columnconfigure(0,weight=1)
        self.minsize(width=500, height=350)
        positionRight = int(self.winfo_screenwidth()/2 - (800/2))
        positionDown = int(self.winfo_screenheight()/2 - (500/2))
        self.geometry(f"800x500+{positionRight}+{positionDown}")
        self.grid()
        self.gridSize = 10
        self.spacing = 20
        self.boundClickEvent = None
        self.speedEntry = tk.StringVar()
        self.popLabel = tk.StringVar()
        self.genLabel = tk.StringVar()
        self.initFrames()
    
    #Set the gridsize for debugging purposes
    def setSize(self, size):
        self.gridSize = size

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
        self.playPause = tk.Button(self.controlsFrame, text='Play pause')
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
        self.gameSpace = tk.Canvas(self.CanvasFrame, bg='#212121', bd=0, width=100, height=100)
        self.gameSpace.grid(row=0, column = 0, sticky=tk.N+tk.S+tk.W+tk.E, padx=2, pady=2)
        self.gameSpace.bind('<Button-1>', self.clickEvent)
     
    #Change the grid spacing
    def setSpacing(self, spacing):
        self.spacing = spacing

    #Draw the lines for the grid
    def drawLines(self):
        #Delete previous lines and get window dimensions
        self.gameSpace.delete('line')
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        #Draw red center dot
        self.gameSpace.addtag_withtag('line', self.gameSpace.create_oval(width-3,height-3,width+3,height+3, fill='#f72aba', outline='#f72aba'))
        #Draw verticle lines starting in the middle
        for x in range(0, int(width/self.spacing) + 1):
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(width+x*self.spacing,0,width+x*self.spacing,height*2, fill='#3b3b3b'))
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(width-x*self.spacing,0,width-x*self.spacing,height*2, fill='#3b3b3b'))
        #Draw horizontal lines starting in the middle
        for x in range(0, int(height/self.spacing) + 1):
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(0,height+x*self.spacing,width*2,height+x*self.spacing, fill='#3b3b3b'))
            self.gameSpace.addtag_withtag('line',self.gameSpace.create_line(0,height-x*self.spacing,width*2,height-x*self.spacing, fill='#3b3b3b'))

    #Draw the lit cells
    def drawSquares(self,squareCoords):
        #Delete previous cells and get window dimensions
        self.gameSpace.delete('square')
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        #Draw each passed square
        for square in squareCoords:
            self.gameSpace.addtag_withtag('square',self.gameSpace.create_rectangle((square[0]*self.spacing)+width+1,-1*(square[1]*self.spacing)+height-1,((square[0]+1)*self.spacing)+width-1,-1*((square[1]+1)*self.spacing)+height+1, fill='#ffff00', outline='#ffff00'))
    
    #Draw both lines and cells at the same time (Drawing lines is costly, only applicable for coarser grids)
    def drawAll(self, squareCoords):
        self.drawLines()
        self.drawSquares(squareCoords)

    #Bind a new eventhandler function to the click event
    def bindClickEvent(self, eventHandler):
        self.boundClickEvent = eventHandler

    #On click call click event handler and pass grid coordinates
    def clickEvent(self, event):
        x, y = event.x, event.y
        #modify coords to grid coords
        width = self.gameSpace.winfo_width()/2
        height = self.gameSpace.winfo_height()/2
        x -= width
        y -= height
        x = floor(x/self.spacing)
        y = floor(y/self.spacing)
        if(self.boundClickEvent is not None): self.boundClickEvent(x,y)
