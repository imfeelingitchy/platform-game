import os, math, random, sys, time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import numpy as np
import communicator as comm
import leveldata_retriever as lr
import mysql.connector as sq
from data import *

def init_game():
    global win, clock, data2, data3, data4, data2_, data3_, data4_
    pg.init()
    pg.font.init()
    pg.mixer.init()
    win = pg.display.set_mode((ww, wh))
    pg.display.set_caption(name_log_in)
    clock = pg.time.Clock()
    os.chdir(os.path.dirname(__file__))
    cur.execute("select * from game_data where published = 'yes'")
    data2 = cur.fetchall()
    data2 = np.array(data2)
    try:
        data2 = data2[:, :4]
    except:
        pass
    data2 = list(map(tuple, data2))
    cur.execute('select * from game_data where creator = %s', (comm.uname,))
    data2_ = cur.fetchall()
    data2.insert(0, ('ID', 'Level Name', 'Creator', 'Play Count'))
    data2_.insert(0, ('ID', 'Level Name', 'Creator', 'Play Count', 'Published?'))
    data3 = []
    data4 = []
    data3_ = []
    data4_ = []
    c = 0
    while c < len(data2) - 1:
        if c % 20 == 0:
            data3.append([])
            data3[-1].append(data2[0])
        data3[-1].append(data2[c + 1])
        data4.append(str(data2[c + 1][0]))
        c += 1
    c = 0
    while c < len(data2_) - 1:
        if c % 20 == 0:
            data3_.append([])
            data3_[-1].append(data2_[0])
        data3_[-1].append(data2_[c + 1])
        data4_.append(str(data2_[c + 1][0]))
        c += 1

def text(txt, x, y, size, colour, alpha = 225):
    t = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'pixel.ttf'), size)
    t2 = t.render(txt, True, colour)
    t2.convert()
    t2.set_alpha(alpha)
    win.blit(t2, (x, y))

def button(w, h, bc, c, ta, disp, id_):
    global hovering
    ms = list(pg.mouse.get_pos())
    ms[0] += 10
    ms[1] += 10
    if ms[0] > ta[1] and ms[0] < ta[1] + w and ms[1] > ta[2] and ms[1] < ta[2] + h:
        pg.draw.rect(win, greentheme[0], (ta[1] - 15, ta[2] - 15, w + 10, h + 10))
        hovering = id_
    pg.draw.rect(win, bc, (ta[1] - 10, ta[2] - 10, w, h))
    pg.draw.rect(win, c, (ta[1] - 5, ta[2] - 5, w - 10, h - 10))
    text(ta[0], ta[1] + disp[0], ta[2] + disp[1], ta[3], ta[4], ta[5])

def connect(raw_ = True):
    global con, cur
    con = sq.connect(user = 'root', host = 'localhost', passwd = mysql_password, db = 'game_server', raw = raw_)
    cur = con.cursor()

def draw(tbl, x, y, size):
    def typeline(w):
        tempstr = ''
        for i in range(len(w)):
            tempstr = tempstr + '+' + '-' * (w[i] + 2)
        tempstr += '+'
        return tempstr
    def typerow(l):
        tempstr = ''
        for i in range(len(l)):
            tempstr = tempstr + '| ' + (('%' + str(w[i]) + 's')%l[i]) + ' '
        tempstr += '|'
        return tempstr
    tbl_font = pg.font.Font(os.path.join(os.getcwd(), 'fonts', 'courier_new.ttf'), size)
    w = []
    for i in range(len(tbl[0])):
        templst = [len(str(tbl[j][i])) for j in range(len(tbl))]
        w.append(max(templst))
    line = tbl_font.render(typeline(w), True, grey)
    for i in range(len(tbl)):
        #drawline(w, i)
        win.blit(line, (x, y + i * size * 2))
        tempsurf = tbl_font.render(typerow(tbl[i]), True, grey)
        win.blit(tempsurf, (x, y + i * size * 2 + size))
    win.blit(line, (x, y + len(tbl) * size * 2))

