# import the pygame module, so you can use it
import pygame
import math
import random
 
WIDTH = 1200
HEIGHT = 650
YBORDER = 1/50
XBORDER = 1/80
YRATIO = 1/9
XRATIO = 1/6
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEEPSKYBLUE = (0,191,255)
BLUE = (0,0,255)
NAVY = (0,0,128)
GRAY = (150, 150, 150)
LIGHTGRAY = (211,211,211)
LIGHTRED = (255, 204, 203)
YELLOW = (255, 255, 0)

#####################################
######## algorithms and data structures to present Petri Net and Transition System

#### interface class UI object
class UIObj:
    def __init__(self, rect) -> None:
        self.rect = rect    # a pygame rectangle is a object with 4 attributes: left, top, width, height
        self.isClicked = 0  # True when UI object is clicked

    def findMatchFont(self, max_size, name): # find a match font for rendering "name" inside the UI object
        font = pygame.font.SysFont("sans", max_size)
        ## if the text bigger than the object, reduce max_size
        while font.size(name)[0] > self.rect.width or font.size(name)[1] > self.rect.height:
            max_size -=1
            font = pygame.font.SysFont("sans", max_size)
        return font

#### Arc present the arc in both Petri Net and TS
class Arc:
    def __init__(self, info) -> None:
        self.info = info #### info present the information of the Arc, can be a label() or a weight)

    def draw(self, screen, v1, v2) -> None: #### draw Arc on screen
        source = ()
        des = ()
        if (v2.centerx - v1.centerx) != 0:
            k = abs((v2.centery - v1.centery)/(v2.centerx - v1.centerx))
        
            if k <=1:
                if v1.centerx < v2.centerx:
                    source = v1.midright
                    des = v2.midleft
                else:
                    source = v1.midleft
                    des = v2.midright
            else:
                if v1.centery < v2.centery:
                    source = v1.midbottom
                    des = v2.midtop
                else:
                    source = v1.midtop
                    des = v2.midbottom
        else:
            if v1.centery < v2.centery:
                source = v1.midbottom
                des = v2.midtop
            else:
                source = v1.midtop
                des = v2.midbottom

        len = math.sqrt(math.pow(source[0]-des[0], 2) + math.pow(source[1]-des[1], 2))
        if len != 0:
            rad = math.acos((source[0]-des[0])/len)
            if source[1] < des[1]: rad = -rad
            a1 = (des[0]+15*math.cos(rad+(math.pi)/6), des[1]+15*math.sin(rad+(math.pi)/6))
            a2 = (des[0]+15*math.cos(rad-(math.pi)/6), des[1]+15*math.sin(rad-(math.pi)/6))
            pygame.draw.line(screen, BLACK, source, des, 2)
            pygame.draw.line(screen, BLACK, des, a1, 2)
            pygame.draw.line(screen, BLACK, des, a2, 2)

        inter = (source[0]/2+des[0]/2, source[1]/2+des[1]/2)
        font = pygame.font.SysFont("sans", 15)
        text = font.render(self.info, True, BLACK)
        screen.blit(text, inter)

    def copy(self):
        newArc = Arc(self.info)
        return newArc

#### State present the state in Transition System
class State(UIObj):
    def __init__(self, rect, name, isInit = 0) -> None:
        super().__init__(rect)
        self.name = name    # name of the state
        self.isInit = isInit    # True when "self" is the initial state
        self.font = self.findMatchFont(15, name)    # match font of the text
        self.text = self.font.render(self.name, True, BLACK)    

    def updateFont(self):   # update the font and the text when self->rect changes
        self.font = self.findMatchFont(15, self.name)   
        self.text = self.font.render(self.name, True, BLACK)

    def draw(self, screen) -> None: # draw state on screen
        global WHITE
        global BLACK
        if self.isInit: 
            pygame.draw.rect(screen, WHITE, self.rect)
            pygame.draw.circle(screen, BLACK, self.rect.center, self.rect.width/2, 2)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
        else:
            pygame.draw.circle(screen, WHITE, self.rect.center, self.rect.width/2)
            pygame.draw.circle(screen, BLACK, self.rect.center, self.rect.width/2, 2)
        textsize = self.font.size(self.name)
        screen.blit(self.text, (self.rect.x + (self.rect.width-textsize[0])/2, self.rect.y + (self.rect.height-textsize[1])/2))

    def copy(self): # return the copy of the self object
        return State(self.rect.copy(), self.name)

#### Transition System object
class TransitionSystem:
    def __init__(self) -> None:
        self.initState = "" # name of the initial state of the TS
        self.states = {}    # a dict map from a name to the State which have that name, i.e: {'a' : State('a')}
        self.adjList = {}   # a dict which each element is another dict, the adjacent list to store Arc, i.e: {'a' : {'b' : Arc('1')}} mean that an arc points from 'a' to 'b' 

    def draw(self, screen): # draw Transition System on screen
        for x in self.adjList:
            for y in self.adjList[x]:
                self.adjList[x][y].draw(screen, self.states[x].rect, self.states[y].rect)
        for x in self.states:
            self.states[x].draw(screen)

    def autoScale(self, whiteboard):    # arrange TS to fit the whiteboard rect when initializing
        nodewidth = 0
        if (len(self.states) - 2) > 15:
            nodewidth = whiteboard.width/(len(self.states) - 2)
        else: 
            nodewidth = whiteboard.width/15
        self.states[self.initState].rect.left = whiteboard.left + nodewidth/2
        self.states[self.initState].rect.top = whiteboard.top + nodewidth/2
        for x in self.states:
            self.states[x].rect.width = nodewidth
            self.states[x].rect.height = nodewidth
            self.states[x].updateFont()
            if x==self.initState: continue
            else:
                self.states[x].rect.centerx = whiteboard.left + nodewidth + random.random()*(whiteboard.width - 2*nodewidth)
                self.states[x].rect.centery = whiteboard.top + nodewidth + random.random()*(whiteboard.height - 2*nodewidth)
    
    def scaling(self, kx, ky):  # scaling TS when the size of the window is changed
        kw = 0
        if kx < ky: kw = kx
        else: kw = ky
        for x in self.states.values():
            x.rect.left *= kx
            x.rect.top *= ky
            x.rect.width *= kw
            x.rect.height *= kw
            x.updateFont()

#### present the place in Petri Net
class Place(UIObj):
    def __init__(self, rect, name, tokens = 0) -> None:
        super().__init__(rect)
        self.name = name    # name of the place
        self.tokens = tokens    # the number of tokens are hold by place

    def draw(self, screen) -> None: # draw place on screen
        global WHITE
        global BLACK
        pygame.draw.circle(screen, WHITE, self.rect.center, self.rect.width/2)
        pygame.draw.circle(screen, BLACK, self.rect.center, self.rect.width/2, 2)
        font1 = self.findMatchFont(20, str(self.tokens))
        text1 = font1.render(str(self.tokens), True, BLACK)
        text1size = font1.size(str(self.tokens))
        screen.blit(text1, (self.rect.x + (self.rect.width-text1size[0])/2, self.rect.y + (self.rect.height-text1size[1])/2))
        font2 = self.findMatchFont(15, self.name)
        text2 = font2.render(self.name, True, BLACK)
        text2size = font2.size(self.name)
        screen.blit(text2, (self.rect.x + (self.rect.width-text2size[0])/2, self.rect.bottom))

    def copy(self): # return the copy of place
        return Place(self.rect.copy(), self.name, self.tokens)

