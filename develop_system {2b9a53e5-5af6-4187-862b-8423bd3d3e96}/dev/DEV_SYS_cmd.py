import rhinoscript.userinterface
import rhinoscript.geometry
import rhinoscriptsyntax as rs
import sys
import math
import operator
import random
import Rhino
import scriptcontext
import union_Main_link
import diagonal_query_final



def clear_list(li):
    for i in li:
        li.remove(i)
    if(len(li)>0):
        clear_list(li)



def getNames():
    global_copy_distance=0
    x_rules=[]
    num_names=[]
    f=open('ruleset.dat','r')
    while True:
        x=f.readline()
        if not x:
            break
        else:
            try:
                x_name=x.split('>>')[0]
                x_field=x.split('>>')[1]
                x_range_min=x.split('>>')[2].split('-')[0]
                x_range_max=x.split('>>')[2].split('-')[1]            
                x_rules.append([x_name,x_field,x_range_min,x_range_max])
                num_names.append(x_name)
            except:
                pass ####   This would be a comment in the file
    f.close()
    num_names_set=set(num_names)
    num_names=[]
    num_names=num_names_set
    x_rules_x=sorted(x_rules,key=operator.itemgetter(0))
    return num_names



#HERE THE PARCEL_CLASS_LIST IS ACTUALLY A PART OF LARGER DIMENSION LIST FROM PREV FUNCTION

def buildParcelInZone(crv, parcel_list, street_list, avenue_list, obj_name, ite, final_list):
    global_copy_distance=0
    x_rules=[]
    far_req=0
    ht_req=0
    cell_cycle=20
    far_time_cycle=30
    far_inc=5
    img_time=20
    max_time=50
    def_far=1.0
    val_street=0.1
    val_avenue=0.70
    val_default=0.1
    out_scr=1
    out_img=0
    probability_merge=10
    save_crv=3
    attr_bias=100
    attr_rad=250
    f=open('ruleset.dat','r')
    while True:
        x=f.readline()
        if not x:
            break
        else:
            x_name=x.split('>>')[0]
            if(obj_name.lower()==x_name.lower()):
                x_field=x.split('>>')[1]
                x_value=x.split('>>')[2].split('-')[0]
                if(str(x_field).lower()=='far'):
                    far_req=x_value
                if(str(x_field).lower()=='ht'):
                    ht_req=x_value
                if(str(x_field).lower()=='cell_cycle'):
                    cell_cycle=x_value
                if(str(x_field).lower()=='far_time_cycle'):
                    far_time_cycle=x_value
                if(str(x_field).lower()=='far_inc'):
                    far_inc=x_value
                if(str(x_field).lower()=='img_time'):
                    img_time=x_value
                if(str(x_field).lower()=='max_time'):
                    max_time=x_value
                if(str(x_field).lower()=='curr_far'):
                    curr_far=x_value                    
                if(str(x_field).lower()=='val_street'):
                    val_street=x_value
                if(str(x_field).lower()=='val_avenue'):
                    val_avenue=x_value
                if(str(x_field).lower()=='val_default'):
                    val_default=x_value
                if(str(x_field).lower()=='output_screen'):
                    out_scr=x_value
                if(str(x_field).lower()=='output_image'):
                    out_img=x_value
                if(str(x_field).lower()=='probability_merge'):
                    probability_merge=x_value
                if(str(x_field).lower()=='save_crv'):
                    save_crv=x_value
                if(str(x_field).lower()=='attr_bias'):
                    attr_bias=x_value
                if(str(x_field).lower()=='attr_radius'):
                    attr_rad=x_value
    f.close()
    #print(obj_name+";"+str(far_req)+";"+str(ht_req)+";"+str(cell_cycle)+";"+str(far_time_cycle))
    #print(obj_name+";"+str(far_inc)+";"+str(img_time)+";"+str(max_time)+";"+str(curr_far))
    #print(obj_name+";"+str(val_street)+";"+str(val_avenue)+";"+str(val_default)+";"+str(probability_merge))
    try:
        rs.DeleteObjects(zonal_parcel_list)
    except:
        pass
    try:
        rs.DeleteObjects(order_list)
    except:
        pass
    try:
        rs.DeleteObjects(order_list_x)
    except:
        pass
    try:
        clear_list(order_list)
    except:
        pass
    try:
        clear_list(order_list_x)
    except:
        pass
    zonal_parcel_list=[]
    order_list=[]
    if(scriptcontext.escape_test(False)):
        print("USER PRESSED ESCAPE KEY")
    for i in parcel_list:
        try:
            ccen=rs.CurveAreaCentroid(i)[0]
            ptincrv=rs.PointInPlanarClosedCurve(ccen,crv)
            di=rs.Distance(ccen,[0,0,0])
            if(ptincrv==1):
                order_list.append([i,di])
            if(scriptcontext.escape_test(False)):
                print("USER PRESSED ESCAPE KEY")
        except:
            pass
    order_list_x=sorted(order_list,key=operator.itemgetter(1))
    k=0
    for i in order_list_x:
        zonal_parcel_list.append(i[0])
        k+=1
    PARCEL_CLASS_LIST=[]
    temp_list=[]
    PARCEL_CLASS_LIST=union_Main_link.initGrowth(zonal_parcel_list,cell_cycle, far_time_cycle, far_inc, def_far)
    temp_list=union_Main_link.growInTime(PARCEL_CLASS_LIST, cell_cycle, far_time_cycle, far_inc, img_time, max_time, val_avenue, val_street, val_default, out_scr, out_img, probability_merge, save_crv, attr_bias, attr_rad)
    for i in temp_list:
        final_list.append(rs.CopyObjects(i,[0,0,0]))
    try:
        rs.DeleteObjects(temp_list)
    except:
        pass
    try:
        for i in PARCEL_CLASS_LIST:
            i.delOBJECT_B()
        clear_list(PARCEL_CLASS_LIST)
    except:
        pass
    pass