def entry(pos, id_, maxlen = 20, type_ = 1):
    #Types:
    # 1 - alphanumeric
    # 2 - all
    # 3 - numbers
    # string - alphanumeric plus characters specified in string
    global textholder, clicked, keydown, inp_font
    text_surf = inp_font.render(textholder[id_][1], True, grey)
    inp_rect = pg.Rect(pos[0], pos[1], 200, 50)
    inp_rect.w = max(200, text_surf.get_width() + 20)
    ms = pg.mouse.get_pos()
    if clicked:
        active = inp_rect.collidepoint(ms)
        textholder[id_][0] = active
    active = textholder[id_][0]
    if active:
        if keydown == 'back':
            textholder[id_][1] = textholder[id_][1][:-1]
        elif keydown != None:
            if (type_ == 1 and keydown.isalnum()) or (type_ == 2 and keydown.isprintable()) or (type_ == 3 and keydown.isdigit()) or (type(type_) == str and (keydown.isalnum() or keydown in type_)):
                if len(textholder[id_][1]) != maxlen:
                    textholder[id_][1] += keydown
    win.blit(text_surf, (pos[0] + 10, pos[1] + 4))
    pg.draw.rect(win, browntheme[1] if active else browntheme[2], inp_rect, 5 if active else 3)

connect(False)

ww = 1600
wh = 900
init_game()

run = True
mode = 1
invalid = 0
grid_count = grid_count2 = 0
textholder = [[0, ''] for i in range(3)]

inp_font = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'times-new-roman.ttf'), 35)
err_sound = pg.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'error.wav'))

cur.execute('select * from game_data where creator = %s', (comm.uname,))
allow_edit = cur.fetchone()
allow_edit = allow_edit != None
try:
    cur.fetchall()
except:
    pass
#allow_edit = True

