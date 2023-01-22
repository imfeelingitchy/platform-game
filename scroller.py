
#############################################################
### _-_-_-_- SMOOTH-SCROLLING PLATFORMING SCRIPT -_-_-_-_ ###
#############################################################

# Intellectual Property of Rithik Raja
# Shockingly implemented without classes or any Pygame Sprite Methods
# Damn fun to play

# Credits: Images from kenney.nl (used under public domain license)

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import random as rd
import numpy as np
import math, time
from data import *
import leveldata_retriever as lr
import communicator as comm

#####   PLAYER FUNCTIONS   #####

#Load player images and initialize player variables
def loadplayer():
    def static_img(img):
        global player_images
        player_images.append([])
        player_images[len(player_images)-1].append(pg.transform.flip(pg.image.load(img).convert_alpha(), True, False))
        player_images[len(player_images)-1].append(None)
        player_images[len(player_images)-1].append(pg.image.load(img).convert_alpha())
    global x, y, w, h, xvel, yvel, xacc, yacc, c, canjump, player_images, player_images_count, cur_img, direc, flying, xold, yold, xvel2, downslope
    os.chdir(os.path.dirname(__file__))
    os.chdir(os.path.join(os.getcwd(), 'walk1'))
    player_images = [[]]
    player_images_count = 0
    for i in range(1, 12):
        player_images[0].append(pg.transform.flip(pg.image.load('p1_walk' + str(i) + '.png').convert_alpha(), True, False))
    static_img('p1_stand.png')
    player_images.append([])
    for i in range(1, 12):
        player_images[2].append(pg.image.load('p1_walk' + str(i) + '.png').convert_alpha())
    static_img('p1_jump.png')
    x = xold = ww/2
    y = yold = wh/2
    w = player_images[1][0].get_rect()[2]
    w -= 20
    h = player_images[1][0].get_rect()[3]
    h -= 10
    c = blue
    xvel = xvel2 =  0
    yvel = 0
    xacc = 2
    yacc = 1
    canjump = 0
    direc = -1
    flying = 1
    downslope = 0

#Player movement: vertical component      
def movevertical():
    def comeout():
        #Find quickest way out of moving platform
        global x, y
        nonlocal vdirec
        temp = y
        ct = 0
        while touching(x, y, 1):
            y += 1
            ct += 1
        ct2 = 0
        y = temp
        while touching(x, y, 1):
            y -= 1
            ct2 += 1
        if ct > ct2:
            vdirec = 1
        else:
            vdirec = -1
        y = temp
    global landy, yvel, xvel, y, x, canjump, flying, gameover, downslope, yold, xold, xvel2
    #Smoothness factor increases as player approaches top/bottom of screen
    smooth = abs(y - wh/2)/(wh/2)
    k = pg.key.get_pressed()
    #Jump
    if k[pg.K_UP] and canjump:
        yvel = 22
        canjump = 0
        flying = 1
    canjump = 0
    #Gravity: affected by longer keypresses
    if k[pg.K_UP] or yvel <= 0:
        yvel -= yacc
    else:
        yvel -= yacc * 1.3
    if landy > -5000:
        #Move land and player relative to each other based on smoothness factor
        landy += yvel * (smooth)
        y -= yvel * (1 - smooth)
        #Preserve old y-coordinate
        yold = y + yvel
        #Push player towards center of screen using section formula and correspondingly move the screen
        ytemp = (y * scroll_smoothness + (wh/2) * smooth)/(smooth + scroll_smoothness)
        dist = ytemp - y
        y += dist
        landy += dist
        updatelandpos()
    else:
        #End game if player has fallen
        if y < wh + 100:
            y -= yvel
        else:
            gameover = 1
            pg.mixer.Sound.play(slap_sound)
    #Init secondary xvel for moving platforms
    xvel2 = 0
    c = touching(x, y, 1)
    #If touching moving platform, revert all moving platforms to their previous frame and check whether touching using old y-coordinate
    if c:
        movelandy(-1)
        t = touching(xold, yold, 1)
        if not t:
            t = leveldata[c[8]]
            #Above in previous frame
            if yold + h < t[1]:
                vdirec = 1
            #Below in previous frame
            elif t[1] + t[3] < yold:
                vdirec = -1
            #Ideally, the following 'else' should not be entered as it implies that touching occured even though the outer 'if' implies the opposite.
            #However, due to any inaccuracy, if the 'else' is entered, find the quickest out.
            else:
                movelandy(1)
                comeout()
                return None
            movelandy(1)
            #Set secondary xvel if touching moving platform from above
            if vdirec == 1 and t[5]['axis'] == 0:
                xvel2 = t[5]['vel']
        #If touching in previous frame, find quickest way out.
        else:
            t = leveldata[c[8]]
            movelandy(1)
            comeout()
            #Set secondary xvel if touching moving platform from above
            if vdirec == 1 and t[5]['axis'] == 0:
                xvel2 = t[5]['vel']
        #Come out of moving platform
        while touching(x, y, 1):
            y -= vdirec
        if vdirec == 1:
            #Enable jumping if touching from above
            yvel = 0
            canjump = 1
            flying = 0
            #Force the player down with velocity comparable to that of moving platform to prevent:
            #   1. the player from sticking to bottom of moving platform
            #   2. the player from 'skipping' when on top of moving platform
            if t[5]['vel']/10 > 0:
                yvel = -t[5]['vel']/1
            else:
                yvel = 0
        else:
            if t[5]['vel']/10 > 0:
                yvel = -t[5]['vel']/1
            else:
                yvel = 0
    #If touching normal platform, come out based on sign of yvel 
    elif touching(x, y) and yvel != 0:
        count = 0
        vdirec = np.sign(yvel)
        while touching(x, y):
            count += 1
            y += vdirec
        if vdirec == -1:
            flying = 0
        if not k[pg.K_UP]:
            canjump = 1
        #If on downslope, force player down to avoid 'skipping'
        if not downslope:
            yvel = 0
        else:
            yvel = downslope
            downslope = 0
        
