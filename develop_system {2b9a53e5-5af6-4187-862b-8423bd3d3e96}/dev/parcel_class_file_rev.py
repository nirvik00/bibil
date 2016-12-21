import rhinoscriptsyntax as rs
import math
import operator
import random
import time


from cell_class_file_rev import Cell_class


class Parcel_class(object):
    CELL_LIST=[]
    CELL_VAL_LIST=[]
    COLOR=[150,150,150]
    CELL_CYCLE=[]
    HEIGHT=0.0
    REQ_FAR_ITE=1.0
    GLOBAL_MAX_FAR=1
    
    def clear_list(self,li):
        for i in li:
            li.remove(i)
        if(len(li)>0):
            clear_list(li)

    def __init__(self, x0_, y0_, ax_, by_, cell_cycle_, far_time_cycle_, far_inc_, main_root_, curr_far_):
        self.x0=x0_
        self.y0=y0_
        self.ax=ax_
        self.by=by_
        self.CURR_FAR=curr_far_
        self.CELL_CYCLE=cell_cycle_
        self.FAR_TIME_CYCLE= far_time_cycle_
        self.FAR_INC=far_inc_
        self.MAIN_ROOT=main_root_
        self.INITIAL_AREA=rs.CurveArea(main_root_)[0]
        p0=[]
        p0.append([self.x0,self.y0,0])
        p0.append([self.x0+self.ax,self.y0,0])
        p0.append([self.x0+self.ax,self.y0+self.by,0])
        p0.append([self.x0,self.y0+self.by,0])
        p0.append([self.x0,self.y0,0])
        self.root=rs.AddPolyline(p0)
        self.layer=rs.AddLayer("_prog_parcel_geo")
        rs.ObjectLayer(self.root,self.layer)

    def buildCells(self):
        #print(str(cell_L)+" ; "+str(cell_W))
        x0=int(self.x0)
        y0=int(self.y0)
        ax=int(self.ax)
        by=int(self.by)
        inc_factor=rs.CurveArea(self.MAIN_ROOT)[0]/(self.INITIAL_AREA)
        self.CELL_L=int(ax/(1+inc_factor))
        self.CELL_W=int(by/(1+inc_factor))
        self.CELL_LIST=[]
        try:
            for i in self.CELL_LIST:
                rs.DeleteObject(i.base_geo)
        except:
            pass
        for i in self.CELL_LIST:
            clear_list(i)
        for i in range(x0,x0+ax,self.CELL_L):
            for j in range(y0, y0+by,self.CELL_W ):
                p0=[]
                p0.append([(i), (j), 0])
                p0.append([(i)+self.CELL_L, (j), 0])
                p0.append([(i)+self.CELL_L, (j)+self.CELL_W, 0])
                p0.append([(i), (j)+self.CELL_W, 0])
                p0.append([(i), (j), 0])
                f_p0=rs.AddPolyline(p0)
                cell=Cell_class(rs.CurveAreaCentroid(f_p0)[0], self.CELL_CYCLE)
                self.CELL_LIST.append(cell)
                rs.DeleteObject(f_p0)

    def initCellVal(self, s_li, s_val, ave_li, ave_val, def_val):
        #cell_L=self.CELL_L
        #cell_W=self.CELL_W
        self.CELL_VAL_LIST=[]
        for i in self.CELL_LIST:
            cen=(i.cen)
            p=[]
            p.append([(cen[0]+self.CELL_L/1.25),(cen[1]),0])
            p.append([(cen[0]-self.CELL_L/1.25),(cen[1]),0])
            p.append([(cen[0]),(cen[1]+self.CELL_W/1.25),0])
            p.append([(cen[0]),(cen[1]-self.CELL_W/1.25),0])
            #rs.AddPointCloud(p)
            val=i.initVAL_opt(s_li, s_val, ave_li, ave_val, def_val, p)
            self.CELL_VAL_LIST.append([val, cen])
        #self.showVal()

    def showVal(self):
        for i in self.CELL_VAL_LIST:
            rs.AddTextDot(i[0],i[1])

    def mapValCellToParcel(self):
        val=[]
        for i in self.CELL_VAL_LIST:
            val.append(i[0])
        val.sort()
        self.VAL=val[len(self.CELL_LIST)-1]

    def update(self,ti,t_cyc,t_inc,local_max_far):
        k=0
        for i in self.CELL_LIST:
            res=i.updateCell(self.CURR_FAR)
            if(res==1):
                self.growParcel(local_max_far)
                #i.destroyCell()
                pass
            k+=1
        pass   

    def growParcel(self,local_max_far):
        self.SYSTEM_FAR=local_max_far
        try:
            if(self.ext_srf):
                rs.DeleteObject(self.ext_srf)
        except:
            pass
        try:
            rs.DeleteObject(self.ext_srf)
        except:
           pass
        try:
            self.srf=rs.AddPlanarSrf(self.MAIN_ROOT)
            crv_ar=rs.CurveArea(self.MAIN_ROOT)[0]
            rs.ObjectLayer(self.srf,self.layer)
            k=0
            far=[]
            self.clear_list(far)
            sum_uid=0
            for i in self.CELL_LIST:
                sum_uid+=i.FAR
                far.append(i.FAR)
            far.sort()
            max_far_cell=far[len(self.CELL_LIST)-1]
            avg=sum_uid/4#(len(self.CELL_LIST)-1)
            if(avg>local_max_far):
                avg=local_max_far
            self.HEIGHT=avg*3
            l=rs.AddLine([0,0,0],[0,0,self.HEIGHT])
            ####    DEFINE COLORS WRT LOCAL FAR OF SYSTEM AND PARCEL'S CURRENT FAR
            self.CURR_FAR=avg
            if(self.CURR_FAR>local_max_far):
                self.CURR_FAR=local_max_far
            RE=(self.CURR_FAR/self.SYSTEM_FAR)*255
            if(RE>255):
                RE=255
            if(RE<0):
                RE=0
            GR=0
            BL=int(255-RE)
            if(BL>255):
                BL=255
            if(BL<0):
                BL=0
            self.COLOR=[RE,GR,BL]
            ####    CREATE SURFACE EXTRUSION    ####
            self.ext_srf=rs.ExtrudeSurface(self.srf,l)      
            rs.ObjectLayer(self.ext_srf,"_prog_parcel_3d")
            rs.ObjectColor(self.ext_srf,self.COLOR)
            idx=rs.AddMaterialToObject(self.ext_srf)
            idx=rs.MaterialColor(idx,color=(self.COLOR[0],self.COLOR[1],self.COLOR[2]))
            rs.DeleteObjects([l,self.srf])
            return self.ext_srf
            #self.showAndExportImage()
        except:
            pass

    def showAndExportImage(self):
        ####    FORCE REDRAW    ####
        rs.Redraw()
        ####    FORCE IMAGE     ####
        k=str(time.time()*1000) #NAME THE IMAGE BASED ON SYSTEM CLOCK IN EXP(10+12)
        string_img="test"+k+".jpg"
        ####    CREATE THE IMAGE    ####
        img=rs.CreatePreviewImage(string_img)

    #def mergeParcel(self, B, PARCEL_LENGTH, PARCEL_WIDTH):
    def mergeParcel(self, B):
        x=rs.CurveBooleanUnion([self.MAIN_ROOT,B.MAIN_ROOT])
        if(len(x)==1 and rs.IsCurve(x[0])):
            rs.DeleteObjects(x)
            return 1
        else:
            rs.DeleteObjects(x)
            return 0

    def constructRoot(self, crv_):
        self.MAIN_ROOT=crv_
        """
        rs.DeleteObject(self.root)
        rs.DeleteObject(self.MAIN_ROOT)
        self.completePARCEL()
        self.x0=rs.CurveStartPoint(crv_)[0]
        self.y0=rs.CurveStartPoint(crv_)[1]
        crv_pt=rs.CurvePoints(crv_)
        self.ax=rs.Distance(crv_pt[0],crv_pt[1])
        self.by=rs.Distance(crv_pt[0],crv_pt[1])
        p0=[]
        p0.append([self.x0,self.y0,0])
        p0.append([self.x0+self.ax,self.y0,0])
        p0.append([self.x0+self.ax,self.y0+self.by,0])
        p0.append([self.x0,self.y0+self.by,0])
        p0.append([self.x0,self.y0,0])
        self.root=rs.AddPolyline(p0) 
        """
        #growParcel()
        #pqr=rs.CopyObject(self.root,[0,0,5])
        #rs.ObjectLayer(pqr,"_prog_merged_parcel")
        pass

    def delOBJECT_A(self):
        try:
            rs.DeleteObject(self.ext_srf)
        except:
            pass

    def delOBJECT_B(self):
        try:
            rs.DeleteObject(self.ext_srf)
        except:
            pass
        try:
            rs.DeleteObject(self.srf)
        except:
            pass
        try:
            for i in self.CELL_LIST:
                rs.DeleteObject(i.base_geo)
        except:
            pass
        pass

    def completePARCEL(self):
        rs.DeleteObject(self.root)
        #rs.ObjectColor(self.ext_srf,[150,150,150])
        for i in self.CELL_LIST:
            try:
                rs.DeleteObject(i.base_geo)
            except:
                pass
        pass