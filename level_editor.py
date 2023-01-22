import os
import sys
import leveldata_retriever as lr
from data import *
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import numpy as np
import communicator as comm

def init_game():
    global win, clock
    pg.init()
    pg.display.init()
    pg.font.init()
    win = pg.display.set_mode((ww, wh))
    pg.display.set_caption(name_level_editor)
    clock = pg.time.Clock()


def update_mouse_pos():
    global ms_pos
    ms = pg.mouse.get_pos()
    ms_pos = -(gridx - ms[0]), gridy - ms[1], ms[0], ms[1]
    
def draw_grid():
    global gridx, gridy, ms_pos
    for i in range(-70 + int(gridx) % 70, ww + 70, 70):
        pg.draw.line(win, black, (i, 0), (i, wh))
    for i in range(-70 + int(gridy) % 70, wh + 70, 70):
        pg.draw.line(win, black, (0, i), (ww, i))
    #ms = pg.mouse.get_pos()
    tempstr = '('+ str(ms_pos[0]) + ', ' + str(ms_pos[1]) + ')'
    text(tempstr, 1430 - len(tempstr) * 20, 770, 40, skyblue)

def scroll_grid():
    global gridx, gridy, ms, old_ms
    ms = pg.mouse.get_pos()
    if pg.mouse.get_pressed()[0]:
        gridx += ms[0] - old_ms[0]
        gridy += ms[1] - old_ms[1]
    old_ms = ms

