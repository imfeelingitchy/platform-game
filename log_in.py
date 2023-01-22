import os, math
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
import communicator as comm
import mysql.connector as sq
from data import *

def entry(pos, id_, maxlen = 20, type_ = 1):
    #Types:
    # 1 - alphanumeric
    # 2 - all
    # 3 - numbers
    # string - alphanumeric plus characters specified in string
    global text, clicked, keydown, inp_font
    text_surf = inp_font.render(text[id_][1], True, grey)
    inp_rect = pg.Rect(pos[0], pos[1], 200, 50)
    inp_rect.w = max(200, text_surf.get_width() + 20)
    ms = pg.mouse.get_pos()
    if clicked:
        active = inp_rect.collidepoint(ms)
        text[id_][0] = active
    active = text[id_][0]
    if active:
        if keydown == 'back':
            text[id_][1] = text[id_][1][:-1]
        elif keydown != None:
            if (type_ == 1 and keydown.isalnum()) or (type_ == 2 and keydown.isprintable()) or (type_ == 3 and keydown.isdigit()) or (type(type_) == str and (keydown.isalnum() or keydown in type_)):
                if len(text[id_][1]) != maxlen:
                    text[id_][1] += keydown
    win.blit(text_surf, (pos[0] + 10, pos[1] + 4))
    pg.draw.rect(win, browntheme[1] if active else browntheme[2], inp_rect, 5 if active else 3)

def draw_text(txt, x, y, size, colour, alpha = 225):
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
    draw_text(ta[0], ta[1] + disp[0], ta[2] + disp[1], ta[3], ta[4], ta[5])

def connect():
    global con, cur
    con = sq.connect(user = 'root', host = 'localhost', passwd = mysql_password, db = 'game_server')
    cur = con.cursor()

connect()  

ww = 1200
wh = 675
pg.init()
pg.font.init()
pg.mixer.init()
win = pg.display.set_mode((ww, wh))
pg.display.set_caption(name_log_in)
clock = pg.time.Clock()
os.chdir(os.path.dirname(__file__))

inp_font = pg.font.Font(os.path.join(os.path.dirname(__file__), 'fonts', 'times-new-roman.ttf'), 35)
err_sound = pg.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'error.wav'))

text = [[0, ''] for i in range(2)]
run = True
fc = -1
hovering = 0
invalid = 0

while run:
    clock.tick(fps)

    fc += 1
    keydown = None
    clicked = False
    button_clicked = 0

    win.fill(greentheme[5])
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                keydown = 'back'
            elif event.key == pg.K_RETURN:
                for i in range(len(text)):
                    text[i][0] = 0
            else:
                keydown = event.unicode
        elif event.type == pg.MOUSEBUTTONDOWN:
            clicked = True
            if hovering:
                button_clicked = hovering

    hovering = 0

    draw_text('Log In', 40, 40 + math.sin(fc / 20) * 10, 100, greentheme[1])
    draw_text('Username:', 40, 250, 50, greentheme[1])
    draw_text('Password:', 40, 330, 50, greentheme[1])
    entry((320, 250), 0, type_ = '_-')
    entry((320, 330), 1, type_ = 2)
    button(250, 80, browntheme[0], browntheme[1], ('Submit', 45, 450, 50, browntheme[3], 255), (28, 7), 1)
    button(250, 80, browntheme[0], browntheme[1], ('Back', 345, 450, 50, browntheme[3], 255), (55, 7), 2)
    if invalid:
        draw_text('Username and password do not match.', 40, 550, 50, redtheme[1])

    if button_clicked == 2:
        comm.rval = 1
        run = False

    elif button_clicked == 1:
        cur.execute('select * from users')
        temp = cur.fetchall()
        if (text[0][1], text[1][1]) in temp:
            comm.rval = 4
            comm.uname = text[0][1]
            run = False
        else:
            invalid = 1
            pg.mixer.Sound.play(err_sound)
            text[1][1] = ''
        

    pg.display.flip()

pg.quit()