#### present the transition in Petri Net
class Transition(UIObj):
    def __init__(self, rect, name) -> None:
        super().__init__(rect)
        self.name = name    # name of the transition
        self.isMoving = 0   # True if the transition is moving by mouse click

    def draw(self, screen, isEnable):   # draw transition on screen
        global WHITE
        global BLACK
        if isEnable:
            pygame.draw.rect(screen, YELLOW, self.rect)
        else: pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        font = self.findMatchFont(15, self.name)
        text = font.render(self.name, True, BLACK)
        textsize = font.size(self.name)
        screen.blit(text, (self.rect.x + (self.rect.width-textsize[0])/2, self.rect.y + (self.rect.height-textsize[1])/2))

    def copy(self): # return the copy of the transition
        return Transition(self.rect.copy(), self.name)

#### Petri Net object
class PetriNet:
    def __init__(self) -> None:
        self.places = {}    # a dict map from a name to a place which have that name, i.e: {'a' : Place('a')}
        self.transitions = {}   # a dict map from a name to a transition which have that name, i.e {'b' : Transition('b')}
        self.adjList = {}   # a dict which each element is another dict, the adjacent list to store Arc, i.e: {'a' : {'b' : Arc('1')}} mean that an arc points from a to b

    def preset(self, name): # return a dict which is the preset of the 'name'
        preset = {}
        if name not in self.adjList:
            return preset
        else:
            for x in self.adjList:
                if name in self.adjList[x]:
                    preset[x] = self.adjList[x][name]
            return preset

    def isEnable(self, name) -> bool:   # check if a transition having the 'name' is enable, return True if enable
        if name not in self.transitions:
            return False
        else: 
            preset = self.preset(name)
            for x in preset:
                if self.places[x].tokens < int(preset[x].info):
                    return False
            return True

    def firing(self, name): # firing a transition have the 'name', return True if success
        if self.isEnable(name):
            preset = self.preset(name)
            for x in preset:
                self.places[x].tokens -= int(preset[x].info)
            for x in self.adjList[name]:
                self.places[x].tokens += int(self.adjList[name][x].info)
            return True
        else: return False

    def setMarking(self, dict): # set place's tokens with a dict maps from name to the number of tokens, i.e: {'a' : 1, 'b' : 2}
        for x in dict:
            self.places[x].tokens = dict[x]

    def markingString(self, names) -> str: # return a string of the marking with 'names' is the list of names of places we need to know, i.e: return '(1,0,0)' with 'names' is ['free', 'busy', 'docu']
        marking = "("
        if (len(names) > 0):
            marking += str(self.places[names[0]].tokens)
        for i in range(1, len(names)):
            marking +=  "," + str(self.places[names[i]].tokens)
        marking += ")"
        return marking

    def markingDict(self): # return a dict of marking which maps from a name to the number of tokens, i.e: {'free' : 1, 'busy' : 2}
        dict = {}
        for x in self.places:
            dict[x] = self.places[x].tokens
        return dict
    
    def copy(self):  # return a copy of the Petri Net
        newPetriNet = PetriNet()
        for x in self.places:
            newPetriNet.places[x] = self.places[x].copy()
        for x in self.transitions:
            newPetriNet.transitions[x] = self.transitions[x].copy()
        for x in self.adjList:
            newPetriNet.adjList[x] = {}
            for y in self.adjList[x]:
                newPetriNet.adjList[x][y] = self.adjList[x][y].copy()
        return newPetriNet

    def reachabilityGraph(self, names): # return a Transition System which is the reachability graph of the Petri Net
        ts = TransitionSystem()
        tempPN = self.copy()
        queue = [tempPN.markingDict()]
        ts.states[tempPN.markingString(names)] = State(pygame.Rect(0, 0, 100, 100), tempPN.markingString(names), 1)
        ts.initState = tempPN.markingString(names)
        ts.adjList[tempPN.markingString(names)] = {}
        while len(queue)>0:
            popmark = queue.pop(0)
            for x in tempPN.transitions:
                tempPN.setMarking(popmark)
                v1 = tempPN.markingString(names)
                if tempPN.isEnable(x):
                    tempPN.firing(x)
                    v2 = tempPN.markingString(names)
                    if v2 not in ts.states:
                        ts.states[v2] = State(pygame.Rect(0, 0, 100, 100), v2)
                        ts.adjList[v2] = {}
                        queue.append(tempPN.markingDict())
                    ts.adjList[v1][v2] = Arc(x)
        return ts            

    def draw(self, screen): # draw Petri Net on screen
        for x in self.adjList:
            for y in self.adjList[x]:
                if x in self.places:
                    self.adjList[x][y].draw(screen, self.places[x].rect, self.transitions[y].rect)
                else:
                    self.adjList[x][y].draw(screen, self.transitions[x].rect, self.places[y].rect)
        for x in self.places:
            self.places[x].draw(screen)
        for x in self.transitions:
            self.transitions[x].draw(screen, self.isEnable(self.transitions[x].name))

    def scaling(self, kx, ky):  # scaling Petri Net when window's size is changed
        kw = 0
        if kx < ky: kw = kx
        else: kw = ky
        for x in self.places.values():
            x.rect.left *= kx
            x.rect.top *= ky
            x.rect.width *= kw
            x.rect.height *= kw
        for x in self.transitions.values():
            x.rect.left *= kx
            x.rect.top *= ky
            x.rect.width *= kw
            x.rect.height *= kw
### end of Petri Net implement
###########################


#### GUI implement
### ...
class Button(UIObj):
    def __init__(self, rect, name, transparent = 0, color = WHITE, renderCol = BLACK) -> None:
        super().__init__(rect)
        self.name = name
        self.transparent = transparent
        self.color = color
        self.renderCol = renderCol
        self.active = 0

    def draw(self, screen) -> None:
        color = (0, 0, 0)
        if self.active: color = LIGHTGRAY
        else: color = self.color
        if self.transparent == 0:
            pygame.draw.rect(screen, color, self.rect)
        font = self.findMatchFont(20, self.name)
        text = font.render(self.name, True, self.renderCol)
        textsize = font.size(self.name)
        screen.blit(text, (self.rect.x + (self.rect.width-textsize[0])/2, self.rect.y + (self.rect.height-textsize[1])/2))