def movehorizontal():
    def comeout():
        global x, y
        nonlocal hdirec
        temp = x
        ct = 0
        while touching(x, y, 1):
            x += 1
            ct += 1
        ct2 = 0
        x = temp
        while touching(x, y, 1):
            x -= 1
            ct2 += 1
        if ct > ct2:
            hdirec = 1
        else:
            hdirec = -1
        x = temp
    global landx, xvel, yvel, x, direc, y, flying, downslope, xold, yold, canjump
    #Smoothness factor increases as player approaches extreme left/right of screen
    smooth = abs(x - ww/2)/(ww/2)
    k = pg.key.get_pressed()
    #Move left/right
    if k[pg.K_LEFT]:
        direc = -1
        xvel -= xacc
    if k[pg.K_RIGHT]:
        direc = 1
        xvel += xacc
    #Friction
    xvel = 0.85 * xvel
    #Move land and player relative to each other based on smoothness factor
    landx -= xvel * smooth
    x += (xvel + xvel2) * (1-smooth)
    #Preserve old x-coordinate
    xold = x - (xvel + xvel2)
    #Push player towards center of screen using section formula and correspondingly move the screen
    xtemp = (x * scroll_smoothness + (ww/2) * smooth)/(smooth + scroll_smoothness)
    dist = xtemp - x
    x += dist
    landx += dist
    updatelandpos()
    c = touching(x, y, 1)
    #If touching moving platform, revert all moving platforms to their previous frame and check whether touching using old x-coordinate
    if c:
        movelandx(-1)
        t = touching(xold, yold, 1)
        if not t:
            t = leveldata[c[8]]
            #To the left in previous frame
            if xold + w < t[0]:
                hdirec = 1
            #To the right in previous frame
            elif t[0] + t[2] < xold:
                hdirec = -1
            #Ideally, the following 'else' should not be entered as it implies that touching occured even though the outer 'if' implies the opposite.
            #However, due to any inaccuracy, if the 'else' is entered, find the quickest out.
            else:
                movelandx(1)
                comeout()
                return None
            movelandx(1)
        #If touching in previous frame, find quickest way out.
        else:
            movelandx(1)
            comeout()
        #Come out of moving platform
        while touching(x, y, 1):
            x -= hdirec
        xvel = 0
    #If touching normal platform...
    elif touching(x, y):
        #Slightly boost y-coordinate upwards
        y -= abs(xvel)
        if touching(x, y):
            #If still touching even with a boosted y-coordinate, then player is touching wall
            y += abs(xvel)
            hdirec = np.sign(xvel)
            #Come out of wall
            while touching(x, y):
                x -= hdirec
            xvel = 0
        #If no longer touching with a boosted y-coordinate, then player is on upslope
        else:
            y += abs(xvel)
            #Come out of upslope
            while touching(x, y):
                y -= 1
    elif not flying:
        #Slightly boost y-coordinate downwards
        y += 20
        #Given player initially not touching, but touching with boosted y-coordinate, then player is on downslope
        if touching(x, y):
            count = 0
            #Come out of downslope
            while touching(x, y):
                count += 1
                y -= 1
            #Set downslope variable to force player down in movevertical()
            downslope = -(20 - count)
        else:
            y -= 20

def drawplayer():
    global player_images_count, direc, canjump
    player_images_count += 1
    if flying:
        #Draw jumping img
        cur_img = player_images[3][direc + 1]
    elif abs(xvel)//1 == 0:
        #Draw stationary img
        cur_img = player_images[1][direc + 1]
    else:
        #Draw walking img
        cur_img = player_images[direc + 1][player_images_count % 11]
    win.blit(cur_img, (x-10, y-10))

