import Rhino
import rhinoscriptsyntax as rs
import operator
import scriptcontext
import math
import random

#def buildParcel(crv, ang):
def buildParcel(crv, ang, parcel_length_x, parcel_width_x, parcel_length_number_x, parcel_width_number_x):    
    bb=rs.BoundingBox(crv)
    crvcen=rs.CurveAreaCentroid(crv)[0]
    bb_pts=rs.AddPolyline([bb[0],bb[1],bb[2],bb[3],bb[0]])
    srf=rs.AddPlanarSrf(bb_pts)
    """
    parcel_length_x=20
    parcel_width_x=40
    parcel_length_number_x=10
    parcel_width_number_x=3
    """
    ave_depth=5
    str_depth=4
    
    srfUdom=rs.SurfaceDomain(srf,0)
    srfVdom=rs.SurfaceDomain(srf,1)
    umin=int(srfUdom[0])
    umax=int(srfUdom[1])
    vmin=int(srfVdom[0])
    vmax=int(srfVdom[1])
    ustep=int(parcel_length_x)
    vstep=int(parcel_width_x)
    p_li=[]

    wx=parcel_width_x
    lx=parcel_length_x
    ad=ave_depth
    sd=str_depth
    wnx=parcel_width_number_x
    lnx=parcel_length_number_x
    ki=0
    for i in range(umin, umax, ustep):
        kj=0
        for j in range(vmin, vmax, vstep):
            if(ki%(lnx+ad)>(int(wx/lx)) and ki%(lnx+ad)<(lnx-int(wx/lx)) and kj%(wnx)!=0):
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
                    else:
                        rs.DeleteObject(p_oly)
            elif((ki%(lnx+ad)>0 and ki%(lnx+ad)<2) and kj%(wnx)>0):
                p=[]
                p.append(rs.EvaluateSurface(srf,i,j))
                p.append(rs.EvaluateSurface(srf,i+vstep,j))
                p.append(rs.EvaluateSurface(srf,i+vstep,j+ustep))
                p.append(rs.EvaluateSurface(srf,i,j+ustep))
                p.append(rs.EvaluateSurface(srf,i,j))
                m0=rs.PointInPlanarClosedCurve(p[0],crv)
                m1=rs.PointInPlanarClosedCurve(p[1],crv)
                m2=rs.PointInPlanarClosedCurve(p[2],crv)
                m3=rs.PointInPlanarClosedCurve(p[3],crv)
                if(m0==0 or m2==0 or m1==0 or m3==0):
                    pass
                else:
                    p_oly=rs.AddPolyline(p)
                    mx=rs.CurveCurveIntersection(p_oly,crv)
                    if(mx is None):
                        p_li.append(p_oly)
                    else:
                        rs.DeleteObject(p_oly)
                q=[]
                q.append(rs.EvaluateSurface(srf,i,j+ustep))
                q.append(rs.EvaluateSurface(srf,i+vstep,j+ustep))
                q.append(rs.EvaluateSurface(srf,i+vstep,j+2*ustep))
                q.append(rs.EvaluateSurface(srf,i,j+2*ustep))
                q.append(rs.EvaluateSurface(srf,i,j+ustep))
                m4=rs.PointInPlanarClosedCurve(p[0],crv)
                m5=rs.PointInPlanarClosedCurve(p[1],crv)
                m6=rs.PointInPlanarClosedCurve(p[2],crv)
                m7=rs.PointInPlanarClosedCurve(p[3],crv)
                if(m4==0 or m5==0 or m6==0 or m7==0):
                    pass
                else:
                    p_oly=rs.AddPolyline(q)
                    nx=rs.CurveCurveIntersection(p_oly,crv)
                    if(nx is None):
                        p_li.append(p_oly)
                    else:
                        rs.DeleteObject(p_oly)
                    pass
            elif((ki%(lnx+ad)>(lnx-int(wx/lx)-1) and ki%(lnx+ad)<(lnx-int(wx/lx)+1)) and kj%(wnx)>0):
                p=[]
                p.append(rs.EvaluateSurface(srf,i,j))
                p.append(rs.EvaluateSurface(srf,i+vstep,j))
                p.append(rs.EvaluateSurface(srf,i+vstep,j+ustep))
                p.append(rs.EvaluateSurface(srf,i,j+ustep))
                p.append(rs.EvaluateSurface(srf,i,j))
                m0=rs.PointInPlanarClosedCurve(p[0],crv)
                m1=rs.PointInPlanarClosedCurve(p[1],crv)
                m2=rs.PointInPlanarClosedCurve(p[2],crv)
                m3=rs.PointInPlanarClosedCurve(p[3],crv)
                if(m0==0 or m2==0 or m1==0 or m3==0):
                    pass
                else:
                    p_oly=rs.AddPolyline(p)
                    mx=rs.CurveCurveIntersection(p_oly,crv)
                    if(mx is None):
                        p_li.append(p_oly)
                    else:
                        rs.DeleteObject(p_oly)
                q=[]
                q.append(rs.EvaluateSurface(srf,i,j+ustep))
                q.append(rs.EvaluateSurface(srf,i+vstep,j+ustep))
                q.append(rs.EvaluateSurface(srf,i+vstep,j+2*ustep))
                q.append(rs.EvaluateSurface(srf,i,j+2*ustep))
                q.append(rs.EvaluateSurface(srf,i,j+ustep))
                m4=rs.PointInPlanarClosedCurve(p[0],crv)
                m5=rs.PointInPlanarClosedCurve(p[1],crv)
                m6=rs.PointInPlanarClosedCurve(p[2],crv)
                m7=rs.PointInPlanarClosedCurve(p[3],crv)
                if(m4==0 or m5==0 or m6==0 or m7==0):
                    pass
                else:
                    p_oly=rs.AddPolyline(q)
                    nx=rs.CurveCurveIntersection(p_oly,crv)
                    if(nx is None):
                        p_li.append(p_oly)
                    else:
                        rs.DeleteObject(p_oly)
            else:
                pass
            kj+=1
        ki+=1

    rs.DeleteObject(srf)
    rs.DeleteObjects([bb_pts])
    #rs.AddTextDot(str("%0.2f"%ang)+","+str(len(p_li)),[crvcen[0],crvcen[1]+500,0])
    #rs.AddTextDot(str(len(p_li)),[crvcen[0],crvcen[1]+500,0])
    return(crv, p_li, len(p_li))


