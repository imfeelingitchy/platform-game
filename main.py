import os, sys, time
import communicator as comm
import mysql.connector as sq
import leveldata_retriever as lr
#import importlib as il

lr.connect()
lr.createtables()

comm.rval = 1
while True:
    if comm.rval == 0:
        break
    if comm.rval == 1:
        comm.rval = 0
        import title
        del sys.modules['title']
        continue
    if comm.rval == 2:
        comm.rval = 0
        import log_in
        del sys.modules['log_in']
        continue
    if comm.rval == 3:
        comm.rval = 0
        import sign_up
        del sys.modules['sign_up']
        continue
    if comm.rval == 4:
        comm.rval = 0
        import dashboard
        del sys.modules['dashboard']
        continue
    if comm.rval == 5:
        comm.rval = 0
        import level_editor
        del sys.modules['level_editor']
        continue
    if comm.rval == 6:
        comm.rval = 0
        import scroller
        del sys.modules['scroller']
        continue

'''comm.rval = 1
while True:
    if comm.rval == 0:
        break
    if comm.rval == 1:
        comm.rval = 0
        try:
            il.reload(title)
        except:
            import title
            del sys.modules['title']
        continue
    if comm.rval == 2:
        comm.rval = 0
        try:
            il.reload(log_in)
        except:
            import log_in
            del sys.modules['log_in']
        continue
    if comm.rval == 3:
        comm.rval = 0
        try:
            il.reload(sign_up)
        except:
            import sign_up
            del sys.modules['sign_up']
        continue
    if comm.rval == 4:
        comm.rval = 0
        try:
            il.reload(dashboard)
        except:
            import dashboard
            del sys.modules['dashboard']
        continue
    if comm.rval == 5:
        comm.rval = 0
        try:
            il.reload(level_editor)
        except:
            import level_editor
            del sys.modules['level_editor']
        continue
    if comm.rval == 6:
        comm.rval = 0
        try:
            il.reload(scroller)
        except:
            import scroller
            del sys.modules['scroller']
        continue'''
'''def wipe_memory():
    for name in dir():
        if not (name.startswith('_') or name == 'wipe_memory'):
            del globals()[name]

comm.rval = 1
while True:
    os.chdir(os.path.dirname(__file__))
    if comm.rval == 0:
        break
    if comm.rval == 1:
        comm.rval = 0
        exec(open('title.py', 'r').read())
        wipe_memory()
        continue
    if comm.rval == 2:
        comm.rval = 0
        exec(open('log_in.py', 'r').read())
        wipe_memory()
        continue
    if comm.rval == 3:
        comm.rval = 0
        exec(open('sign_up.py', 'r').read())
        wipe_memory()
        continue
    if comm.rval == 4:
        comm.rval = 0
        exec(open('dashboard.py', 'r').read())
        wipe_memory()
        continue
    if comm.rval == 5:
        comm.rval = 0
        exec(open('level_editor.py', 'r').read())
        wipe_memory()
        continue
    if comm.rval == 6:
        comm.rval = 0
        exec(open('scroller.py', 'r').read())
        wipe_memory()
        continue'''

