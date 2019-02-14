import time
"""from xlrd import open_workbook

book = open_workbook("testdata_xlsx")
sheet = book.sheet_by_index(0)"""

kt = [1.21,2.41]
kv = [1,0]
pt = [1.1, 2.1]
pv = [2,0]

k_on = 1
p_on = 2

"""for row in range(2, yourlastrow):
    pt.append(sheet.cell(row,0))
    pv.append(sheet.cell(row,1))
    kt.append(sheet.cell(row,2))
    kv.append(sheet.cell(row,3))

print(pt)"""

K = 0    #0 or 1            #pressure sensor
P = 0     #0 or 1 or 2      #pedal

kvidx = [i for i , x in enumerate(kv) if x == 1]
pvidx = [i for i , x in enumerate(pv) if x == 2]

ktlist = [kt[i] for i in kvidx]
ptlist = [pt[i] for i in pvidx]
print(kvidx)
print(pvidx)
print(ktlist)
print(ptlist)

print(len(ktlist))
td = 0
for i in range(len(ktlist)):
    min = 1 #must be greater than 0.5 (threshold)
    for j in range(len(ptlist)):
        if abs(ktlist[i] - ptlist[j]) < min:
            min = abs(ktlist[i] - ptlist[j])
            print("min : "+ str(min))
        else: #(ktlist[i] - ptlist[j]) > min:
            td = abs(ktlist[i] - ptlist[j-1])
            break



"""

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
        time.sleep(0.5)
        if K == 1:
            DIRECT_STATE = 3
        else:
            DIRECT_STATE = 1
    if DIRECT_STATE == 2:
        time.sleep(0.5)
        if P == 2:
            DIRECT_STATE = 3
        else:
            DIRECT_STATE = 1
    if DIRECT_STATE == 3:
        direct = True
        DIRECT_STATE = 0

while True: #legato
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
"""
