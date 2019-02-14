##kt = [1.21, 2.41, 3.6, 5, 6.1, 8.2]
##kv = [1, 0, 1, 0, 1, 0]
##pt = [1.1, 2.1, 4, 4.01, 5.1, 6.2, 8]
##pv = [2, 0, 1, 2, 0, 1, 0]
                
def direct(kt, kv, pt, pv):
        kvidx_on = [i for i , x in enumerate(kv) if x == 1]
        pvidx_on = [i for i , x in enumerate(pv) if x == 2]

        kvidx_off = [i for i , x in enumerate(kv) if x == 0]
        pvidx_off = [i for i , x in enumerate(pv) if x == 0]

        ktlist_on = [kt[i] for i in kvidx_on]
        ptlist_on = [pt[i] for i in pvidx_on]

        ktlist_off = [kt[i] for i in kvidx_off]
        ptlist_off = [pt[i] for i in pvidx_off]


        print("ktlist_on = " + str(ktlist_on))
        print("ptlist_on = " + str(ptlist_on))


        print("ktlist_off = " + str(ktlist_off))
        print("ptlist_off = " + str(ptlist_off))

        td = 0
        direct_list = []
        start_time = 0
        end_time = 0
        BOTH_ON = False
        DIRECT = False
        start_list = []
        end_list = []

        for i in range(len(ktlist_on)):
                check = 1 #must be greater than 0.5 (threshold)
                for j in range(len(ptlist_on)):
                        print("ktlist_on[i] = " + str(ktlist_on[i]))
                        print("ptlist_on[j] = " + str(ptlist_on[j]))
                        if abs(ktlist_on[i] - ptlist_on[j]) < check:
                                check = abs(ktlist_on[i] - ptlist_on[j])
                                print("check : "+ str(check))
                        else: #(ktlist[i] - ptlist[j]) > check:
                                td = abs(ktlist_on[i] - ptlist_on[j-1])
                                print("td = " + str(td))
                                if td < 0.5:
                                        start_time = min(ktlist_on[i], ptlist_on[j-1])
                                        start_list.append(start_time)
                                        BOTH_ON = True

        if BOTH_ON == True:
                for i in range(len(ktlist_off)):
                        check = 1 #must be greater than 0.5 (threshold)
                        for j in range(len(ptlist_off)):
                                print("ktlist_off[i] = " + str(ktlist_off[i]))
                                print("ptlist_off[j] = " + str(ptlist_off[j]))
                                if abs(ktlist_off[i] - ptlist_off[j]) < check:
                                        check = abs(ktlist_off[i] - ptlist_off[j])
                                        print("check : "+ str(check))
                                else: #(ktlist[i] - ptlist[j]) > check:
                                        td = abs(ktlist_off[i] - ptlist_off[j-1])
                                        print("td = " + str(td))
                                        if td < 0.5:
                                                end_time = max(ktlist_off[i], ptlist_off[j-1])
                                                end_list.append(end_time)
                                                DIRECT = True

        print("start_list = " + str(start_list))
        print("end_list = " + str(end_list))
        if DIRECT == True:
                for i in range(min(len(start_list), len(end_list))):
                        direct_list.append({'start':start_list[i],'end':end_list[i]})

        print("final direct_list = " + str(direct_list))
        return direct_list
