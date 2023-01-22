import mysql.connector as sq
import numpy as np
from data import *
import random as rd
import pickle as pk
import os, math

def addleveldata(tileset):
    leveldata = []
    def add(x, y, obj, sp = {}):
        nonlocal leveldata
        if obj.isdigit():
            leveldata.append([x, y, sp.get('w', -1), sp.get('h', -1), obj, sp])
        else:
            tempimg = tileset[obj]
            leveldata.append([x, y, tempimg[1], tempimg[2], obj, sp])
    def addrow(x, y, obj, sp, length):
        w = tileset[obj][1]
        for i in range(length):
            add(x + w * i, y, obj, sp)
    def addcol(x, y, obj, sp, length):
        h = tileset[obj][2]
        for i in range(length):
            add(x, y + h * i, obj, sp)
    ###
    add(395, 400, 'grassLedgeLeft.png', {'coll': 0})
    add(1030, 400, 'grassLedgeRight.png', {'coll': 0})
    for i in range(14):
        addrow(400, 400 + i * 70, 'grassCenter.png', {'coll': 0, 'dark': 100}, 9)
    addrow(400, 400, 'grassHalfMid.png', {'coll': 'up', 'front': 1}, 9)
    ###
    add(820, 190, 'grassHillLeft.png', {'coll': 'tri'})
    add(890, 190, 'grassHillLeft2.png', {})
    add(890, 120, 'grassHillLeft.png', {'coll': 'tri'})
    add(960, 120, 'grassHillLeft2.png', {})
    add(960, 50, 'grassHillLeft.png', {'coll': 'tri'})
    add(960, 190, 'grassCenter.png', {})
    add(1030, 50, 'grassMid.png', {})
    add(1030, 120, 'grassCenter.png', {})
    add(1030, 190, 'grassCenter.png', {})
    add(1100, 50, 'grassCliffRight.png', {})
    ###
    addrow(540, 610, 'grassHalfMid.png', {'coll': 'up', 'front': 1}, 10)
    ###
    for i in range(3):
        addcol(1030 + i * 70, 610, 'grassCenter.png', {'coll': 0, 'dark': 100}, 6)
    ###
    add(540, 190, 'grassHillRight.png', {'coll': 'tri2'})
    add(470, 190, 'grassLeft.png', {})
    ###
    add(0, 0, '2', {'txt': "Why, hello there", 'size': 100, 'colour': blue, 'front': 1})
    ###
    add(750, 820, 'grass.png', {'move': 'sin', 'sinpower': 2, 'sinlength': 300, 'sinvalue': 0, 'sintemp': 750, 'vel': 0, 'axis': 0})
    l = np.array(leveldata)
    l = np.append(l, l[:, :2], axis = 1)
    return l


def connect(raw_ = True):
    global con, cur
    con = sq.connect(user = 'root', host = 'localhost', passwd = mysql_password, allow_local_infile = True, db = 'game_server', raw = raw_)
    cur = con.cursor()

def createleveltable_old():
    global con, cur
    cur.execute('create table {} (l_id int, x int, y int, w int, h int, obj varchar(30), sp varchar(200))'.format('levels'))

def createtables():
    global con, cur
    cur.execute('create database if not exists game_server')
    cur.execute('create table if not exists {} (l_no int, l_data longblob)'.format('level_data'))
    cur.execute('create table if not exists {} (id int, level_name varchar(30), creator varchar(30), play_count int, published varchar(3))'.format('game_data'))
    cur.execute('create table if not exists {} (username varchar(30), password varchar(30))'.format('users'))
    
def export(leveldata, lno):
    global con, cur
    connect(True)
    pickled_data = pk.dumps(leveldata)
    cur.execute('delete from level_data where l_no = %s', (lno,))
    cur.execute('insert into level_data values (%s, %s)', (lno, pickled_data))
    con.commit()
    con.close()

def new(lno):
    global con, cur
    connect(True)
    pickled_data = pk.dumps(np.array([]))
    cur.execute('insert into level_data values (%s, %s)', (lno, pickled_data))
    con.commit()
    con.close()

def set_publish(state, lno):
    connect(False)
    cur.execute('update game_data set published = %s where id = %s', (state, lno))
    con.commit()
    con.close()

def importleveldata(lno):
    global con, cur
    connect(True)
    cur.execute('select * from level_data where l_no = {}'.format(lno))
    data = cur.fetchall()
    data = data[0][1]
    data = pk.loads(data)
    data = np.array(data)
    con.close()
    return data
    
def export_old(leveldata, lno):
    global con, cur
    leveldata = np.insert(leveldata, 0, lno, axis = 1)
    os.chdir(os.path.dirname(__file__))
    np.savetxt('data.csv', leveldata, delimiter = ';', fmt = '%s')
    cur.execute('set global local_infile = 1')
    cur.execute('delete from levels where l_id = {}'.format(lno))
    cur.execute('load data local infile "{}" into table {} fields terminated by ";" lines terminated by "\n"'.format(os.path.join(os.getcwd(), 'data.csv'), 'levels'))
    con.commit()
    con.close()
    os.remove('data.csv')
    
def importleveldata_old(lno):
    global con, cur
    if not con.is_connected():
        connect()
    cur.execute('select * from levels where l_id = {}'.format(lno))
    data = cur.fetchall()
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i].pop(0)
        for j in range(4):
            data[i][j] = int(data[i][j])
        data[i][5] = eval(data[i][5])
    data = np.array(data)
    data = np.append(data, data[:, :2], axis = 1)
    return data

def get_published(lno):
    global con, cur
    connect(False)
    cur.execute('select published from game_data where id = %s', (lno,))
    temp = cur.fetchall()
    con.close()
    return temp[0][0]
    
    
def publish(lno):
    global con, cur
    connect(False)
    cur.execute("update game_data set published = 'yes' where id = %s", (lno,))
    con.commit()
    con.close()

def unpublish(lno):
    global con, cur
    connect(False)
    cur.execute("update game_data set published = 'no' where id = %s", (lno,))
    con.commit()
    con.close()