def updategridpos():
    if leveldata.size != 0:
        leveldata[:, 0] = leveldata[:, 6] + gridx
        leveldata[:, 1] = leveldata[:, 7] + gridy

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
    if tool == 'add' and above_player:
        win.blit(red_surf, (gridx + ww//2 - 26, gridy + wh//2 - 199))
    win.blit(player_img, (gridx + ww//2 - 22, gridy + wh//2 - 152))

def q_prompt():
    if count <= 50:
        text("Press 'Q' to toggle menu", ww//2 - 450, wh//2, 70, midnightblue, alpha = 225)
    elif count <= 125:
        text("Press 'Q' to toggle menu", ww//2 - 450, wh//2, 70, midnightblue, alpha = 225 - (count - 50) * 3)
    
def text(txt, x, y, size, colour, alpha = 225):
    t = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), size)
    t2 = t.render(txt, False, colour)
    t2.convert()
    t2.set_alpha(alpha)
    win.blit(t2, (x, y))

def get_tiles():
    global tileset
    tileset = {}
    os.chdir(os.path.dirname(__file__))
    os.chdir(os.path.join(os.getcwd(), 'Tiles'))
    folders = ('green', 'brown', 'cream', 'grey', 'browngrey', 'purple', 'white', 'misc', 'the rest')
    c = 0
    for folder in folders:
        os.chdir(os.path.join(os.getcwd(), folder))
        d = sorted(os.listdir())
        for i in d:
            try:
                temp = pg.image.load(i).convert_alpha()
                tileset[i] = (temp, temp.get_rect()[2], temp.get_rect()[3], c)
            except:
                pass
            c += 1
        os.chdir('..')

def button(w, h, bc, c, ta, disp, id_):
    global buttons, hovering
    ms = list(pg.mouse.get_pos())
    ms[0] += 10
    ms[1] += 10
    if ms[0] > ta[1] and ms[0] < ta[1] + w and ms[1] > ta[2] and ms[1] < ta[2] + h:
        pg.draw.rect(win, greentheme[0], (ta[1] - 15, ta[2] - 15, w + 10, h + 10))
        hovering = id_
    pg.draw.rect(win, bc, (ta[1] - 10, ta[2] - 10, w, h))
    pg.draw.rect(win, c, (ta[1] - 5, ta[2] - 5, w - 10, h - 10))
    text(ta[0], ta[1] + disp[0], ta[2] + disp[1], ta[3], ta[4], ta[5])
    #buttons.append((ta[1], ta[2], w, h))

def imgbutton(s, pos, id_):
    global buttons, hovering, sel_block
    ms = list(pg.mouse.get_pos())
    touching = ms[0] > pos[0] and ms[0] < pos[0] + s[1] and ms[1] > pos[1] and ms[1] < pos[1] + s[2]
    if touching or id_ == sel_block:
        pg.draw.rect(win, greentheme[0], (pos[0] - 10, pos[1] - 10, s[1] + 20, s[2] + 20))
        if touching:
            hovering = id_
    win.blit(s[0], pos)
    #buttons.append((pos[0], pos[1], s[1], s[2]))

def remove_dup():
    global leveldata, tileset
    try:
        ld2 = leveldata.copy()
        '''l2 = ld2[:, 4]
        l2 = np.array(list(map(lambda x: tileset.get(x, (None, None, None, -1))[3], l2)))
        ld2[:, 4] = l2
        ld2 = ld2[:, :5]
        ld2 = ld2.astype(int)
        a, ind = np.unique(ld2, return_index = True, axis = 0)'''
        ld3 = np.apply_along_axis(lambda x: ''.join(list(map(str, x))), axis = 1, arr = ld2)
        a, ind = np.unique(ld3, return_index = True)
        leveldata = leveldata[ind]
    except:
        pass

def clicked_block(clickd):
    global sel_block, sel_block_name, sel_block_coll, sel_block_int, sel_block_move, sel_block_dark
    sel_block = clickd
    sel_block_name = tiles[-sel_block - 1][4]
    if 'HillLeft2' in sel_block_name or 'HillRight2' in sel_block_name:
        sel_block_coll = 1
    elif 'HillLeft' in sel_block_name:
        sel_block_coll = 'tri'
    elif 'HillRight' in sel_block_name:
        sel_block_coll = 'tri2'
    elif 'Half' in sel_block_name or 'bridge' in sel_block_name:
        sel_block_coll = 'up'
    elif 'Lava' in sel_block_name:
        sel_block_coll = 'death'
    elif 'Exit' in sel_block_name:
        sel_block_coll = 'finish'
    else:
        sel_block_coll = 1
    if ('sign' in sel_block_name or 'cloud' in sel_block_name or 'Water' in sel_block_name or 'fence' in sel_block_name or 'hill' in sel_block_name) and not 'Exit' in sel_block_name:
        sel_block_int = False
    else:
        sel_block_int = True
    sel_block_move = None
    sel_block_dark = False

#Returns empty tuple if player is not touching anything, else returns tuple of all
#info of block being touched along with its index in the leveldata list
def touching(x, y, m = 2):
    r = ()
    c = 0
    for i in leveldata:
        moving = 'move' in i[5]
        if not moving and m == 0 or moving and m == 1 or m == 2:
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
    r = ()
    #Rectangular collision applied first
    if x > i[0] and x - i[2] < i[0] and y - i[3] < i[1] and y > i[1]:
        #If rectangle
        if 'coll' not in i[5]:
            r = i
        elif i[5]['coll'] in (0, 'death', 'finish'):
            r = i
        #Elif trinagle
        elif i[5].get('coll') in ('tri', 'tri2'):
            if i[5].get('coll') == 'tri':
                x1 = i[0] + i[2]
                x2 = i[0]
                y1 = i[1]
                y2 = i[1] + i[3]
                xx = x
                yy = y
            elif i[5].get('coll') == 'tri2':
                x1 = i[0]
                x2 = i[0] + i[2]
                y1 = i[1]
                y2 = i[1] + i[3]
                xx = x
                yy = y
            #Apply two-point formula of straight line to obtain hypotenuse of triangle, then treat as an inequality to determine collision
            if yy > ((y2 - y1) / (x2 - x1)) * (xx - x1) + y1:
                r = i
        elif i[5].get('coll') == 'up':
            r = i
    return tuple(r)


ww = int(1600/1.1)
wh = int(900/1.1)

init_game()

get_tiles()
#leveldata = lr.addleveldata(tileset)
#leveldata = np.array([])
#leveldata = np.array(sorted(leveldata, key = lambda x: x[5].get('front', 0)))
#leveldata = np.array(leveldata)
#leveldata = np.append(leveldata, leveldata, axis = 0)
try:
    leveldata = comm.leveldata
except:
    leveldata = np.array([])

gridx = gridy = 0

tool = 'scroll'
mode = 1
hovering = 0
cwlayer = 1
#tiles = [i for i in tileset.values()]
tiles = [tileset[i] + (i,) for i in tileset]
len_tiles = 132
tile_count = 0
snap = True
above_player = False
tempdata = leveldata.copy()

player_img = pg.image.load(os.path.join(os.path.dirname(__file__), 'walk1', 'p1_stand.png')).convert_alpha()
red_surf = pg.Surface((70, 140))
red_surf.fill(red)
red_surf.set_alpha(150)



clicked_block(-1)

run = True
count = 0

#   Modes:
#     +ve: Editor
#     -1: Blank menu
#     -2: Layers
#     -3: Scroll help
#     -4: Add block, block type
#     -5: [Empty]
#     -6: [Empty]
#     -7: Add block, collision
#     -8: Add block, movement
#     -9: Add block, help
#     -10: Delete block, help

# Button IDs:
# -ve: Add block - Block selection 
# 1: Publish level
# 2: Test Level
# 3: Save and Exit
# 4: Scroll
# 5: Add blocks
# 6: Delete blocks
# 7: Layers
# 8: Scroll - Help
# 9: Add block - Block type
# 10: Add block - Next
# 11: Add block - Prev
# 12: Add block - Collision
# 13: Add block - More
# 14: Add block - Help
# 15: Add block - Toggle interactivity
# 16: Add block - Toggle darkness effect
# 17: Add block - Movement - None
# 18: Add block - Movement - Horizontal
# 19: Add block - Movement - Vertical
# 20: Delete block - Help

while run:
    clock.tick(fps)
    keydown = ''
    clicked = 0
    count += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.KEYDOWN:
            keydown = event.key
        elif event.type == pg.MOUSEBUTTONDOWN:
            if hovering:
                clicked = hovering
            else:
                clicked = 500

    if keydown == pg.K_q:
        hovering = 0
        mode = -mode

    if mode >= 1:
        win.fill(white)
        update_mouse_pos()
        updategridpos()
        for i in range(4):
            drawland(i)
        draw_grid()
        q_prompt()
        if tool == 'scroll':
            scroll_grid()
        elif tool == 'add':
            remove_dup()
            xtemp = tiles[-sel_block - 1][1]
            ytemp = tiles[-sel_block - 1][2]
            if snap:
                above_player = ms_pos[0] >= 700 and ms_pos[0] < 700 + xtemp and ms_pos[1] >= -350 and ms_pos[1] < -350 + ytemp + 70
            else:
                above_player = ms_pos[0] >= 700 - xtemp//2 and ms_pos[0] < 700 - xtemp//2 + xtemp + 70 and ms_pos[1] >= -350 - ytemp //2 and ms_pos[1] < -350 - ytemp //2 + ytemp + 140
            if not sel_block_int:
                above_player = False
            if not above_player:
                if keydown in (pg.K_LSHIFT, pg.K_RSHIFT):
                    snap = not snap
                ms_pos_temp = list(ms_pos)
                tempimg = tiles[-sel_block - 1]
                if snap:
                    xtemp = ms_pos_temp[0] % 70
                    ms_pos_temp[0] -= xtemp
                    ms_pos_temp[2] -= xtemp
                    ytemp = ms_pos_temp[1] % 70 - 70
                    ms_pos_temp[1] += ytemp
                    ms_pos_temp[3] += ytemp
                    xtemp, ytemp = ms_pos_temp[2], ms_pos_temp[3]
                else:
                    xtemp, ytemp = ms_pos_temp[2] - tempimg[1] // 2, ms_pos_temp[3] - tempimg[2] // 2
                win.blit(tempimg[0], (xtemp, ytemp))

                if pg.mouse.get_pressed()[0]:
                    leveldata = list(leveldata)
                    d = {}
                    if sel_block_move != None:
                        d['move'] = 'sin'
                        d['sinpower'] = 2
                        d['sinlength'] = 300
                        d['sinvalue'] = 0
                        d['vel'] = 0
                        if sel_block_move == 'h':
                            d['axis'] = 0
                            d['sintemp'] = -gridx + xtemp
                        elif sel_block_move == 'v':
                            d['axis'] = 1
                            d['sintemp'] = -gridy + ytemp
                    if sel_block_int:
                        if sel_block_coll != 1:
                            d['coll'] = sel_block_coll
                    else:
                        d['coll'] = 0
                    if sel_block_dark:
                        d['dark'] = 100
                    d['front'] = cwlayer
                    temp = tiles[-sel_block - 1]
                    leveldata.append(np.array([-gridx + xtemp, -gridy + ytemp, temp[1], temp[2], temp[4], d, -gridx + xtemp, -gridy + ytemp]))
                    leveldata = np.array(leveldata)

        elif tool == 'delete':
            if pg.mouse.get_pressed()[0]:
                t = touching(gridx + ms_pos[0], gridy - ms_pos[1])
                if t:
                    leveldata = np.delete(leveldata, t[8], axis = 0)
            
    else:
        win.fill(browntheme[5])
        #buttons = []
        hovering = 0

        if clicked == 1:
            if lr.get_published(comm.lno) == 'no':
                lr.publish(comm.lno)
            else:
                lr.unpublish(comm.lno)
        elif clicked == 2:
            pg.quit()
            comm.leveldata = leveldata
            import scroller
            del sys.modules['scroller']
            del scroller
            init_game()
        elif clicked == 3:
            lr.export(leveldata, comm.lno)
            tempdata = leveldata.copy()
            

        if clicked == 4:
            tool = 'scroll'
            mode = -1
        elif clicked == 5:
            tool = 'add'
            mode = -1
        elif clicked == 6:
            tool = 'delete'
            mode = -1
        
        text('Options:', 50, 50, 55, browntheme[1])
        if lr.get_published(comm.lno) == 'no':
            button(250, 80, browntheme[0], browntheme[1], ('Publish Level', 300, 50, 32, browntheme[3], 255), (7, 14), 1)
        else:
            button(250, 80, browntheme[0], browntheme[1], ('Unpublish Level', 300, 50, 28, browntheme[3], 255), (5, 16), 1)
        button(250, 80, browntheme[0], browntheme[1], ('Test Level', 600, 50, 40, browntheme[3], 255), (10, 10), 2)
        #button(250, 80, browntheme[0], browntheme[1], ('Export to File', 600, 50, 32, browntheme[3], 255), (5, 14), 2)
        button(250, 80, browntheme[0], browntheme[1], ('Save', 900, 50, 50, browntheme[3], 255), (55, 5), 3)
        
        text('Tools:', 50, 150, 65, browntheme[1])
        button(250, 80, browntheme[0], browntheme[1], ('Scroll', 300, 150, 50, greentheme[2] if tool == 'scroll' else browntheme[3], 255), (40, 5), 4)
        button(250, 80, browntheme[0], browntheme[1], ('Add Blocks', 600, 150, 35, greentheme[2] if tool == 'add' else browntheme[3], 255), (19, 13), 5)
        button(250, 80, browntheme[0], browntheme[1], ('Delete Blocks', 900, 150, 32, greentheme[2] if tool == 'delete' else browntheme[3], 255), (2, 14), 6)

        button(140, 60, browntheme[0], browntheme[1], ('Layers', 50, 750, 35, greentheme[2] if mode == -2 else browntheme[3], 255), (3, 3), 7)
        if tool == 'scroll':
            button(140, 60, browntheme[0], browntheme[1], ('Help', 220, 750, 35, greentheme[2] if mode == -3 else browntheme[3], 255), (23, 3), 8)
        elif tool == 'add':
            button(140, 60, browntheme[0], browntheme[1], ('Block Type', 220, 750, 21, greentheme[2] if mode == -4 else browntheme[3], 255), (3, 10), 9)
            button(140, 60, browntheme[0], browntheme[1], ('Collision', 390, 750, 25, greentheme[2] if mode == -7 else browntheme[3], 255), (8, 8), 12)
            button(140, 60, browntheme[0], browntheme[1], ('More', 560, 750, 35, greentheme[2] if mode == -8 else browntheme[3], 255), (20, 2), 13)
            button(140, 60, browntheme[0], browntheme[1], ('Help', 730, 750, 35, greentheme[2] if mode == -9 else browntheme[3], 255), (23, 3), 14)
        elif tool == 'delete':
            button(140, 60, browntheme[0], browntheme[1], ('Help', 220, 750, 35, greentheme[2] if mode == -9 else browntheme[3], 255), (23, 3), 20)

        if clicked == 7:
            mode = -2
        elif clicked == 8:
            mode = -3
        elif clicked == 9:
            mode = -4
        elif clicked == 12:
            mode = -7
        elif clicked == 13:
            mode = -8
        elif clicked == 14:
            mode = -9
        elif clicked == 20:
            mode = -10
            
        if mode == -1:
            text('Press Q again to return to editor.', 50, 290, 40, browntheme[1])
            text('Or press the red \'x\' to exit. (unsaved work will be lost)', 50, 370, 40, browntheme[1])
            if np.array_equal(tempdata, leveldata):
                text('<< Saved >>', 50, 500, 50, browntheme[0])

        elif mode == -2:
            if keydown == pg.K_RIGHT:
                cwlayer = (cwlayer + 1) % 4
            elif keydown == pg.K_LEFT:
                cwlayer = (cwlayer - 1) % 4
            text('You are working on layer', 50, 290, 65, browntheme[1])
            text(str(cwlayer), 885, 280, 85, greentheme[1])
            text('Order of appearance:', 50, 350, 65, browntheme[1])
            text('Layer 3  ->  Layer 2  ->  Player  ->  Layer 1  ->  Layer 0', 50, 420, 35, browntheme[1])
            text('Use arrow keys to change', 50, 460, 65, browntheme[1])
            
        elif mode == -3:
            text('Click and drag to scroll across the grid.', 50, 290, 65, browntheme[1])
            
        elif mode == -4:
            button(140, 60, browntheme[0], browntheme[1], ('Next', 800, 650, 35, browntheme[3], 255), (23, 3), 10)
            button(140, 60, browntheme[0], browntheme[1], ('Prev.', 500, 650, 35, browntheme[3], 255), (23, 3), 11)
            if clicked == 10:
                tile_count = (tile_count + 1) % (len_tiles // 20 + 1)
            elif clicked == 11:
                tile_count = (tile_count - 1) % (len_tiles // 20 + 1)
            elif clicked < 0:
                clicked_block(clicked)
            xtemp, ytemp = 60, 250
            for i in range(tile_count * 20, tile_count * 20 + 20):
                if i >= len_tiles:
                    break
                imgbutton(tiles[i], (xtemp, ytemp), -i - 1)
                xtemp += 140
                if xtemp >= 1400:
                    xtemp = 60
                    ytemp += 200
                    
        elif mode == -7:
            if sel_block_int:
                if 'Lava' in sel_block_name:
                    text('Hazard: Will cause player to lose game upon collision.', 50, 290, 40, browntheme[1])
                elif 'Exit' in sel_block_name:
                    text('Goal: Level completed upon touching', 50, 290, 40, browntheme[1])
                elif sel_block_coll in (1, 'tri', 'tri2'):
                    text('Normal collision', 50, 290, 40, browntheme[1])
                elif sel_block_coll == 'up':
                    text('Player will not collide with block while coming up from below,', 50, 290, 40, browntheme[1])
                    text('but only while coming down from above.', 50, 350, 40, browntheme[1])
            else:
                text('Non-interactive: Will not collide with player.', 50, 290, 40, browntheme[1])
                if 'Water' in sel_block_name:
                    text('Note: Swimming mechanics not supported.', 50, 350, 40, browntheme[1])
            button(370, 80, browntheme[0], browntheme[1], ('Turn interactivity ' + ('off' if sel_block_int else 'on'), 50, 430, 30, browntheme[3], 255), (10, 14), 15)
            if clicked == 15:
                sel_block_int = not sel_block_int
                
        elif mode == -8:
            text('Darkness effect:', 50, 290, 40, browntheme[1])
            button(140, 60, browntheme[0], browntheme[1], ('On' if sel_block_dark else 'Off', 450, 290, 35, greentheme[2] if sel_block_dark else browntheme[3], 255), (33, 2), 16)
            if clicked == 16:
                sel_block_dark = not sel_block_dark
            text('Movement:', 50, 400, 40, browntheme[1])
            button(200, 60, browntheme[0], browntheme[1], ('None', 50, 500, 35, greentheme[2] if sel_block_move == None else browntheme[3], 255), (45, 2), 17)
            button(200, 60, browntheme[0], browntheme[1], ('Horizontal', 280, 500, 30, greentheme[2] if sel_block_move == 'h' else browntheme[3], 255), (15, 5), 18)
            button(200, 60, browntheme[0], browntheme[1], ('Vertical', 510, 500, 30, greentheme[2] if sel_block_move == 'v' else browntheme[3], 255), (28, 5), 19)
            if clicked == 17:
                sel_block_move = None
            if clicked == 18:
                sel_block_move = 'h'
            if clicked == 19:
                sel_block_move = 'v'
            
        elif mode == -9:
            text('Click to add block.', 50, 290, 60, browntheme[1])
            text('Click and drag to add multiple blocks.', 50, 390, 60, browntheme[1])
            text('Press Shift to toggle \'snap to grid\' effect.', 50, 490, 60, browntheme[1])

        elif mode == -10:
            text('Click to delete block.', 50, 290, 60, browntheme[1])
            text('Click and drag to delete multiple blocks.', 50, 390, 60, browntheme[1])
        
                
            
            
    pg.display.flip()
    #print(touching(gridx + ms_pos[0], gridy - ms_pos[1]))
    
comm.rval = 4
pg.quit()
