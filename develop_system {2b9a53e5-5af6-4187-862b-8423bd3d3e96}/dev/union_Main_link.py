import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import math
import operator
import random
import Nirvik_UI_Utility
import time

from parcel_class_file_rev import Parcel_class
from cell_class_file_rev import Cell_class

rs.ClearCommandHistory()

#def getObjectsFromDrawing(sender, e):
def getObjectsFromDrawing():
    crv_list=[]
    avenue_list=rs.ObjectsByLayer("_prog_ori_avenue")
    street_list=rs.ObjectsByLayer("_prog_ori_street")
    parcel_list=rs.ObjectsByLayer("_prog_ori_parcel")
    for i in avenue_list:
        AVENUE_LIST.append(rs.coercecurve(i))
    for i in street_list:
        STREET_LIST.append(rs.coercecurve(i))
    for i in parcel_list:
        PARCEL_LIST.append(i)
    initGrowth()

def initGrowth(li,cell_cycle_, far_time_cycle_, far_inc_, def_far_):
    print("initialize growth...")
    ####    CONSTRUCT PARCELS  ####
    rs.EnableRedraw(False)
    PARCEL_LIST=li
    CELL_CYCLE=cell_cycle_
    FAR_TIME_CYCLE=far_time_cycle_
    FAR_INC=far_inc_
    DEF_FAR=def_far_
    k=0
    for i in PARCEL_LIST:
        try:
            crv_pts=rs.CurvePoints(i)
            x0=crv_pts[0][0]
            y0=crv_pts[0][1]
            bb=rs.BoundingBox(i)
            ax=rs.Distance(bb[0],bb[1])
            by=rs.Distance(bb[1],bb[2])
            PARCEL_CLASS_LIST.append(Parcel_class(x0, y0, ax, by, CELL_CYCLE, FAR_TIME_CYCLE, FAR_INC,i,DEF_FAR)) ######### PARCEL CLASS INIT
        except:
            rs.DeleteObject(i)
            rs.DeleteObject(PARCEL_LIST[k])
        k+=1
    rs.EnableRedraw(True)
    #growInTime()
    return PARCEL_CLASS_LIST
    pass