#def mainFunc(crv_site):    
def mainFunc(crv_site,parcel_length, parcel_width, parcel_length_number, parcel_width_number, global_copy_distance):
    ppd=[]
    k=1
    li=[]
    move_constant=500
    crv_site_cen=rs.CurveAreaCentroid(crv_site)[0]
    crv_site_pts=rs.CurvePoints(crv_site)
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
            #x=buildParcel(crv_move,a)
            x=buildParcel(crv_move, a, parcel_length, parcel_width, parcel_length_number, parcel_width_number)
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
            rs.RotateObject(c,mo_cen,a_f)
            rs.ObjectLayer(c,"_prog_ori_parcel")
    rs.RotateObject(mo,mo_cen,a_f) 
    try:
        rs.ObjectLayer(mo_rot,"_prog_empty_site")
    except:
        pass
    for i in lix:
        rs.DeleteObject(i[0])
        rs.DeleteObjects(i[1])
        pass

"""
crv_site=rs.GetObject("pick curve")
crv_site_cen=rs.CurveAreaCentroid(crv_site)[0]
crv_site_pts=rs.CurvePoints(crv_site)
parcel_length_x=20
parcel_width_x=40
parcel_length_number_x=15
parcel_width_number_x=3
ave_depth=5
str_depth=4

# find distance between all points
move_constant=500
#x=buildParcel(crv_site,0)
mainFunc(crv_site)
"""