def refeshScreen(kx, ky):
    global workspace
    global taskbar
    global whiteboard

    global wsButtonNames
    global wsButtonWidth
    global wsButtonHeight
    global wsButtons 

    global buttonInTaskbarWidth
    global buttonInTaskbarHeight
    global createButton
    global petriButton
    global tsButton

    global tokenEntryHeight

    global upButtons
    global downButtons
    global textRect
    global tokenRect
    
    global text0
    global text1
    global text2
    global text3
    global text4
    global text5
    global text6
    global text7
    global text8

    global fontnote
    global note0
    global note1

    global token0

    global token1

    global token2

    global token3

    global nodewidth
    ##### init graph 0
    global slotfree0
    global slotbusy0
    global slotdocu0

    global start0
    global change0
    global end0

    global free0
    global busy0
    global docu0

    global petri0

    global graph0
    global activeGraph0
    ###
    ###### init graph 1
    global free1
    global docu1
    global start1
    global change1
    global end1
    global busy1
    global graph1
    global activeGraph1
    ####
    #### init graph 2
    global wait2
    global done2
    global inside2
    global start2
    global change2
    global graph2

    ###
    ##### init graph 3
    global wait3
    global done3
    global busy3
    global inside3
    global start3
    global change3
    global free3
    global end3
    global docu3
    global graph3
    global activeGraph3

    global mode
    global guides

    screen.fill(BLUE)

    workspace = pygame.Rect(WIDTH*XRATIO, 0, WIDTH*(1-XRATIO), HEIGHT)
    taskbar = pygame.Rect(workspace.left, workspace.top, workspace.width, workspace.height*YRATIO)
    pygame.draw.rect(screen, NAVY, taskbar)
    oldBoard = whiteboard
    whiteboard = pygame.Rect(workspace.left, taskbar.bottom, workspace.width, workspace.height - taskbar.height)
    pygame.draw.rect(screen, WHITE, whiteboard)

    wsButtonWidth = (WIDTH - workspace.width)*(1 - 2*XBORDER)
    wsButtonHeight = (HEIGHT - taskbar.height)*(1 - (len(wsButtonNames) + 1)*YBORDER)/len(wsButtonNames)
    for x in range(len(wsButtonNames)):
        wsButtons[x].rect = pygame.Rect((WIDTH - workspace.width)*XBORDER, x*((HEIGHT - taskbar.height)*YBORDER + wsButtonHeight) + (HEIGHT - taskbar.height)*YBORDER + taskbar.height, wsButtonWidth, wsButtonHeight)
        wsButtons[x].draw(screen)

    buttonInTaskbarWidth = taskbar.w/6*(1 - 2*XBORDER)
    buttonInTaskbarHeight = taskbar.h*(1 - 2*YBORDER)
    createButton.rect = pygame.Rect(taskbar.left + taskbar.w/2 + taskbar.w*XBORDER/6, taskbar.h*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight)
    petriButton.rect = pygame.Rect(taskbar.left + taskbar.width*2/3 + taskbar.width*XBORDER/6, taskbar.height*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight)
    tsButton.rect = pygame.Rect(taskbar.left + taskbar.width*5/6 + taskbar.width*XBORDER/6, taskbar.height*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight)

    tokenEntryHeight = (buttonInTaskbarHeight - taskbar.height*YBORDER)/2

    for x in range(2):
        for y in range(3):
            textRect[3*x + y] = pygame.Rect(taskbar.left + taskbar.width/6*(y + XBORDER), taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, buttonInTaskbarWidth - tokenEntryHeight*3/2, tokenEntryHeight)
            tokenRect[3*x + y] = pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight*3/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, tokenEntryHeight, tokenEntryHeight)

            upButtons[3*x + y].rect = pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, tokenEntryHeight/2, tokenEntryHeight/2)
            downButtons[3*x + y].rect = pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x + tokenEntryHeight/2, tokenEntryHeight/2, tokenEntryHeight/2)

    text0.rect = textRect[0]
    text1.rect = textRect[1]
    text2.rect = textRect[2]
    text3.rect = textRect[3]
    text4.rect = textRect[4]
    text5.rect = textRect[5]
    text6.rect = textRect[3]
    text7.rect = textRect[4]
    text8.rect = textRect[5]

    for x in guides:
        x.rect.left *= kx
        x.rect.top *= ky
        x.rect.width *= kx
        x.rect.height *= ky

    fontnote = pygame.font.SysFont("sans", int(whiteboard.width/57))
    note0 = fontnote.render("(free, busy, docu)", True, BLACK)
    note1 = fontnote.render("(free, busy, docu, wait, inside, done)", True, BLACK)

    for x in range(6):
        token0[x].rect = tokenRect[x]

    for x in range(3):
        token1[x].rect = tokenRect[x]

    for x in range(3):
        token2[x].rect = tokenRect[x + 3]

    for x in range(6):
        token3[x].rect = tokenRect[x]

    graph0[0].scaling(kx, ky)
    graph0[1].scaling(kx, ky)
    graph1[0].scaling(kx, ky)
    graph1[1].scaling(kx, ky)
    graph2.scaling(kx, ky)
    graph3[0].scaling(kx, ky)
    graph3[1].scaling(kx, ky)

    if mode==0:
        for x in guides:
            x.draw(screen)
    elif mode==1:
        if activeGraph0==1: 
            screen.blit(note0, whiteboard) 
        petriButton.draw(screen)
        tsButton.draw(screen)
        text0.draw(screen)
        text1.draw(screen)
        text2.draw(screen)
        text3.draw(screen)
        text4.draw(screen)
        text5.draw(screen)
        for x in range(len(token0)):
            token0[x].draw(screen)
            upButtons[x].draw(screen)
            downButtons[x].draw(screen)  
        graph0[activeGraph0].draw(screen)
    elif mode==2:
        if activeGraph1==1: 
            screen.blit(note0, whiteboard) 
        petriButton.draw(screen)
        tsButton.draw(screen)
        text0.draw(screen)
        text1.draw(screen)
        text2.draw(screen)
        for x in range(len(token1)):
            token1[x].draw(screen)
            upButtons[x].draw(screen)
            downButtons[x].draw(screen)
        graph1[activeGraph1].draw(screen)
    elif mode==3:
        text6.draw(screen)
        text7.draw(screen)
        text8.draw(screen)
        for x in range(len(token2)):
            token2[x].draw(screen)
            upButtons[x + 3].draw(screen)
            downButtons[x + 3].draw(screen)
        graph2.draw(screen)
    elif mode==4:
        if activeGraph3==1: 
            screen.blit(note1, whiteboard) 
        petriButton.draw(screen)
        tsButton.draw(screen)
        text0.draw(screen)
        text1.draw(screen)
        text2.draw(screen)
        text6.draw(screen)
        text7.draw(screen)
        text8.draw(screen)
        for x in range(len(token3)):
            token3[x].draw(screen)
            upButtons[x].draw(screen)
            downButtons[x].draw(screen) 
        graph3[activeGraph3].draw(screen)
    if mode!=0: createButton.draw(screen) 

    pygame.display.flip()

# define a variable to control the main loop
pygame.init()
# load and set the logo
#logo = pygame.image.load("logo32x32.png")
#pygame.display.set_icon(logo)
pygame.display.set_caption("Petri Net")
    
# create a surface on screen that has the size of 240 x 180

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

screen.fill(BLUE)