#PARCEL_CLASS_LIST, cell_cycle, far_time_cycle, far_inc, img_time, max_time, val_avenue, val_street, val_default, out_scr, out_img, probability_merge, save_crv, attr_bias, attr_rad
def growInTime(PARCEL_CLASS_LIST, cell_cycle_, far_time_cycle_, far_inc_, img_time_, max_time_, val_avenue_, val_street_, val_def_, out_scr_, out_img_, probability_merge_, save_crv_, attr_bias_, attr_rad_):
    rs.EnableRedraw(False)
    CELL_CYCLE=int(cell_cycle_)
    FAR_TIME_CYCLE=int(far_time_cycle_)
    FAR_INC=float(far_inc_)
    IMG_TIME=int(img_time_)
    MAX_TIME=int(max_time_)
    VAL_AVENUE=float(val_avenue_)
    VAL_STREET=float(val_street_)
    VAL_DEFAULT=float(val_def_)
    OUT_IMG_YES=int(out_img_)
    IMG_TIME=int(img_time_)
    OUTPUT_SCREEN=int(out_scr_)
    PROBABILITY_MERGE=int(probability_merge_)
    SAVE_CRV=int(save_crv_)
    ATTR_BIAS=float(attr_bias_)
    ATTR_RAD=float(attr_rad_)
    print(str(ATTR_BIAS)+" - "+str(ATTR_RAD))
    #### GET ATTRACTOR CURVES
    attr_pts=[]
    attr_crvs=rs.ObjectsByLayer("_prog_attr_crv")
    try:
        for i in attr_crvs:
            p=rs.AddPoint(rs.CurveAreaCentroid(i)[0])
            attr_pts.append(p)
    except:
        pass
    #### GLOBAL  MAXIMUM FAR
    global_far_i=1
    for i in range(1,MAX_TIME,1):
        global_far_i*=(1+(FAR_INC/100))
    GLOBAL_MAX_FAR=global_far_i*(len(PARCEL_CLASS_LIST))
    print("max far="+str(GLOBAL_MAX_FAR))
    print("developing the system in time...")    
    for i in PARCEL_CLASS_LIST:
        i.buildCells()
        i.initCellVal(STREET_LIST, VAL_STREET, AVENUE_LIST, VAL_AVENUE, VAL_DEFAULT)
        i.mapValCellToParcel()
        pass
    LOCAL_FAR=1.0
    for i in range(0,int(MAX_TIME),1):
        LOCAL_FAR*=((1+(FAR_INC/100)))
        #print(str(LOCAL_FAR)+" ; "+str(i))
        print("SYSTEM TIME  : "+ str(i)+" / "+str(MAX_TIME))
        if(scriptcontext.escape_test(False)):
            print("USER PRESSED ESCAPE KEY")
            break
        #if((i%IMG_TIME==0) and ui_OUT_IMG_YES.Checked==True):
        if((i%IMG_TIME==0 or i==int(MAX_TIME)) and OUT_IMG_YES==1):
            showAndExportImage()
            pass
        #if (ui_RENDER_YES.Checked==True):
        if((OUTPUT_SCREEN==1)):
            rs.Redraw()
        k=0
        for j in PARCEL_CLASS_LIST: 
            if(k<len(PARCEL_CLASS_LIST)-1):
                A=PARCEL_CLASS_LIST[k]
                B=PARCEL_CLASS_LIST[k+1]
                n=random.randrange(1,100)
                if(n<PROBABILITY_MERGE):
                    try:
                        #print("trying to merge...")
                        x=A.mergeParcel(B)
                        #print("merge try result : "+str(x))
                        if(x==1):
                            A.completePARCEL()
                            A.delOBJECT_A()
                            AB_crv=rs.CurveBooleanUnion([A.MAIN_ROOT, B.MAIN_ROOT])[0]
                            rs.ObjectLayer(AB_crv,"_prog_merged_parcel")
                            rs.DeleteObjects([A.MAIN_ROOT,B.MAIN_ROOT])
                            A.constructRoot(AB_crv)
                            A.buildCells()
                            A.initCellVal(STREET_LIST, VAL_STREET, AVENUE_LIST, VAL_AVENUE, VAL_DEFAULT)
                            sum_attr=LOCAL_FAR
                            try:
                                for k_attr in attr_pts:
                                    if(rs.IsPoint(k_attr)):
                                        attr_dis=rs.Distance(k_attr,rs.CurveAreaCentroid(A.MAIN_ROOT)[0])
                                        if(attr_dis<ATTR_RAD):
                                            #print("ok")
                                            sum_attr+=(LOCAL_FAR*ATTR_BIAS/attr_dis)
                            except:
                                sum_attr=LOCAL_FAR
                            for t in range(i):
                                A.update(t,FAR_TIME_CYCLE, FAR_INC, sum_attr) ######### UPDATE MERGER TO CURRENT VALUE
                            A.mapValCellToParcel()
                            B.completePARCEL()
                            B.delOBJECT_B()
                            del(PARCEL_CLASS_LIST[k+1])
                            #print("merge complete")
                        else:
                            #print("not Compatible")
                            pass
                    except:
                        pass
                else:
                    #print("Probability too LOW")
                    pass
            else:
                #print("end of list")
                pass
            sum_attr1=LOCAL_FAR
            try:
                for k_attr1 in attr_pts:
                    if(rs.IsPoint(k_attr)):
                        ccenX=rs.CurveAreaCentroid(PARCEL_CLASS_LIST[k].MAIN_ROOT)[0]
                        attr_dis=rs.Distance(k_attr1,ccenX)
                        if(attr_dis<ATTR_RAD):
                            sum_attr1+=(LOCAL_FAR*ATTR_BIAS/attr_dis)
            except:
                sum_attr1=LOCAL_FAR
            PARCEL_CLASS_LIST[k].update(i,FAR_TIME_CYCLE, FAR_INC, sum_attr1)  ######### UPDATE PARCEL CLASS
            export_crv_time=int(MAX_TIME/(SAVE_CRV))
            if(i%SAVE_CRV==0):
                try:
                    save_crv_copy=rs.CopyObject(PARCEL_CLASS_LIST[k].MAIN_ROOT,[0,0,PARCEL_CLASS_LIST[k].HEIGHT])
                    rs.ObjectLayer(save_crv_copy,"_prog_intermediate_parcel")
                except:
                    pass
            k+=1
        pass
    FIND_FAR_REACHED=0
    for i in PARCEL_CLASS_LIST:
        try:
            i.completePARCEL()
        except:
            pass
        FIND_FAR_REACHED+=i.CURR_FAR
    print("DEVELOPMENT IS COMPLETE")
    ret_list=[]
    for i in PARCEL_CLASS_LIST:
        try:
            ret_list.append(i.ext_srf)
        except:
            pass
        pass
    rs.EnableRedraw(True)
    k=0
    for i in PARCEL_CLASS_LIST:
        #print(str(k)+" - "+str(i.CURR_FAR))
        k+=1
    return ret_list

def showAndExportImage():    
    rs.Redraw()                
    K=ms=time.time()
    string_img=str("test"+str(K)+".jpg")
    img=rs.CreatePreviewImage(string_img)
    print("img created")



AVENUE_LIST=[]
STREET_LIST=[]
HOR_PARCEL_LIST=[]
VER_PARCEL_LIST=[]
PARCEL_LIST=[]
PARCEL_CLASS_LIST=[]
COLOR_LIST=[]
CELL_LIST=[]
CELL_FAR_LIST=[]
BLOCK_LIST=[]


render_background_color=1
rs.RenderColor(render_background_color, (255,255,255))
CELL_LENGTH=6
CELL_WIDTH=6
FLOOR_HT=1.0
CURR_TIME=0
CURR_FAR=1

##################################################
####        GLOBAL DIMENSION VARIABLES        ####
##################################################