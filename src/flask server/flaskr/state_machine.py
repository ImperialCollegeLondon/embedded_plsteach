
K = 0    #0 or 1
P = 0     #0 or 1 or 2

direct = False
legato = False

DIRECT_STATE = 0
LEGATO_STATE = 0
while True: # direct_state
    if DIRECT_STATE == 0:
        if P == 2:
            DIRECT_STATE = 1
        else if K == 1
            DIRECT_STATE = 2
    if DIRECT_STATE == 1:
        t = 0.5
        if K == 1:
            DIRECT_STATE = 3
        else:
            DIRECT_STATE = 1
    if DIRECT_STATE == 2:
        if P == 2:
            DIRECT_STATE = 3
        else:
            DIRECT_STATE = 1
    if DIRECT_STATE == 3:
        direct = True
        DIRECT_STATE = 0

while True:
    if LEGATO_STATE = 0:
        if K == 1:
            LEGATO_STATE = 1
    if LEGATO_STATE = 1:
        if K == 0:
            LEGATO_STATE = 0
        else if P == 1:
            LEGATO_STATE = 2
    if LEGATO_STATE = 2:
        if P == 0:
            LEGATO_STATE = 0
        else if K == 0:
            legato == True
            LEGATO_STATE = 0