while run:
    clock.tick(fps)

    button_clicked = 0
    clicked = False
    keydown = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            clicked = True
            if hovering:
                button_clicked = hovering
                invalid = 0
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                keydown = 'back'
            elif event.key == pg.K_RETURN:
                for i in range(len(textholder)):
                    textholder[i][0] = 0
            else:
                keydown = event.unicode

    hovering = 0

    win.fill(greentheme[5])

    if mode == 1:
        text('Welcome, ' + comm.uname, 40, 30, 70, greentheme[1])
        button(250, 120, browntheme[0], browntheme[1], ('Play', 50, 200, 80, browntheme[3], 255), (28, 10), 1)
        button(290, 70, browntheme[0], browntheme[1], ('Create Level', 50, 350, 40, browntheme[3], 255), (5, 5), 2)
        button(290, 70, browntheme[0], browntheme[1], ('Edit Level', 50, 440, 40, browntheme[3], 255), (35, 5), 3)

        if button_clicked == 1:
            c = 1
            mode = 2
        elif button_clicked == 2:
            mode = 4
        elif button_clicked == 3:
            if allow_edit:
                c = 1
                mode = 5
            else:
                invalid = 1
                pg.mixer.Sound.play(err_sound)

        if invalid:
            text('You need to create a level first.', 40, 550, 50, redtheme[1])

    elif mode == 2 or mode == 5:
        c += 1
        if mode == 2:
            draw(data3[grid_count], 30, 10, c)
        else:
            draw(data3_[grid_count], 30, 10, c)
        if c == 19:
            mode += 1

    elif mode == 3:
        draw(data3[grid_count], 30, 10, 19)
        button(150, 60, browntheme[0], browntheme[1], ('Prev', 150, 840, 40, browntheme[3], 255), (15, 0), 6)
        button(150, 60, browntheme[0], browntheme[1], ('Next', 350, 840, 40, browntheme[3], 255), (15, 0), 7)
        text('Enter level ID corresponding to', 900, 60, 40, greentheme[1])
        text('that which you want to play:', 900, 140, 40, greentheme[1])
        button(250, 120, browntheme[0], browntheme[1], ('Play', 920, 320, 80, browntheme[3], 255), (28, 10), 8)
        button(250, 80, browntheme[0], browntheme[1], ('Back', 910, 800, 50, browntheme[3], 255), (60, 5), 9)
        entry((910, 220), 1, type_ = 3)
        if invalid:
           text('Please enter a valid level ID.', 900, 550, 40, redtheme[1]) 

        if button_clicked == 6:
            grid_count = (grid_count - 1) % len(data3)
        elif button_clicked == 7:
            grid_count = (grid_count + 1) % len(data3)
        elif button_clicked == 8:
            if textholder[1][1] not in data4:
                invalid = 1
                pg.mixer.Sound.play(err_sound)
                textholder[1][1] = ''
            else:
                #pg.quit()
                lr.connect()
                comm.lno = int(textholder[1][1])
                comm.leveldata = lr.importleveldata(comm.lno)
                comm.rval = 6
                run = False
                cur.execute("update game_data set play_count = play_count + 1 where id = %s", (comm.lno,))
                con.commit()
                '''import scroller
                del sys.modules['scroller']
                init_game()'''
        elif button_clicked == 9:
            mode = 1

    elif mode == 4:
        text('Enter level name:', 40, 30, 50, greentheme[1])
        entry((40, 120), 0, type_ = 2)
        button(250, 80, browntheme[0], browntheme[1], ('Continue', 45, 220, 50, browntheme[3], 255), (10, 5), 4)
        button(250, 80, browntheme[0], browntheme[1], ('Back', 350, 220, 50, browntheme[3], 255), (60, 5), 5)

        if button_clicked == 4:
            invalid = not bool(textholder[0][1])
            if not invalid:
                comm.rval = 5
                comm.lname = textholder[0][1]
                cur.execute('select * from game_data')
                templist = cur.fetchall()
                comm.lno = len(templist) + 1
                cur.execute("insert into game_data values (%s, %s, %s, 0, 'no')", (comm.lno, comm.lname, comm.uname))
                con.commit()
                comm.leveldata = np.array([])
                lr.export(comm.leveldata, comm.lno)
                comm.rval = 5
                run = False
                '''pg.quit()
                import level_editor
                del sys.modules['level_editor']
                init_game()
                mode = 1'''
            else:
                pg.mixer.Sound.play(err_sound)

        if invalid:
            text('Please enter a valid level name.', 40, 300, 50, redtheme[1])
            
        elif button_clicked == 5:
            mode = 1

    elif mode == 6:
        draw(data3_[grid_count2], 30, 10, 19)
        button(150, 60, browntheme[0], browntheme[1], ('Prev', 150, 840, 40, browntheme[3], 255), (15, 0), 10)
        button(150, 60, browntheme[0], browntheme[1], ('Next', 350, 840, 40, browntheme[3], 255), (15, 0), 11)
        text('Enter level ID corresponding to', 900, 60, 40, greentheme[1])
        text('that which you want to edit:', 900, 140, 40, greentheme[1])
        button(250, 120, browntheme[0], browntheme[1], ('Edit', 920, 320, 80, browntheme[3], 255), (28, 10), 12)
        button(250, 80, browntheme[0], browntheme[1], ('Back', 910, 800, 50, browntheme[3], 255), (60, 5), 13)
        entry((910, 220), 2, type_ = 3)
        if invalid:
           text('Please enter a valid level ID.', 900, 550, 40, redtheme[1]) 

        if button_clicked == 10:
            grid_count2 = (grid_count2 - 1) % len(data3)
        elif button_clicked == 11:
            grid_count2 = (grid_count2 + 1) % len(data3)
        elif button_clicked == 12:
            if textholder[2][1] not in data4_:
                invalid = 1
                pg.mixer.Sound.play(err_sound)
                textholder[2][1] = ''
            else:
                #pg.quit()
                lr.connect()
                comm.lno = int(textholder[2][1])
                comm.leveldata = lr.importleveldata(comm.lno)
                comm.rval = 5
                run = False
                '''import level_editor
                del sys.modules['level_editor']
                init_game()'''
        elif button_clicked == 13:
            mode = 1


    pg.display.flip()

pg.quit()