workspace = pygame.Rect(WIDTH*XRATIO, 0, WIDTH*(1-XRATIO), HEIGHT)
taskbar = pygame.Rect(workspace.left, workspace.top, workspace.width, workspace.height*YRATIO)
pygame.draw.rect(screen, NAVY, taskbar)
whiteboard = pygame.Rect(workspace.left, taskbar.bottom, workspace.width, workspace.height - taskbar.height)
pygame.draw.rect(screen, WHITE, whiteboard)

wsButtonNames = ("GUIDE", "Question 1b/i", "Question 1b/ii", "Question 2", "Question 3 & 4")
wsButtonWidth = (WIDTH - workspace.width)*(1 - 2*XBORDER)
wsButtonHeight = (HEIGHT - taskbar.height)*(1 - (len(wsButtonNames) + 1)*YBORDER)/len(wsButtonNames)
wsButtons = []
for x in range(len(wsButtonNames)):
    wsButtons.append(Button(pygame.Rect((WIDTH - workspace.width)*XBORDER, x*((HEIGHT - taskbar.height)*YBORDER + wsButtonHeight) + (HEIGHT - taskbar.height)*YBORDER + taskbar.height, wsButtonWidth, wsButtonHeight), wsButtonNames[x]))
    if x==0: wsButtons[x].active = 1
    wsButtons[x].draw(screen)

buttonInTaskbarWidth = taskbar.w/6*(1 - 2*XBORDER)
buttonInTaskbarHeight = taskbar.h*(1 - 2*YBORDER)
createButton = Button(pygame.Rect(taskbar.left + taskbar.w/2 + taskbar.w*XBORDER/6, taskbar.h*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight), "SET")
petriButton = Button(pygame.Rect(taskbar.left + taskbar.width*2/3 + taskbar.width*XBORDER/6, taskbar.height*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight), "PETRI NET")
tsButton = Button(pygame.Rect(taskbar.left + taskbar.width*5/6 + taskbar.width*XBORDER/6, taskbar.height*YBORDER, buttonInTaskbarWidth, buttonInTaskbarHeight), "T.SYSTEM")

tokenEntryHeight = (buttonInTaskbarHeight - taskbar.height*YBORDER)/2

upButtons = []
downButtons = []
textRect = []
tokenRect = []
for x in range(2):
    for y in range(3):
        textRect.append(pygame.Rect(taskbar.left + taskbar.width/6*(y + XBORDER), taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, buttonInTaskbarWidth - tokenEntryHeight*3/2, tokenEntryHeight))
        tokenRect.append(pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight*3/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, tokenEntryHeight, tokenEntryHeight))

        upButtons.append(Button(pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x, tokenEntryHeight/2, tokenEntryHeight/2), "+", color = GRAY))
        downButtons.append(Button(pygame.Rect(taskbar.left + taskbar.width*(y + 1)/6*(1 - XBORDER) - tokenEntryHeight/2, taskbar.height*YBORDER + (tokenEntryHeight + taskbar.height*YBORDER)*x + tokenEntryHeight/2, tokenEntryHeight/2, tokenEntryHeight/2), "-", color = GRAY))

text0 = Button(textRect[0], "free", 1, renderCol= WHITE)
text1 = Button(textRect[1], "busy", 1, renderCol= WHITE)
text2 = Button(textRect[2], "docu", 1, renderCol= WHITE)
text3 = Button(textRect[3], "max free", 1, renderCol= WHITE)
text4 = Button(textRect[4], "max busy", 1, renderCol= WHITE)
text5 = Button(textRect[5], "max docu", 1, renderCol= WHITE)
text6 = Button(textRect[3], "wait", 1, renderCol= WHITE)
text7 = Button(textRect[4], "inside", 1, renderCol= WHITE)
text8 = Button(textRect[5], "done", 1, renderCol= WHITE)
guide0 = Button(pygame.Rect(whiteboard.left, whiteboard.top, whiteboard.width, whiteboard.height/5), "- Choose the question to implement. Click SET to set your optional input.", 1)
guide1 = Button(pygame.Rect(whiteboard.left, guide0.rect.bottom, whiteboard.width, guide0.rect.height), "- Click and hold to move any node, click only to fire enable transitions.", 1)
guide2 = Button(pygame.Rect(whiteboard.left, guide1.rect.bottom, whiteboard.width, guide1.rect.height), "- Click PETRI NET or T.SYSTEM to switch between the Petri Net and Transition System.", 1)
guide3 = Button(pygame.Rect(whiteboard.left, guide2.rect.bottom, whiteboard.width, guide2.rect.height), "- NOTE: Although the algorithm can take any input, the Transiton System can be huge with just small number.", 0, YELLOW)
guide4 = Button(pygame.Rect(whiteboard.left, guide3.rect.bottom, whiteboard.width, guide3.rect.height), "- We recommend using small inputs when observing Transition System and any input to obverse Petri Net.", 0, YELLOW)
guides = [guide0, guide1, guide2, guide3, guide4]
for x in guides:
    x.draw(screen)
fontnote = pygame.font.SysFont("sans", 20)
note0 = fontnote.render("(free, busy, docu)", True, BLACK)
note1 = fontnote.render("(free, busy, docu, wait, inside, done)", True, BLACK)

token0 = []
for x in range(6):
    token0.append(Button(tokenRect[x], "1"))
token0[2].name = "0"

token1 = []
for x in range(3):
    token1.append(Button(tokenRect[x], "0"))
token1[0].name = "4"

token2 = []
for x in range(3):
    token2.append(Button(tokenRect[x + 3], "0"))
token2[0].name = "5"
token2[2].name = "1"
##pygame.display.flip()

token3 = []
for x in range(6):
    token3.append(Button(tokenRect[x].copy(), "0"))
token3[0].name = "1"
token3[3].name = "3"
token3[5].name = "1"

nodewidth = whiteboard.width/15
##### init graph 0
slotfree0 = Place(pygame.Rect(whiteboard.left + nodewidth, whiteboard.top + nodewidth, nodewidth, nodewidth), "slot free")
slotbusy0 = Place(pygame.Rect(whiteboard.left, whiteboard.bottom - 2*nodewidth, nodewidth, nodewidth), "slot busy", 1)
slotdocu0 = Place(pygame.Rect(whiteboard.left + nodewidth + whiteboard.height, whiteboard.top + nodewidth, nodewidth, nodewidth), "slot docu", 1)
slotbusy0.rect.left = (slotfree0.rect.left + slotdocu0.rect.left)/2

start0 = Transition(pygame.Rect(whiteboard.left, whiteboard.top, nodewidth, nodewidth), "start")
start0.rect.left = (slotfree0.rect.left + slotbusy0.rect.left)/2
start0.rect.top = (slotfree0.rect.top + slotbusy0.rect.top)/2
change0 = Transition(pygame.Rect(whiteboard.left, whiteboard.top, nodewidth, nodewidth), "change")
change0.rect.left = (slotbusy0.rect.left + slotdocu0.rect.left)/2
change0.rect.top = (slotbusy0.rect.top + slotdocu0.rect.top)/2
end0 = Transition(pygame.Rect(whiteboard.left, whiteboard.top + nodewidth, nodewidth, nodewidth), "end")
end0.rect.left = (slotdocu0.rect.left + slotfree0.rect.left)/2