#Returns empty tuple if player is not touching anything, else returns tuple of all
#info of block being touched along with its index in the leveldata list
def touching(x, y, m = 0):
    r = ()
    c = 0
    for i in leveldata:
        moving = 'move' in i[5]
        if not moving and m == 0 or moving and m == 1:# or m == 2:
            r = subtouching(i, x, y)
            if r:
                break
        c += 1
    if r:
        return r + (c,)
    else:
        return r

#Check touching for specific block by virtue of x & y coordinates, widths, and heights
def subtouching(i, x, y):
    global gameover
    r = ()
    #If block is interactive:
    if i[5].get('coll', 1):
        #Rectangular collision applied first
        if x + w > i[0] and x - i[2] < i[0] and y - i[3] < i[1] and y + h > i[1]:
            #If rectangle
            if 'coll' not in i[5]:
                r = i
            #Elif trinagle
            elif i[5].get('coll') in ('tri', 'tri2'):
                if i[5].get('coll') == 'tri':
                    x1 = i[0] + i[2]
                    x2 = i[0]
                    y1 = i[1]
                    y2 = i[1] + i[3]
                    xx = x + w
                    yy = y + h
                elif i[5].get('coll') == 'tri2':
                    x1 = i[0]
                    x2 = i[0] + i[2]
                    y1 = i[1]
                    y2 = i[1] + i[3]
                    xx = x
                    yy = y + h
                #Apply two-point formula of straight line to obtain hypotenuse of triangle, then treat as an inequality to determine collision
                if yy > ((y2 - y1) / (x2 - x1)) * (xx - x1) + y1:
                    r = i
            #Collision type 'up' => only collides on hitting vertically downwards
            #Elif collision type is 'up' and falling down and bottom of player is above top of block in previous frame
            elif i[5].get('coll') == 'up' and yvel <= 0 and round(y + yvel + h) <= round(i[1]):
                r = i
            elif i[5].get('coll') == 'death':
                gameover = 1
                pg.mixer.Sound.play(slap_sound)
            elif i[5].get('coll') == 'finish':
                gameover = 2
                pg.mixer.Sound.play(finish_sound)
    return tuple(r)

#####   LAND FUNCTIONS   #####
def drawland_old():
    once = 1
    for i in leveldata:
        if once and i[5].get('front', 0) == 2:
            drawplayer()
            once = 0
        #If object not on screen, continue
        if (i[0] + i[2] < 0 or i[0] > ww or i[1] + i[3] < 0 or i[1] > wh) and not 'txt' in i[5]:
            continue
        #Drawing of land is split into 3 layers. Order of appearance: 2 -> player -> 1 -> 0
        if i[4] == '1':
            #Rectangles (unused)
            pg.draw.rect(win, white, (i[0], i[1], i[2], i[3]))
        elif i[4] == '2':
            #Text
            text(i[5]['txt'], i[0], i[1], i[5]['size'], i[5]['colour'])
        else:
            #Images
            win.blit(tileset[i[4]][0], (i[0], i[1]))
        #Shadow effect
        if i[5].get('dark', 0):
            s = pg.Surface((i[2], i[3]))
            s.fill(black)
            s.set_alpha(i[5]['dark'])
            win.blit(s, (i[0], i[1]))
    if once:
        drawplayer()

def drawland(layer):
    try:
        l_temp = leveldata[np.array(list(map(lambda x: x.get('front', 0) == layer, leveldata[:, 5])))]
    except:
        l_temp = []
    for i in l_temp:
        #If object not on screen, continue
        if (i[0] + i[2] < 0 or i[0] > ww or i[1] + i[3] < 0 or i[1] > wh) and not 'txt' in i[5]:
            continue
        #Drawing of land is split into 4 layers. Order of appearance: 3 -> 2 -> player -> 1 -> 0
        if i[4] == '1':
            #Rectangles (unused)
            pg.draw.rect(win, white, (i[0], i[1], i[2], i[3]))
        elif i[4] == '2':
            #Text
            text(i[5]['txt'], i[0], i[1], i[5]['size'], i[5]['colour'])
        else:
            #Images
            win.blit(tileset[i[4]][0], (i[0], i[1]))
        #Shadow effect
        if i[5].get('dark', 0):
            s = pg.Surface((i[2], i[3]))
            s.fill(black)
            s.set_alpha(i[5]['dark'])
            win.blit(s, (i[0], i[1]))

#Must me called each time landx/landy is modified
def updatelandpos():
    try:
        leveldata[:, 0] = leveldata[:, 6] + landx
        leveldata[:, 1] = leveldata[:, 7] + landy
    except:
        pass