def getEmptySiteData(obj_name):
    global_copy_distance=0
    es_parcel_length=15
    es_parcel_width=50
    es_parcel_length_num=16
    es_parcel_width_num=3
    f=open('ruleset.dat','r')
    while True:
        x=f.readline()
        if not x:
            break
        else:
            x_name=x.split('>>')[0]
            if(obj_name.lower()==x_name.lower()):
                x_field=x.split('>>')[1]
                x_value=x.split('>>')[2].split('-')[0]
                if(str(x_field).lower()=='parcel_length'):
                    es_parcel_length=x_value
                if(str(x_field).lower()=='parcel_width'):
                    es_parcel_width=x_value
                if(str(x_field).lower()=='parcel_length_number'):
                    es_parcel_length_num=x_value
                if(str(x_field).lower()=='parcel_width_number'):
                    es_parcel_width_num=x_value
    f.close()
    arr=[es_parcel_length,es_parcel_width,es_parcel_length_num,es_parcel_width_num]
    return arr


def mainFunction():
    global_copy_distance=0
    num_names=getNames()
    for i in num_names:
        print(i)
        
    rs.EnableRedraw(False)
    empty_site=rs.ObjectsByLayer("_prog_empty_site")
    EMPTY_LIST=[]
    for i in empty_site:
        crv_site=i
        crv_site_cen=rs.CurveAreaCentroid(crv_site)[0]
        crv_site_pts=rs.CurvePoints(crv_site)
        j=0
        for j in num_names:
            x_name='_rule_'+str(j).lower()
            c=rs.ObjectsByLayer(x_name)
            for k in c:
                m=rs.PointInPlanarClosedCurve(crv_site_cen, k)
                if(m==1):
                    arr=getEmptySiteData(j)
                    parcel_length=int(arr[0])
                    parcel_width=int(arr[1])
                    parcel_length_number=int(arr[2])
                    parcel_width_number=int(arr[3])
                    x=diagonal_query_final.mainFunc(crv_site,parcel_length, parcel_width, parcel_length_number, parcel_width_number, global_copy_distance)
                    #x=diagonal_query_final.mainFunc(crv_site)
        rs.CopyObjects(i,[global_copy_distance,0,0])
        EMPTY_LIST.append(i)
    rs.EnableRedraw(True)
    AVENUE_LIST=[]
    STREET_LIST=[]
    PARCEL_LIST=[]

    crv_list=[]
    avenue_list=rs.ObjectsByLayer("_prog_ori_avenue")
    street_list=rs.ObjectsByLayer("_prog_ori_street")
    parcel_list=rs.ObjectsByLayer("_prog_ori_parcel")
    for i in avenue_list:
        #rs.CopyObjects(i,[global_copy_distance,0,0])
        AVENUE_LIST.append(rs.coercecurve(i))
    for i in street_list:
        #rs.CopyObjects(i,[global_copy_distance,0,0])
        STREET_LIST.append(rs.coercecurve(i))
    for i in parcel_list:
        #rs.CopyObjects(i,[global_copy_distance,0,0])
        PARCEL_LIST.append(i)
    for i in num_names:
        x_name='_rule_'+str(i).lower()
        crvs=[]
        if(rs.IsLayer(x_name)):
            crvs=(rs.ObjectsByLayer(x_name))
            K=0
            final_list=[]
            for j in crvs:
                obj_name=x_name.split('_')[2]
                if(PARCEL_LIST is not None):
                    buildParcelInZone(j, PARCEL_LIST, STREET_LIST, AVENUE_LIST, obj_name, K, final_list)
                K+=1
        else:
            pass


##################################################
####        GLOBAL DIMENSION VARIABLES        ####
##################################################




__commandname__ = "DEV_SYS"

def RunCommand( is_interactive ):
    rs.AddLayer("_prog_cell")
    rs.AddLayer("_prog_cell_geo")
    rs.AddLayer("_prog_parcel_3d")
    rs.AddLayer("_prog_merged_parcel")
    rs.AddLayer("_prog_ori_parcel")
    rs.AddLayer("_prog_intermediate_parcel")
    rs.ClearCommandHistory()
    mainFunction()
    return 0

#RunCommand(True)