free0 = Place(pygame.Rect(whiteboard.left, whiteboard.top, nodewidth, nodewidth), "free", 1)
free0.rect.left = (start0.rect.left + end0.rect.left)/2
free0.rect.top = (start0.rect.top + end0.rect.top)/2
busy0 = Place(pygame.Rect(whiteboard.left, start0.rect.top, nodewidth, nodewidth), "busy", 1)
busy0.rect.left = (start0.rect.left + change0.rect.left)/2
docu0 = Place(pygame.Rect(whiteboard.left, whiteboard.top, nodewidth, nodewidth), "docu")
docu0.rect.left = (change0.rect.left + end0.rect.left)/2
docu0.rect.top = (change0.rect.top + end0.rect.top)/2

petri0 = PetriNet()
petri0.places = {slotfree0.name : slotfree0, slotbusy0.name : slotbusy0, slotdocu0.name : slotdocu0, free0.name : free0, busy0.name : busy0, docu0.name : docu0}
petri0.transitions = {start0.name : start0, change0.name : change0, end0.name : end0}

petri0.adjList[slotfree0.name] = {end0.name : Arc("1")}
petri0.adjList[slotbusy0.name] = {start0.name : Arc("1")}
petri0.adjList[slotdocu0.name] = {change0.name : Arc("1")}
petri0.adjList[free0.name] = {start0.name : Arc("1")}
petri0.adjList[busy0.name] = {change0.name : Arc("1")}
petri0.adjList[docu0.name] = {end0.name : Arc("1")}
petri0.adjList[start0.name] = {slotfree0.name : Arc("1"), busy0.name : Arc("1")}
petri0.adjList[change0.name] = {slotbusy0.name : Arc("1"), docu0.name : Arc("1")}
petri0.adjList[end0.name] = {slotdocu0.name : Arc("1"), free0.name : Arc("1")}

graph0 = [petri0]
graph0.append(graph0[0].reachabilityGraph(("free", "busy", "docu")))
graph0[1].autoScale(whiteboard)
activeGraph0 = 0
###
###### init graph 1
free1 = Place(pygame.Rect(whiteboard.left + nodewidth, whiteboard.top + nodewidth, nodewidth, nodewidth), "free", 4)
docu1 = Place(pygame.Rect(whiteboard.right - 2*nodewidth, whiteboard.top + nodewidth, nodewidth, nodewidth), "docu")
start1 = Transition(pygame.Rect(whiteboard.left + nodewidth, whiteboard.bottom - 2*nodewidth, nodewidth, nodewidth), "start")
change1 = Transition(pygame.Rect(whiteboard.right - 2*nodewidth, whiteboard.bottom - 2*nodewidth, nodewidth, nodewidth), "change")
end1 = Transition(pygame.Rect((free1.rect.left + docu1.rect.left)/2, whiteboard.top + nodewidth, nodewidth,nodewidth), "end")
busy1 = Place(pygame.Rect(end1.rect.left, whiteboard.bottom - 2*nodewidth, nodewidth, nodewidth), "busy")
graph1 = [PetriNet()]
graph1[0].places = {free1.name : free1, busy1.name : busy1, docu1.name : docu1}
graph1[0].transitions = {start1.name : start1, change1.name : change1, end1.name : end1}
graph1[0].adjList[free1.name] = {start1.name : Arc("1")}
graph1[0].adjList[start1.name] = {busy1.name : Arc("1")}
graph1[0].adjList[busy1.name] = {change1.name : Arc("1")}
graph1[0].adjList[change1.name] = {docu1.name : Arc("1")}
graph1[0].adjList[docu1.name] = {end1.name : Arc("1")}
graph1[0].adjList[end1.name] = {free1.name : Arc("1")}

