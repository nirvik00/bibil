import Rhino
import rhinoscriptsyntax as rs
import operator
import scriptcontext
import math
import random

def buildParcel(crv, ang,parcel_length,parcel_width,parcel_length_number, parcel_width_number, move_constant):
    bb=rs.BoundingBox(crv)
    crvcen=rs.CurveAreaCentroid(crv)[0]
    bb_pts=rs.AddPolyline([bb[0],bb[1],bb[2],bb[3],bb[0]])
    srf=rs.AddPlanarSrf(bb_pts)
    
    srfUdom=rs.SurfaceDomain(srf,0)
    srfVdom=rs.SurfaceDomain(srf,1)
    umin=int(srfUdom[0])
    umax=int(srfUdom[1])
    vmin=int(srfVdom[0])
    vmax=int(srfVdom[1])
    ustep=int(parcel_length)
    vstep=int(parcel_width)
    p_li=[]
    ki=0
    for i in range(umin, umax, ustep):
        kj=0
        for j in range(vmin, vmax, vstep):
            if(ki%parcel_length_number!=0 and kj%parcel_width_number!=0):
                p=[]
                p.append(rs.EvaluateSurface(srf,i,j))
                p.append(rs.EvaluateSurface(srf,i+ustep,j))
                p.append(rs.EvaluateSurface(srf,i+ustep,j+vstep))
                p.append(rs.EvaluateSurface(srf,i,j+vstep))
                p.append(rs.EvaluateSurface(srf,i,j))
                m0=rs.PointInPlanarClosedCurve(p[0],crv)
                m1=rs.PointInPlanarClosedCurve(p[1],crv)
                m2=rs.PointInPlanarClosedCurve(p[2],crv)
                m3=rs.PointInPlanarClosedCurve(p[3],crv)
                if(m0==0 or m1==0 or m2==0 or m3==0):
                    pass
                else:
                    p_oly=rs.AddPolyline(p)
                    mx=rs.CurveCurveIntersection(p_oly,crv)
                    if(mx is None):
                        p_li.append(p_oly)
            kj+=1
        ki+=1
    
    rs.DeleteObject(srf)
    rs.DeleteObjects([bb_pts])
    return(crv, p_li, len(p_li))



#def mainFunc(crv_site):
def mainFunc(crv_site,parcel_length,parcel_width,parcel_length_number, parcel_width_number, move_constant):
    crv_site_cen=rs.CurveAreaCentroid(crv_site)[0]
    crv_site_pts=rs.CurvePoints(crv_site)
    ppd=[]
    k=1
    li=[]
    for i in range(len(crv_site_pts)):
        for j in range(2,len(crv_site_pts)-1,1):
            d=rs.Distance(crv_site_pts[i],crv_site_pts[j])
            a=rs.Angle(crv_site_pts[i],crv_site_pts[j])[0]
            if(a<0):
                a+=360
            crv_rot=rs.RotateObjects(crv_site,crv_site_cen,-a,[0,0,1],True)
            b=rs.BoundingBox(crv_site)
            bdi=rs.Distance(b[0],b[1])*(k)
            p=rs.CurveStartPoint(crv_site)
            crv_move=rs.MoveObject(crv_rot,[move_constant*k,0,0])
            x=buildParcel(crv_move,a,parcel_length,parcel_width,parcel_length_number, parcel_width_number, move_constant)
            crv_final=x[0]
            p_li=[]
            for ite in x[1]:
                p_li.append(ite)
            num=x[2]
            temp_li=[crv_final,p_li,num,a]
            li.append([crv_final,p_li,num,a])
            k+=1
    
    lix=sorted(li,key=operator.itemgetter(2))
    n=len(lix)-1
    print("maximum cells are " +str(lix[n][2]))
    crv_final=lix[n][0]
    try:
        rs.DeleteObjects(p_li_final)
    except:
        pass
    num=lix[n][2]
    a_f=lix[n][3]
    crv_final_cen=rs.CurveAreaCentroid(crv_final)[0]
    x0=crv_site_cen[0]
    y0=crv_site_cen[1]
    x=crv_final_cen[0]
    y=crv_final_cen[1]
    mo=rs.CopyObject(crv_final,[x0-x,y0-y,0])
    mo_cen=rs.CurveAreaCentroid(mo)[0]
    for i in lix[n][1]:
        if(rs.IsCurve(i)):
            c=rs.CopyObject(i,[x0-x,y0-y,0])
            parcel=rs.RotateObject(c,mo_cen,a_f)
            try:
                rs.ObjectLayer(parcel,"_prog_ori_parcel")
            except:
                pass
    mo_rot=rs.RotateObject(mo,mo_cen,a_f)
    try:
        rs.ObjectLayer(mo_rot,"_prog_empty_site")
    except:
        pass
    for i in lix:
        rs.DeleteObject(i[0])
        rs.DeleteObjects(i[1])




"""
crv_site=rs.GetObject("pick curve")

####    GLOBAL VARIABLES    ####
parcel_length=10
parcel_width=10
parcel_length_number=8
parcel_width_number=4
move_constant=500

mainFunc(crv_site)
"""