#Move moving platforms (x)            
def movelandx(d = 1):
    for i in leveldata:
        if 'move' in i[5] and i[5].get('axis') == 0:
            p = i[5]['sinpower']/100 * d
            i[5]['sinvalue'] += p
            i[6] = i[5]['sintemp'] + math.sin(i[5]['sinvalue']) * i[5]['sinlength']
            i[5]['vel'] = i[5]['sinlength'] * (math.sin(i[5]['sinvalue']) - math.sin(i[5]['sinvalue'] - p)) / 0.85
            updatelandpos()

#Move moving platforms (y)
def movelandy(d = 1):
    for i in leveldata:
        if 'move' in i[5] and i[5].get('axis') == 1:
            p = i[5]['sinpower']/100 * d
            i[5]['sinvalue'] += p
            i[7] = i[5]['sintemp'] + math.sin(i[5]['sinvalue']) * i[5]['sinlength']
            i[5]['vel'] = i[5]['sinlength'] * (math.sin(i[5]['sinvalue']) - math.sin(i[5]['sinvalue'] - p))
            updatelandpos()

def get_tiles_old():
    global tileset
    tileset = {}
    os.chdir(os.path.dirname(__file__))
    os.chdir(os.path.join(os.getcwd(), 'Tiles'))
    d = os.listdir()
    for i in d:
        try:
            temp = pg.image.load(i).convert_alpha()
            tileset[i] = (temp, temp.get_rect()[2], temp.get_rect()[3])
        except:
            pass

def get_tiles():
    global tileset
    tileset = {}
    os.chdir(os.path.dirname(__file__))
    os.chdir(os.path.join(os.getcwd(), 'Tiles'))
    folders = ('green', 'brown', 'cream', 'grey', 'browngrey', 'purple', 'white', 'misc', 'the rest')
    c = 0
    for folder in folders:
        os.chdir(os.path.join(os.getcwd(), folder))
        d = os.listdir()
        for i in d:
            try:
                temp = pg.image.load(i).convert_alpha()
                tileset[i] = (temp, temp.get_rect()[2], temp.get_rect()[3], c)
            except:
                pass
            c += 1
        os.chdir('..')

#####   TEXT FUNCTIONS   #####

#Draw text
def text(txt, x, y, size, colour):
    t = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), size)
    t2 = t.render(txt, False, colour)
    t2.convert()
    win.blit(t2, (x, y))

#####   DRIVER CODE   #####

#init game
pg.init()
pg.mixer.init()
#pg.display.init()
pg.font.init()
ww = int(1600/1.1)
wh = int(900/1.1)
clock = pg.time.Clock()
win = pg.display.set_mode((ww, wh), pg.FULLSCREEN)
pg.display.set_caption(name_scroller)
run = True

#init game particulars
get_tiles()
loadplayer()
#leveldata = lr.addleveldata(tileset)
#lr.connect()
#leveldata = lr.importleveldata(1)
leveldata = comm.leveldata
leveldata = np.array(sorted(leveldata, key = lambda x: x[5].get('front', 0)))
landx = 22
landy = 152
gameover = 0
os.chdir(os.path.dirname(__file__))
slap_sound = pg.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'slap.wav'))
finish_sound = pg.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'honk.ogg'))
music_loop = pg.mixer.music.load(os.path.join(os.getcwd(), 'sounds', 'electroman adventures.ogg'))

#Rate at which camera adjusts to match player's position
scroll_smoothness = 5

#Get background(s)
os.chdir(os.path.join(os.getcwd(), 'Backgrounds'))
bg = pg.transform.scale(pg.image.load('bg_grasslands.png').convert(), (ww, wh))

pg.mixer.music.play(-1)
#MAIN LOOP
while run:
    clock.tick(fps)
    for event in pg.event.get():
        #Check for quit
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                run = False
            elif event.key == pg.K_r and gameover:
                gameover = 0
                landx = 22
                landy = 152
                xvel = 0
                yvel = 0
                x = xold = ww/2
                y = yold = wh/2
                canjump = 0
                direc = -1
                flying = 1
                downslope = 0
                pg.mixer.music.play(-1)
                

    if not gameover:
        movelandx()
        movehorizontal()
        movelandy()
        movevertical()
        win.blit(bg, (0, 0))
        text("FPS: " + str(round(clock.get_fps(), 1)), 20, 20, 50, skyblue)
        drawland(0)
        drawland(1)
        drawplayer()
        drawland(2)
        drawland(3)
    else:
        pg.mixer.music.stop()
        win.fill(black)
        if gameover == 1:
            text('You Died Lol', 450, 300, 100, white)
            text('Esc to quit', 470, 500, 50, white)
            text('R to retry', 470, 550, 50, white)
        else:
            text('Level Complete', 400, 300, 100, white)
            text('Esc to quit', 420, 500, 50, white)
            text('R to play again', 420, 550, 50, white)
    pg.display.flip()
    

comm.rval = 4
pg.quit()
