import os, time, random, sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import communicator as comm
from data import *

def scale(who, wfac, hfac):
    return pg.transform.scale(who, (int(who.get_rect()[2] * wfac), int(who.get_rect()[3] * hfac))).convert_alpha()

def sizeup(who, wfac, hfac):
    return pg.transform.scale(who, (who.get_rect()[2] + wfac, who.get_rect()[3] + hfac)).convert_alpha()

def move(obj):
    if obj[9] == 0:
        if obj[8] > 0:
            obj[4] += obj[6]
            obj[5] += obj[7]
            obj[2] += obj[4]
            obj[3] += obj[5]
            obj[8] -= 1
            obj[1] = scale(obj[0], obj[10], obj[10])
            obj[10] += obj[11]
    else:
        obj[9] -= 1
    return obj

def blit(obj):
    if obj[8] != 0 and obj[9] == 0 or obj[12] == 1:
        win.blit(obj[1], (obj[2], obj[3]))

pg.init()
pg.font.init()
font = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), 80)
font2 = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), 40)
font3 = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), 60)
'''font = pg.font.SysFont('Tahoma', 60)
font3 = pg.font.SysFont('Tahoma', 80)
try:
    font2 = pg.font.SysFont('sfcompacttextitalicttf', 100)
except:
    font2 = pg.font.SysFont('Arial', 100)'''

ww = 1200
wh = 675
win = pg.display.set_mode((ww, wh))
pg.display.set_caption(name_title)

os.chdir(os.path.dirname(__file__))

run = True

blitlist = []

#Surface object for fading in background
bg = pg.Surface((ww, wh))
bg.fill(skyblue)
bg.convert()

#Shadow effect
shad = pg.Surface((250, 125))
shad.fill(black)
shad.set_alpha(50)

#templist format: [reference surface object, displayed surface object, x, y, xvel, yvel, xacc, yacc, no. of frames, frame delay, initial size factor, size increment factor, infinitely displayed or not]

#Clouds
for i in range(20):
    tempimg = pg.image.load(os.path.join(os.getcwd(), 'Tiles', 'misc', 'cloud' + str(random.randint(1, 3)) + '.png')).convert_alpha()
    templist = [tempimg, tempimg, 60 * (i - random.random()), -50 * (1 + random.random()) - 50, 0, random.randint(15, 20), 0, -1, 15, i * 2, 1, 0.03, 1]
    blitlist.append(templist)

#Hills
for i in range(10):
    tempimg = pg.image.load(os.path.join(os.getcwd(), 'Tiles', 'misc', 'hill_large.png')).convert_alpha()
    templist = [tempimg, tempimg, 120 * i, 30 * (1 + random.random()) + wh, 0, random.randint(-20, -15), 0, 1, 15, i * 2, 1, 0.03, 1]
    blitlist.append(templist)

#Box for 'create account' option
tempimg = pg.Surface((250, 125))
tempimg.fill(black)
templist = [tempimg, tempimg, -300, wh/2 + 50, 60, 0, -3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)
tempimg = pg.Surface((240, 115))
tempimg.fill(aquablue)
templist = [tempimg, tempimg, -300 + 5, wh/2 + 50 + 5, 60, 0, -3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)

#Title
tempimg = font.render('A Generic Platform Game', True, black)
templist = [tempimg, tempimg, ww/2 - tempimg.get_width()/2, -100, 0, 26, 0, -1, 26, 120, 1, 0, 1]
blitlist.append(templist)

#Text: 'Create account'
tempimg = font2.render('Create an', True, black)
templist = [tempimg, tempimg, -300 + 30, wh/2 + 55 + 20, 60, 0, -3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)
tempimg = font2.render('Account', True, black)
templist = [tempimg, tempimg, -300 + 45, wh/2 + 55 + 60, 60, 0, -3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)

#Box for 'Log in' option
tempimg = pg.Surface((250, 125))
tempimg.fill(black)
templist = [tempimg, tempimg, ww + 50, wh/2 + 50, -60, 0, 3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)
tempimg = pg.Surface((240, 115))
tempimg.fill(aquablue)
templist = [tempimg, tempimg, ww + 50 + 5, wh/2 + 50 + 5, -60, 0, 3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)

#Text: 'Log in'
tempimg = font3.render('Log In', True, black)
templist = [tempimg, tempimg, ww + 50 + 45, wh/2 + 50 + 35, -60, 0, 3, 0, 20, 130, 1, 0, 1]
blitlist.append(templist)

#Flying demo player
tempimg = pg.image.load(os.path.join(os.getcwd(), 'walk1', 'p1_jump.png')).convert_alpha()
templist = [tempimg, tempimg, -200, 800, 22, -38, -0.3, 1, 80, 50, 2.5, 0.03, 0]
blitlist.append(templist)

clock = pg.time.Clock()
fc = -1
pos = ((ww + 50 - 570, wh/2 + 50, 1), (-300 + 570, wh/2 + 50, 2))

while run:
    fc += 1
    clock.tick(fps)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN and t != 0:
            comm.rval = t + 1
            run = False

    t = 0
    mx, my = pg.mouse.get_pos()
    for i in pos:
        if mx > i[0] and mx < i[0] + 250 and my > i[1] and my < i[1] + 125:
            t = i[2]

    for i in blitlist:
        move(i)
    
    if fc * 8 <= 255:
        win.fill(midnightblue)
    else:
        win.fill(skyblue)

    if fc * 8 <= 255:
        bg2 = bg
        bg2.set_alpha(fc * 8)
        win.blit(bg2, (0, 0))
        

    for i in blitlist:
        blit(i)

    if t != 0  and fc > 155:
        win.blit(shad, (pos[t - 1][0], pos[t - 1][1]))
        
    
    pg.display.flip()
    
pg.quit()
