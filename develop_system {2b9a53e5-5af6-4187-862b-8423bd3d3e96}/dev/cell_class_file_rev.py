import rhinoscriptsyntax as rs
import math
import random
import operator

class Cell_class(object):
    FAR=1.0
    PROB_GROWTH=0.0
    OBJ_CLR=[150,150,150]
    VAL=0.1
    #def __init__(self, cen_, base_geo_, cell_cycle_):
    def __init__(self, cen_, cell_cycle_):
        self.cen=cen_
        #self.base_geo=rs.AddPolyline(base_geo_)
        #rs.ObjectLayer(self.base_geo,"_prog_cell")
        self.CURR_TIME=0.0
        self.CELL_CYCLE=cell_cycle_

#QUICKER ALGO
    def initVAL_opt(self, s_li, s_val, ave_li, ave_val, def_val, p):
        self.VAL=def_val
        true_street=0
        true_avenue=0
        i=0
        j=0
        for i in p:
            px=i
            #px=rs.AddPoint(i)
            for j in s_li:
                m1=rs.PointInPlanarClosedCurve(px,j)
                if(m1==1 or m1==2):
                    true_street+=1
            for k in ave_li:
                m2=rs.PointInPlanarClosedCurve(px,k)
                if(m2==1 or m2==2):
                    true_avenue+=1
            #rs.DeleteObject(px)        
        if(true_street>0 and true_avenue<1):
            self.VAL+=s_val+def_val
        elif(true_street<1 and true_avenue>0):
            self.VAL+=ave_val+def_val
        elif(true_street>0 and true_avenue>0):
            self.VAL+=(ave_val+s_val+def_val)
        else:
            self.VAL=def_val
        #rs.AddTextDot(self.VAL,self.cen)
        return self.VAL
#SHOW EXTRUDED CELL
    def growGeo(self,far):
        try:
            rs.DeleteObject(self.SRF_EXT)
        except:
            pass        
        """
        ext=rs.AddLine([0,0,0],[0,0,self.FAR])
        self.SRF=rs.AddPlanarSrf(self.base_geo)
        self.SRF_EXT=rs.ExtrudeSurface(self.SRF,ext)
        rs.ObjectLayer(self.SRF_EXT,"_prog_cell_geo")
        rs.ObjectColor(self.SRF_EXT,self.OBJ_CLR)
        rs.DeleteObjects([ext,self.SRF])
        """
    def destroyCell(self):
        try:
            rs.DeleteObject(self.SRF_EXT)
            rs.DeleteObject(self.SRF)
        except:
            pass
#UPDATE PROBABILITY TO GROW
    def updateCell(self, far):
        if(self.CURR_TIME<self.CELL_CYCLE):
            self.CURR_TIME+=1
            self.POTENTIAL=(float(self.CURR_TIME)/float(self.CELL_CYCLE))*(self.VAL)*10
        else:
            self.CURR_TIME=0
            self.POTENTIAL=1
        re=255*(self.POTENTIAL)
        bl=255*(1-self.POTENTIAL)
        if(re>=255):
            re=255
        elif(re<0):
            re=0
        else:
            re=re
        gr=0
        if(bl>=255):
            bl=255
        elif(bl<0):
            bl=0
        else:
            bl=bl
            self.OBJ_CLR=[re,gr,bl]
        #use condition to connect probability of growth and potential if required
        pqr=(random.randrange(0,100))*150
        prob_growth=self.POTENTIAL+pqr
        #print(prob_growth)
        #if(prob_growth>=1.0 or pqr<10):
        if(prob_growth>=1.0):
            self.growGeo(self.FAR)
            xfar=self.FAR*(1.2)
            if(xfar>far):
                self.FAR=far
            else:
                self.FAR=xfar
            return 1
        else:
            return 0