graph1.append(graph1[0].reachabilityGraph(("free", "busy", "docu")))
graph1[1].autoScale(whiteboard)
activeGraph1 = 0
####
#### init graph 2
wait2 = Place(pygame.Rect(whiteboard.left + nodewidth, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "wait", 5)
done2 = Place(pygame.Rect(whiteboard.right - 2*nodewidth, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "done", 1)
inside2 = Place(pygame.Rect((wait2.rect.left + done2.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "inside")
start2 = Transition(pygame.Rect((wait2.rect.left + inside2.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "start")
change2 = Transition(pygame.Rect((inside2.rect.left + done2.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "change")
graph2 = PetriNet()
graph2.places = {wait2.name : wait2, inside2.name : inside2, done2.name : done2}
graph2.transitions = {start2.name : start2, change2.name : change2}
graph2.adjList[wait2.name] = {start2.name : Arc("1")}
graph2.adjList[start2.name] = {inside2.name : Arc("1")}
graph2.adjList[inside2.name] = {change2.name : Arc("1")}
graph2.adjList[change2.name] = {done2.name : Arc("1")}
graph2.adjList[done2.name] = {}

###
##### init graph 3
wait3 = Place(pygame.Rect(whiteboard.left + nodewidth, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "wait", 3)
done3 = Place(pygame.Rect(whiteboard.right - 2*nodewidth, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "done", 1)
busy3 = Place(pygame.Rect((wait3.rect.left + done3.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "busy")
inside3 = Place(pygame.Rect((wait3.rect.left + done3.rect.left)/2, whiteboard.bottom - 2*nodewidth, nodewidth, nodewidth), "inside")
start3 = Transition(pygame.Rect((wait3.rect.left + inside3.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "start")
change3 = Transition(pygame.Rect((inside3.rect.left + done3.rect.left)/2, whiteboard.top + whiteboard.height/2 - nodewidth/2, nodewidth, nodewidth), "change")
free3 = Place(pygame.Rect(start3.rect.left, whiteboard.top + nodewidth, nodewidth, nodewidth), "free", 1)
end3 = Transition(pygame.Rect(busy3.rect.left, whiteboard.top + nodewidth, nodewidth, nodewidth), "end")
docu3 = Place(pygame.Rect(change3.rect.left, whiteboard.top + nodewidth, nodewidth, nodewidth), "docu")
graph3 = [PetriNet()]
graph3[0].places = {wait3.name : wait3, inside3.name : inside3, done3.name : done3, free3.name : free3, busy3.name : busy3, docu3.name : docu3}
graph3[0].transitions = {start3.name : start3, change3.name : change3, end3.name : end3}
graph3[0].adjList[wait3.name] = {start3.name : Arc("1")}
graph3[0].adjList[inside3.name] = {change3.name : Arc("1")}
graph3[0].adjList[done3.name] = {}
graph3[0].adjList[free3.name] = {start3.name : Arc("1")}
graph3[0].adjList[busy3.name] = {change3.name : Arc("1")}
graph3[0].adjList[docu3.name] = {end3.name : Arc("1")}
graph3[0].adjList[start3.name] = {busy3.name : Arc("1"), inside3.name : Arc("1")}
graph3[0].adjList[change3.name] = {done3.name : Arc("1"), docu3.name : Arc("1")}
graph3[0].adjList[end3.name] = {free3.name : Arc("1")}

graph3.append(graph3[0].reachabilityGraph(("free", "busy", "docu", "wait", "inside", "done")))
graph3[1].autoScale(whiteboard)
activeGraph3 = 0

running = True
mode = 0

# main loop
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mode==1:
        isMoved = 0
        if activeGraph0==0:
            for x in graph0[0].places.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
            for x in graph0[0].transitions.values():
                if x.isMoving:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom += rely
                    isMoved = 1
                    break
                elif x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx*relx + rely*rely > 4:
                        x.isMoving = 1
                        if relx < 0:
                            if x.rect.left + relx < whiteboard.left:
                                x.rect.left = whiteboard.left
                            else:
                                x.rect.left += relx
                        else:
                            if x.rect.right + relx > whiteboard.right:
                                x.rect.right = whiteboard.right
                            else: x.rect.right += relx
                        if rely < 0:
                            if x.rect.top + rely < whiteboard.top:
                                x.rect.top = whiteboard.top
                            else: x.rect.top += rely
                        else:
                            if x.rect.bottom + rely > whiteboard.bottom:
                                x.rect.bottom = whiteboard.bottom
                            else: x.rect.bottom +=rely
                        isMoved = 1
                        break
        else: 
            for x in graph0[1].states.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
        if isMoved:
            pygame.draw.rect(screen, WHITE, whiteboard)
            if activeGraph0==1: screen.blit(note0, whiteboard) 
            graph0[activeGraph0].draw(screen)
            pygame.display.update(whiteboard)
    elif mode==2:
        isMoved = 0
        if activeGraph1==0:
            for x in graph1[0].places.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
            for x in graph1[0].transitions.values():
                if x.isMoving:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom += rely
                    isMoved = 1
                    break
                elif x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx*relx + rely*rely > 4:
                        x.isMoving = 1
                        if relx < 0:
                            if x.rect.left + relx < whiteboard.left:
                                x.rect.left = whiteboard.left
                            else:
                                x.rect.left += relx
                        else:
                            if x.rect.right + relx > whiteboard.right:
                                x.rect.right = whiteboard.right
                            else: x.rect.right += relx
                        if rely < 0:
                            if x.rect.top + rely < whiteboard.top:
                                x.rect.top = whiteboard.top
                            else: x.rect.top += rely
                        else:
                            if x.rect.bottom + rely > whiteboard.bottom:
                                x.rect.bottom = whiteboard.bottom
                            else: x.rect.bottom += rely
                        isMoved = 1
                        break
        else: 
            for x in graph1[1].states.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
        if isMoved:
            pygame.draw.rect(screen, WHITE, whiteboard)
            if activeGraph1==1: screen.blit(note0, whiteboard) 
            graph1[activeGraph1].draw(screen)
            pygame.display.update(whiteboard)
    elif mode==3:
        isMoved = 0
        for x in graph2.places.values():
            if x.isClicked:
                relx, rely = pygame.mouse.get_rel()
                if relx < 0:
                    if x.rect.left + relx < whiteboard.left:
                        x.rect.left = whiteboard.left
                    else:
                        x.rect.left += relx
                else:
                    if x.rect.right + relx > whiteboard.right:
                        x.rect.right = whiteboard.right
                    else: x.rect.right += relx
                if rely < 0:
                    if x.rect.top + rely < whiteboard.top:
                        x.rect.top = whiteboard.top
                    else: x.rect.top += rely
                else:
                    if x.rect.bottom + rely > whiteboard.bottom:
                        x.rect.bottom = whiteboard.bottom
                    else: x.rect.bottom += rely
                isMoved = 1
                break
        for x in graph2.transitions.values():
            if x.isMoving:
                relx, rely = pygame.mouse.get_rel()
                if relx < 0:
                    if x.rect.left + relx < whiteboard.left:
                        x.rect.left = whiteboard.left
                    else:
                        x.rect.left += relx
                else:
                    if x.rect.right + relx > whiteboard.right:
                        x.rect.right = whiteboard.right
                    else: x.rect.right += relx
                if rely < 0:
                    if x.rect.top + rely < whiteboard.top:
                        x.rect.top = whiteboard.top
                    else: x.rect.top += rely
                else:
                    if x.rect.bottom + rely > whiteboard.bottom:
                        x.rect.bottom = whiteboard.bottom
                    else: x.rect.bottom += rely
                isMoved = 1
                break
            elif x.isClicked:
                relx, rely = pygame.mouse.get_rel()
                if relx*relx + rely*rely > 4:
                    x.isMoving = 1
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom += rely
                    isMoved = 1
                    break

        if isMoved:
            pygame.draw.rect(screen, WHITE, whiteboard)
            graph2.draw(screen)
            pygame.display.update(whiteboard)
    elif mode==4:
        isMoved = 0
        if activeGraph3==0:
            for x in graph3[0].places.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
            for x in graph3[0].transitions.values():
                if x.isMoving:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
                elif x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx*relx + rely*rely > 4:
                        x.isMoving = 1
                        relx, rely = pygame.mouse.get_rel()
                        if relx < 0:
                            if x.rect.left + relx < whiteboard.left:
                                x.rect.left = whiteboard.left
                            else:
                                x.rect.left += relx
                        else:
                            if x.rect.right + relx > whiteboard.right:
                                x.rect.right = whiteboard.right
                            else: x.rect.right += relx
                        if rely < 0:
                            if x.rect.top + rely < whiteboard.top:
                                x.rect.top = whiteboard.top
                            else: x.rect.top += rely
                        else:
                            if x.rect.bottom + rely > whiteboard.bottom:
                                x.rect.bottom = whiteboard.bottom
                            else: x.rect.bottom += rely
                        isMoved = 1
                        break
        else: 
            for x in graph3[1].states.values():
                if x.isClicked:
                    relx, rely = pygame.mouse.get_rel()
                    if relx < 0:
                        if x.rect.left + relx < whiteboard.left:
                            x.rect.left = whiteboard.left
                        else:
                            x.rect.left += relx
                    else:
                        if x.rect.right + relx > whiteboard.right:
                            x.rect.right = whiteboard.right
                        else: x.rect.right += relx
                    if rely < 0:
                        if x.rect.top + rely < whiteboard.top:
                            x.rect.top = whiteboard.top
                        else: x.rect.top += rely
                    else:
                        if x.rect.bottom + rely > whiteboard.bottom:
                            x.rect.bottom = whiteboard.bottom
                        else: x.rect.bottom +=rely
                    isMoved = 1
                    break
        if isMoved:
            pygame.draw.rect(screen, WHITE, whiteboard)
            if activeGraph3==1: screen.blit(note1, whiteboard) 
            graph3[activeGraph3].draw(screen)
            pygame.display.update(whiteboard)
    # event handling, gets all event from the event queue
    for event in pygame.event.get():
        # only do something if the event is of type QUIT
        if event.type == pygame.QUIT:
            # change the value to False, to exit the main loop
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if workspace.collidepoint(mouse_x, mouse_y): 
                if mode == 1:
                    if taskbar.collidepoint(mouse_x, mouse_y):
                        if createButton.rect.collidepoint(mouse_x, mouse_y):
                            createButton.active = 1
                            createButton.draw(screen)
                            pygame.display.update(createButton.rect)
                            dict = {"free" : int(token0[0].name), "busy" : int(token0[1].name), "docu" : int(token0[2].name), "slot free" : int(token0[3].name) - int(token0[0].name), "slot busy" : int(token0[4].name) - int(token0[1].name), "slot docu" : int(token0[5].name) - int(token0[2].name)}
                            graph0[0].setMarking(dict)
                            graph0[1] = graph0[0].reachabilityGraph(("free", "busy", "docu"))
                            graph0[1].autoScale(whiteboard)
                            pygame.draw.rect(screen, WHITE, whiteboard)
                            graph0[0].draw(screen)
                            if activeGraph0==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                activeGraph0 = 0
                            createButton.active = 0
                            createButton.draw(screen)
                            pygame.display.update(workspace)
                        elif petriButton.rect.collidepoint(mouse_x, mouse_y):
                            if activeGraph0==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                graph0[0].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph0 = 0
                        elif tsButton.rect.collidepoint(mouse_x, mouse_y):
                            if activeGraph0==0:
                                petriButton.active = 0
                                tsButton.active = 1
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                screen.blit(note0, whiteboard) 
                                graph0[1].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph0 = 1
                        else:
                            for x in range(len(token0)):
                                if upButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    newval = int(token0[x].name) + 1
                                    token0[x].name = str(newval)
                                    token0[x].draw(screen)
                                    if x < 3 and newval > int(token0[x + 3].name):
                                        token0[x + 3].name = str(newval)
                                        token0[x + 3].draw(screen)
                                        pygame.display.update((token0[x].rect, token0[x + 3].rect))
                                    else: pygame.display.update(token0[x].rect)
                                    break
                                elif downButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    newval = int(token0[x].name) - 1
                                    if newval < 0: pass
                                    elif x >= 3 and newval < int(token0[x - 3].name): pass
                                    else: 
                                        token0[x].name = str(newval)
                                        token0[x].draw(screen)
                                        pygame.display.update(token0[x].rect)
                                    break
                    elif whiteboard.collidepoint(mouse_x, mouse_y): 
                        if activeGraph0==0:
                            for x in graph0[0].places.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                            for x in graph0[0].transitions.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                        else:
                            for x in graph0[1].states.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                elif mode==2: 
                    if taskbar.collidepoint(mouse_x, mouse_y): 
                        if createButton.rect.collidepoint(mouse_x, mouse_y): 
                            createButton.active = 1
                            createButton.draw(screen)
                            pygame.display.update(createButton.rect)
                            dict = {"free" : int(token1[0].name), "busy" : int(token1[1].name), "docu" : int(token1[2].name)}
                            graph1[0].setMarking(dict)
                            graph1[1] = graph1[0].reachabilityGraph(("free", "busy", "docu"))
                            graph1[1].autoScale(whiteboard)
                            pygame.draw.rect(screen, WHITE, whiteboard)
                            graph1[0].draw(screen)
                            if activeGraph1==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                activeGraph1 = 0
                            createButton.active = 0
                            createButton.draw(screen)
                            pygame.display.update(workspace)
                        elif petriButton.rect.collidepoint(mouse_x, mouse_y): 
                            if activeGraph1==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                graph1[0].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph1 = 0
                        elif tsButton.rect.collidepoint(mouse_x, mouse_y): 
                            if activeGraph1==0:
                                petriButton.active = 0
                                tsButton.active = 1
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                screen.blit(note0, whiteboard) 
                                graph1[1].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph1 = 1
                        else:
                            for x in range(len(token1)):
                                if upButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    token1[x].name = str(int(token1[x].name) + 1)
                                    token1[x].draw(screen)
                                    pygame.display.update(token1[x].rect)
                                    break
                                elif downButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    newval = int(token1[x].name) - 1
                                    if newval < 0: pass
                                    else:
                                        token1[x].name = str(newval)
                                        token1[x].draw(screen)
                                        pygame.display.update(token1[x].rect)
                                    break
                    elif whiteboard.collidepoint(mouse_x, mouse_y): 
                        if activeGraph1==0:
                            for x in graph1[0].places.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                            for x in graph1[0].transitions.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                        else:
                            for x in graph1[1].states.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                elif mode==3: 
                    if taskbar.collidepoint(mouse_x, mouse_y): 
                        if createButton.rect.collidepoint(mouse_x, mouse_y): 
                            createButton.active = 1
                            createButton.draw(screen)
                            pygame.display.update(createButton.rect)
                            dict = {"wait" : int(token2[0].name), "inside" : int(token2[1].name), "done" : int(token2[2].name)}
                            graph2.setMarking(dict)
                            pygame.draw.rect(screen, WHITE, whiteboard)
                            graph2.draw(screen)
                            createButton.active = 0
                            createButton.draw(screen)
                            pygame.display.update((createButton.rect, whiteboard))
                        else:
                            for x in range(len(token2)):
                                if upButtons[x + 3].rect.collidepoint(mouse_x, mouse_y):
                                    token2[x].name = str(int(token2[x].name) + 1)
                                    token2[x].draw(screen)
                                    pygame.display.update(token2[x].rect)
                                    break
                                elif downButtons[x + 3].rect.collidepoint(mouse_x, mouse_y):
                                    newval = int(token2[x].name) - 1
                                    if newval < 0: pass
                                    else:
                                        token2[x].name = str(newval)
                                        token2[x].draw(screen)
                                        pygame.display.update(token2[x].rect)
                                    break
                    elif whiteboard.collidepoint(mouse_x, mouse_y): 
                        for x in graph2.places.values():
                            if x.rect.collidepoint(mouse_x, mouse_y):
                                x.isClicked = 1
                                pygame.mouse.get_rel()
                                break
                        for x in graph2.transitions.values():
                            if x.rect.collidepoint(mouse_x, mouse_y):
                                x.isClicked = 1
                                pygame.mouse.get_rel()
                                break
                elif mode==4: 
                    if taskbar.collidepoint(mouse_x, mouse_y):
                        if createButton.rect.collidepoint(mouse_x, mouse_y):
                            createButton.active = 1
                            createButton.draw(screen)
                            pygame.display.update(createButton.rect)
                            dict = {"free" : int(token3[0].name), "busy" : int(token3[1].name), "docu" : int(token3[2].name), "wait" : int(token3[3].name), "inside" : int(token3[4].name), "done" : int(token3[5].name)}
                            graph3[0].setMarking(dict)
                            graph3[1] = graph3[0].reachabilityGraph(("free", "busy", "docu", "wait", "inside", "done"))
                            graph3[1].autoScale(whiteboard)
                            pygame.draw.rect(screen, WHITE, whiteboard)
                            graph3[0].draw(screen)
                            if activeGraph3==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                activeGraph3 = 0
                            createButton.active = 0
                            createButton.draw(screen)
                            pygame.display.update(workspace)
                        elif petriButton.rect.collidepoint(mouse_x, mouse_y):
                            if activeGraph3==1:
                                petriButton.active = 1
                                tsButton.active = 0
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                graph3[0].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph3 = 0
                        elif tsButton.rect.collidepoint(mouse_x, mouse_y):
                            if activeGraph3==0:
                                petriButton.active = 0
                                tsButton.active = 1
                                petriButton.draw(screen)
                                tsButton.draw(screen)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                screen.blit(note1, whiteboard) 
                                graph3[1].draw(screen)
                                pygame.display.update(workspace)
                                activeGraph3 = 1
                        else:
                            for x in range(len(token3)):
                                if upButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    token3[x].name = str(int(token3[x].name) + 1)
                                    token3[x].draw(screen)
                                    pygame.display.update(token3[x].rect)
                                    break
                                elif downButtons[x].rect.collidepoint(mouse_x, mouse_y):
                                    newval = int(token3[x].name) - 1
                                    if newval < 0: pass
                                    else:
                                        token3[x].name = str(newval)
                                        token3[x].draw(screen)
                                        pygame.display.update(token3[x].rect)
                                    break
                    elif whiteboard.collidepoint(mouse_x, mouse_y): 
                        if activeGraph3==0:
                            for x in graph3[0].places.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                            for x in graph3[0].transitions.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
                        else:
                            for x in graph3[1].states.values():
                                if x.rect.collidepoint(mouse_x, mouse_y):
                                    x.isClicked = 1
                                    pygame.mouse.get_rel()
                                    break
            else:
                for x in range(len(wsButtons)):
                    if wsButtons[x].rect.collidepoint(mouse_x, mouse_y) and x!=mode:
                        pygame.draw.rect(screen, NAVY, taskbar)
                        pygame.draw.rect(screen, WHITE, whiteboard)
                        wsButtons[x].active = 1
                        wsButtons[x].draw(screen)
                        wsButtons[mode].active = 0
                        wsButtons[mode].draw(screen)
                        mode = x
                        if x==0:
                            for x in guides:
                                x.draw(screen)
                        elif x==1:
                            if activeGraph0==0: 
                                petriButton.active = 1
                                tsButton.active = 0
                            else:
                                screen.blit(note0, whiteboard) 
                                petriButton.active = 0
                                tsButton.active = 1
                            petriButton.draw(screen)
                            tsButton.draw(screen)
                            text0.draw(screen)
                            text1.draw(screen)
                            text2.draw(screen)
                            text3.draw(screen)
                            text4.draw(screen)
                            text5.draw(screen)
                            for x in range(len(token0)):
                                token0[x].draw(screen)
                                upButtons[x].draw(screen)
                                downButtons[x].draw(screen)  
                            graph0[activeGraph0].draw(screen)
                        elif x==2:
                            if activeGraph1==0: 
                                petriButton.active = 1
                                tsButton.active = 0
                            else:
                                screen.blit(note0, whiteboard) 
                                petriButton.active = 0
                                tsButton.active = 1
                            petriButton.draw(screen)
                            tsButton.draw(screen)
                            text0.draw(screen)
                            text1.draw(screen)
                            text2.draw(screen)
                            for x in range(len(token1)):
                                token1[x].draw(screen)
                                upButtons[x].draw(screen)
                                downButtons[x].draw(screen)
                            graph1[activeGraph1].draw(screen)
                        elif x==3:
                            text6.draw(screen)
                            text7.draw(screen)
                            text8.draw(screen)
                            for x in range(len(token2)):
                                token2[x].draw(screen)
                                upButtons[x + 3].draw(screen)
                                downButtons[x + 3].draw(screen)
                            graph2.draw(screen)
                        elif x==4:
                            if activeGraph3==0: 
                                petriButton.active = 1
                                tsButton.active = 0
                            else:
                                screen.blit(note1, whiteboard) 
                                petriButton.active = 0
                                tsButton.active = 1
                            petriButton.draw(screen)
                            tsButton.draw(screen)
                            text0.draw(screen)
                            text1.draw(screen)
                            text2.draw(screen)
                            text6.draw(screen)
                            text7.draw(screen)
                            text8.draw(screen)
                            for x in range(len(token3)):
                                token3[x].draw(screen)
                                upButtons[x].draw(screen)
                                downButtons[x].draw(screen) 
                            graph3[activeGraph3].draw(screen)
                        if mode!=0: createButton.draw(screen)                           
                        #Button(whiteboard, "Set initial marking and click CREATE button to create a new petrinet").draw(screen)
                        pygame.display.flip()
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if mode==1:
                if activeGraph0==0:
                    for x in graph0[0].places.values():
                        if x.isClicked:
                            x.isClicked = 0
                            break
                    for x in graph0[0].transitions.values():
                        if x.isClicked:
                            if x.isMoving==0 and graph0[0].isEnable(x.name):
                                graph0[0].firing(x.name)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                graph0[0].draw(screen)
                                #pygame.display.update(whiteboard)
                            x.isMoving = 0
                            x.isClicked = 0
                            break
                else:
                    for x in graph0[1].states.values():
                        if x.isClicked:
                            x.isClicked = 0
                            break
            elif mode==2:
                if activeGraph1==0:
                    for x in graph1[0].places.values():
                        if x.isClicked:
                            x.isClicked = 0
                            break
                    for x in graph1[0].transitions.values():
                        if x.isClicked:
                            if x.isMoving==0 and graph1[0].isEnable(x.name):
                                graph1[0].firing(x.name)
                                pygame.draw.rect(screen, WHITE, whiteboard)
                                graph1[0].draw(screen)
                                #pygame.display.update(whiteboard)
                            x.isMoving = 0
                            x.isClicked = 0
                            break
                else:
                    for x in graph1[1].states.values():
                        if x.isClicked:
                            x.isClicked = 0
                            break
            elif mode==3:
                for x in graph2.places.values():
                    if x.isClicked:
                        x.isClicked = 0
                        break
                for x in graph2.transitions.values():
                    if x.isClicked:
                        if x.isMoving==0 and graph2.isEnable(x.name):
                            graph2.firing(x.name)
                            pygame.draw.rect(screen, WHITE, whiteboard)
                            graph2.draw(screen)
                            #pygame.display.update(whiteboard)
                        x.isMoving = 0
                        x.isClicked = 0
                        break
            elif mode==4:
                    if activeGraph3==0:
                        for x in graph3[0].places.values():
                            if x.isClicked:
                                x.isClicked = 0
                                break
                        for x in graph3[0].transitions.values():
                            if x.isClicked:
                                if x.isMoving==0 and graph3[0].isEnable(x.name):
                                    graph3[0].firing(x.name)
                                    pygame.draw.rect(screen, WHITE, whiteboard)
                                    graph3[0].draw(screen)
                                    #pygame.display.update(whiteboard)
                                x.isMoving = 0
                                x.isClicked = 0
                                break
                    else:
                        for x in graph3[1].states.values():
                            if x.isClicked:
                                x.isClicked = 0
                                break
        elif event.type == pygame.WINDOWSIZECHANGED:
            kx = event.x/WIDTH
            ky = event.y/HEIGHT
            WIDTH = event.x
            HEIGHT = event.y
            refeshScreen(kx, ky)
        elif event.type == pygame.WINDOWFOCUSGAINED:
            pygame.display.flip()



