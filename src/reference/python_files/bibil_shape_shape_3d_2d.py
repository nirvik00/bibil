"""
Created on Jun 6, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import math
import ghpythonlib.components as ghcomp
import copy
import scriptcontext as sc

vec = sc.sticky["Vector"]
TOL = sc.doc.ModelAbsoluteTolerance
#import pydevd as py
#py.settrace()

class Shape:
    """
    Parent shape operations and information
    """
    TOL = sc.doc.ModelAbsoluteTolerance
    
    def __init__(self,geom,cplane=None):
        self.geom = geom
        self.cplane = cplane
        self.north = rs.VectorCreate([0,1,0],[0,0,0])
        self.area = None
        self.local_north = None
    def reset(self):
        def get_dim_bbox(b):
            ## counterclockwise, start @ bottom SW  
            #      n_wt
            #      -----
            #      |   |
            # w_ht |   | e_ht = y_dist
            #      |   |
            #      -----
            #     s_wt = x_dist
            return b[:2],b[1:3],b[2:4],[b[3],b[0]]
            self.cplane = self.get_cplane_advanced(self.geom)
        # primary edges
        try:
            self.bottom_crv = self.get_bottom(self.geom,self.get_boundingbox(self.geom,None)[0])
        except Exception as e:
            print e
        try:
            if self.cplane == None:
                self.cplane = self.get_cplane_advanced(self.geom)
                self.local_north = self.cplane.YAxis
        except Exception as e:
            print e
        try:
            self.bbpts = self.get_boundingbox(self.geom,self.cplane)
            self.s_wt,self.e_ht,self.n_wt,self.w_ht = get_dim_bbox(self.bbpts)
            # x,y,z distances
            self.x_dist = float(rs.Distance(self.s_wt[0],self.s_wt[1]))
            self.y_dist = float(rs.Distance(self.e_ht[0],self.e_ht[1]))
            self.area = None
        except Exception as e:
            print e
    def op_split(self,axis,ratio,deg=0.,split_depth=0):
        """
        op_split: self, ratio -> (list of geom)
        Splits original geom into two
        """
        def helper_make_split_srf_z(ratio_):
            try:
                zht = ratio_ * self.z_dist
                splitptlst = self.bbpts[:4]+[self.bbpts[0]]
                splitptlst = map(lambda b:rc.Geometry.Point3d(b[0],b[1],b[2]+zht),splitptlst)
                splitcurve = rc.Geometry.Curve.CreateControlPointCurve(splitptlst,1)
                split_surf_ = rc.Geometry.Brep.CreatePlanarBreps(splitcurve)[0]
                return split_surf_
            except Exception as e:
                print "Error @ shape.helper_make_split_srf_z"
                print e
        def helper_make_split_srf_xy(ratio_,degree):
            try:
                if axis == "NS":
                    edge_0, edge_1 = self.s_wt, self.n_wt
                    dist = ratio_*self.x_dist
                else:#if axis == "EW"
                    edge_0, edge_1 = self.e_ht, self.w_ht
                    dist = ratio_*self.y_dist
                    
                ### helper geom that splits box
                line_0 = rs.AddLine(edge_0[0],edge_0[1])
                line_1 = rs.AddLine(edge_1[1],edge_1[0])
                # ^flip because counterclockwise
                mid_0 = rs.DivideCurveLength(line_0,dist,True,True)[1]
                mid_1 = rs.DivideCurveLength(line_1,dist,True,True)[1]            
                split_line = rs.AddCurve([mid_0,mid_1],1)
                if float(degree) > 0.5:
                    cpt = rs.DivideCurve(split_line,2,True,True)[1] 
                    split_line = rs.RotateObject(split_line,cpt,degree)
                if self.ht < 1: ht = 1.
                else: ht = self.ht
                split_path = rs.AddCurve([[0,0,0],[0,0,ht*2]],1)
                
                sc_ = 3,3,3
                line_cpt = rs.DivideCurve(split_line,2)[1]
                split_line_ = rs.ScaleObject(split_line,line_cpt,sc_)
                split_surf_ = rs.coercebrep(rs.ExtrudeCurve(split_line,split_path))
                return split_line_, split_surf_
            except Exception as e:
                print "Error @ shape.helper_make_split_srf_xy"
                print e
        
        rs.EnableRedraw(False)
        #if (self.dimension in "3d") == True: self.convert_guid('3d')
        #else: self.convert_guid('2d')
        if axis == "Z":
            split_surf = helper_make_split_srf_z(ratio)
        else:
            split_line,split_surf = helper_make_split_srf_xy(ratio,deg)
        
        try:#if True:
            ## For split_depth == 0.
            if split_depth <= 0.1:
                geom = rs.coercebrep(self.geom) if self.is_guid(self.geom) else self.geom 
                lst_child = geom.Split(split_surf,TOL)
            ## For split_depth > 0.
            else:
                if self.z_dist < 0.09:
                    print 'not a 3d geom, therefore will not split'
                ## check local_north and apply if missing
                if not self.local_north:
                    self.local_north = self.cplane.YAxis
                # to apply local transformations
                vec_angle = rs.VectorAngle(self.north,self.local_north)
                vec_dir = 1 if self.north[0] > self.local_north[0] else -1
                # vec transformation
                
                local_north_line = rs.AddLine([0,0,0],rs.AddPoint(self.local_north[0],self.local_north[1],self.local_north[2]))
                split_angle = rs.Angle2(split_line,local_north_line)
                perpendicular = True if (abs(split_angle[0]-90.)<2. or abs(split_angle[0]-270.)<2) else False
                if not perpendicular:
                    c_xypt = rs.AddPoint(self.cpt[0]+split_depth,self.cpt[1],self.cpt[2])
                else:
                    c_xypt = rs.AddPoint(self.cpt[0],self.cpt[1]+split_depth,self.cpt[2])
                xy_path = rs.AddCurve([self.cpt,c_xypt])
                xy_path_rot = rs.RotateObject(xy_path,self.cpt,vec_angle*vec_dir,[0,0,1])
                cutter = rs.ExtrudeSurface(split_surf,xy_path_rot)
                if not perpendicular:
                    move_pt = rs.AddPoint(self.cpt[0]-split_depth/2.,self.cpt[1],self.cpt[2])
                else:
                    move_pt = rs.AddPoint(self.cpt[0],self.cpt[1]-split_depth/2.,self.cpt[2])
                move_pt = rs.RotateObject(move_pt,self.cpt,vec_angle*vec_dir)
                cutter = rs.CopyObject(cutter,rs.VectorCreate(move_pt,self.cpt))
                rc_geom, rc_cutter = rs.coercebrep(self.geom),rs.coercebrep(cutter)
                rc_cutter.Flip()
                lst_child = rc.Geometry.Brep.CreateBooleanIntersection(rc_geom,rc_cutter,TOL)
                #print 'rotation', rs.coercegeometry(xy_path_rot)
                #self.DEBUG.append(rs.coercegeometry(xy_path_rot))
                #self.DEBUG.append(rc_cutter)
                #self.DEBUG.append(self.cpt)
                #print lst_child
                if lst_child != None and len(lst_child) == 1:
                    rc_cutter.Flip()
                    lst_child = rc.Geometry.Brep.CreateBooleanIntersection(rc_geom,rc_cutter,TOL)
        except Exception as e:
            print "Error @ shape.op_split while splitting"
            print e
        ## Clean up or rearrange or cap the split child geometries
        try:
            if lst_child == None or len(lst_child) == 1:
                lst_child = [copy.copy(self.geom)]
            else:
                if not "2" in self.dimension:
                    if not self.is_guid(lst_child[0]): lst_child_ = map(lambda child: sc.doc.Objects.AddBrep(child), lst_child)
                    map(lambda child: rs.CapPlanarHoles(child),lst_child_)
                    lst_child = map(lambda child: rs.coercebrep(child),lst_child_)
                if axis == "Z":
                    z_0 = rc.Geometry.AreaMassProperties.Compute(lst_child[0]).Centroid[2]
                    z_1 = rc.Geometry.AreaMassProperties.Compute(lst_child[1]).Centroid[2]    
                    if z_0 > z_1: 
                        tempchild = lst_child.pop(0)
                        lst_child.append(tempchild)
        except Exception as e:
            print "Error @ shape.op_split while formatting children"
            print e
        rs.EnableRedraw(False)
        return lst_child
    def get_boundingbox(self,geom_,cplane_):
        def check_bbpts(b):
            ## check if 3d shape and if first 4 pts at bottom
            if b[0][2] > b[4][2]:
                b_ = b[4:] + b[:4]
                b = b_
            return b
        try:
            bbpts_ = rs.BoundingBox(geom_,cplane_)
            return check_bbpts(bbpts_)
        except Exception as e:
            print "Error @ get_boundingbox"
            print e
    def is_guid(self,geom):
        return type(rs.AddPoint(0,0,0)) == type(geom) 
    def convert_rc(self,dim=None):
        # phase this function out
        try:
            if dim==None: dim = self.dimension
            if dim == "2d":
                if self.is_guid(self.crv):
                    self.crv = rs.coercecurve(self.crv)
                if self.is_guid(self.ext):
                    self.ext = rs.coercebrep(self.ext)
            else:
                if self.is_guid(self.bottom_crv):
                    self.bottom_crv = rs.coercecurve(self.bottom_crv)
            if self.is_guid(self.geom):
                self.geom = rs.coercegeometry(self.geom)
        except Exception as e:
            print "Error @ shape.convert_rc"
            print e
    def convert_guid(self,dim='2d'):
        # phase this out
        try:
            if dim == "2d":
                if not self.is_guid(self.crv):
                    self.crv = sc.doc.Objects.AddCurve(self.crv)
                if not self.is_guid(self.ext):
                    self.ext = sc.doc.Objects.AddBrep(self.ext)
            else:
                if self.bottom_crv and not self.is_guid(self.bottom_crv):
                    self.bottom_crv = sc.doc.Objects.AddCurve(self.bottom_crv)
            if not self.is_guid(self.geom):
                self.geom = sc.doc.Objects.AddBrep(self.geom)
        except Exception as e:
            print "Error @ shape.convert_guid"
            print e
    def get_bottom(self,g,refpt,tol=0.1):
        ## Extract curves from brep according to input cpt lvl
        try:
            if g == None: g = self.geom
            if self.is_guid(refpt): refpt = rs.coerce3dpoint(refpt)
            if self.is_guid(g): g = rs.coercebrep(g)
            plane = rc.Geometry.Plane(refpt,rc.Geometry.Vector3d(0,0,1))
            crvs = g.CreateContourCurves(g,plane)
            return crvs[0]
        except Exception as e:
            print "Error @ shape.get_bottom"
            print e
    def get_shape_axis(self,crv):
        ### Purpose: Input 2d planar curve
        ### and return list of vector axis based
        ### on prominence
        debug = sc.sticky['debug']
        ## topological ordering preserved
        ## direction counterclockwise
        try:
            segments = crv.DuplicateSegments()
            for i in xrange(len(segments)):
                segment = segments[i]
                nc = segment.ToNurbsCurve()
                end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
                #print (end_pts[0],end_pts[1]), '\n'
                if i == 1:
                    debug.append(end_pts[1])
        except Exception as e:
            print "Error @ shape.get_shape_axis"
            print e
    def get_cplane_advanced(self,g):
        def helper_define_axis_pts(pl_):
            ##(origin,x,y)
            o_pt_ = pl_[2]
            x_pt_ = pl_[1]
            y_pt_ = pl_[0]
            return o_pt_,x_pt_,y_pt_
        def helper_rotate_cplane(cplane_,ra_,cpt_):
            ## rotate cplane in xy plane
            axis = rc.Geometry.Vector3d(0,0,1)
            angle_in_radians = math.radians(ra_)
            cplane.Rotate(angle_in_radians,axis,cpt_)
        def helper_local_north(cplane,vecangle_):
            ### defines local_north vector: a vector located
            ### within the local plane, that is closest to world north
            ### Find the orientation closest to local north
            ### within the 90 rotation increments of the 
            ### referenced cplane
            veclst = []
            orient_lst = [0.,90.,180.,270.]
            for orient in orient_lst:
                veclst.append(abs(orient - vecangle_))
            ## find the 90 rotation increment closest to world north
            minindex = min(xrange(len(veclst)),key=veclst.__getitem__)
            orient_angle = orient_lst[minindex]
            return orient_angle
        def helper_check_direction_rotation(cplane_,lno,opt):
            # probably a better way to do this
            helper_rotate_cplane(cplane_,lno,opt)
            pos_angle = vec(self.north).angle(vec(cplane_.YAxis))
            helper_rotate_cplane(cplane_,lno*-2,opt)
            neg_angle = vec(self.north).angle(vec(cplane_.YAxis))
            if pos_angle < neg_angle:
                helper_rotate_cplane(cplane_,lno*2,opt)
            return cplane_
        try:
            if self.is_guid(g):
                brep = rs.coercebrep(g)
            else: brep = g
            debug = sc.sticky['debug']
            ## Get primary axis
            nc = self.bottom_crv.ToNurbsCurve()
            planar_pts = [nc.Points[i].Location for i in xrange(nc.Points.Count)]
            self.get_shape_axis(self.bottom_crv)
            o_pt,x_pt,y_pt = helper_define_axis_pts(planar_pts)
            ## Generate plane
            normal = rc.Geometry.Vector3d(0,0,1)
            cplane = rc.Geometry.Plane(o_pt,normal)
            ## Rotate cplane to align with primary axis (temp)
            y_axis = x_pt - o_pt #create axis through vector subtraction
            align_angle = vec(self.north).angle(vec(y_axis))
            align_angle = float(align_angle)
            helper_rotate_cplane(cplane,align_angle*-1,o_pt)
            ## rotate cplane yaxis according to world north
            local_north_orient = helper_local_north(cplane,align_angle)
            cplane = helper_check_direction_rotation(cplane,local_north_orient,o_pt)
            self.local_north = cplane.YAxis
            #debug.append(cplane)
            return cplane
        except Exception as e:
            print "Error @ shape.get_cplane_advanced"
            print e
        
    def get_area(self):
        try:
            area_crv = self.bottom_crv if self.dimension == '3d' else self.crv
            if self.is_guid(area_crv):area_crv = rs.coercecurve(area_crv)
            try:
                area = rc.Geometry.AreaMassProperties.Compute(area_crv).Area
            except Exception as e:
                print e
                area = self.x_dist * self.y_dist
            self.area = area
            return area
        except Exception as e:
            print "Error @ shape.get_area"
            print e
    def get_long_short_axis(self):
        if (self.x_dist > self.y_dist): 
            long_dist,short_dist = self.x_dist,self.y_dist
            long_axis,short_axis = 'EW','NS'
        else:
            long_dist,short_dist = self.y_dist,self.x_dist
            long_axis,short_axis = 'NS','EW'
        return long_axis,long_dist,short_axis,short_dist
    def make_face(self,curve_,z,face=None):
        # phase this out
        try:
            if not face:
                face = rc.Geometry.Extrusion.Create(curve_,z,False)
                cp = self.get_cplane(face)
                face = sc.doc.Objects.AddSurface(face)
                return Shape_2D(face,cp)
        except Exception as e:
            print "Error @ shape.make_face"
            print e
class Shape_2D(Shape):
    # Phase out??
    """ 
    Shape_2D deals with surfaces. 
    Shape is its parent class, like Shape_3D.
    """
    def __init__(self,geom,cplane=None,local_north=None):  
        Shape.__init__(self,geom,cplane,local_north)
        self.dimension = '2d'
        self.reset()
        self.ext=None
    def reset(self,xy_change=True):
        try:
            if not xy_change:
                curr_ht = rs.BoundingBox(self.ext)[4][2]
                #print 'abs', curr_ht, self.ht
                if not abs(curr_ht-self.ht) <= 2:
                    self.op_extrude_2d(self.ht)
                #Shape.reset(self)
                # face references
            else:
                Shape.reset(self)
                srf_pt = rs.SurfacePoints(self.geom)
                if len(srf_pt) > 4:
                    print "line 189, srfpts > 4"
                else: 
                    #self.crv = sc.doc.Objects.AddCurve(ghcomp.ConvexHull(srf_pt,self.cplane)[1])
                    crv_lst = ghcomp.BrepWireframe(rs.coercebrep(self.geom))  
                    crv = rc.Geometry.Curve.JoinCurves(crv_lst)[0]
                    self.crv = rs.coercecurve(crv)
                self.cpt = rs.SurfaceAreaCentroid(self.geom)[0]
                self.ht = float(self.y_dist)
                self.geom = rs.coercebrep(self.geom)
                Shape.reset(self)
        except Exception as e:
            print "Error @ Shape_2D.reset"
            print e   
class Shape_3D(Shape):
    """ 
    Shape_3D deals with breps and extrusions. 
    Shape is its parent class.
    """
    def __init__(self,geom,cplane=None,reset=True):
        Shape.__init__(self,geom,cplane)
        self.dimension = '3d'
        #super(Shape_3D,self).__init__(geom,cplane,local_north)
        self.bottom_crv = None
        if reset and self.geom != None:
            self.reset()
    def reset(self,xy_change=True):
        try:
            Shape.reset(self)
            bp = self.bbpts
            if xy_change == True:
                self.cpt = rc.Geometry.AreaMassProperties.Compute(self.bottom_crv).Centroid
            # curve profile info
            self.ht = float(bp[4][2])
            self.z_dist = float(float(bp[4][2]) - self.cpt[2])
        except Exception as e:
            print "Error @ Shape_3D.reset"
            print e
    def construct_faces(self):
        # phase this out
        try:
            g = copy.copy(self.bottom_crv)
            cg = rs.coercegeometry(g)
            loc = ghcomp.DeconstructBrep(cg)[1]
            for i,c in enumerate(loc):
                face = rc.Geometry.Extrusion.Create(c,self.z_dist,False)
                cp = self.get_cplane(face)
                #face = sc.doc.Objects.AddSurface(face)
                loc[i] = Shape_2D(face,cp)
            self.face_lst = loc
            self.face_bottom = rs.AddPlanarSrf(g)[0]
            #self.face_bottom = rc.Geometry.Brep.CreatePlanarBreps([cg])[0]
            self.face_top = rs.CopyObject(self.face_bottom,[0,0,self.z_dist])
        except Exception as e:
            print "Error @ Shape_3d.construct_faces"
            print e
    def op_extrude(self,z_dist,curve=None):
        try:
            returnflag = False 
            if curve == None:
                curve = rs.coercecurve(self.bottom_crv) if self.is_guid(self.bottom_crv) else self.bottom_crv
                returnflag = True
            ext = rc.Geometry.Extrusion.Create(curve,z_dist,True)
            ## check if extruded correct dir
            refcpt = rc.Geometry.AreaMassProperties.Compute(ext).Centroid
            v = rc.Geometry.Vector3d(0,0,1)
            if z_dist > 0.:
                if refcpt[2] < self.cpt[2]:
                    #print 'move up'
                    ext.Translate(0.,0.,z_dist)
            else: 
                if refcpt[2] > self.cpt[2]:
                    #print 'move down'
                    ext.Translate(0.,0.,z_dist*-1)
            brep = ext.ToBrep()
            if returnflag == False:return brep
            else:
                self.geom = brep
                self.reset(xy_change=False)
        except Exception as e:
            print "Error @ Shape_3D.op_extrude"
            print e
    def op_check_offset(self,dim,curve,count=0,refcpt = None):
        #print 'count: ', count, 'dim: ', dim
        if count > 5 or int(dim <= 0):
            return None
        else: 
            try:    
                if not self.is_guid(curve):
                    curve = sc.doc.Objects.AddCurve(curve)            
                if not refcpt: 
                    refcpt = rs.CurveAreaCentroid(curve)[0]
                offcurve = rs.OffsetCurve(rs.CopyObject(curve),refcpt,dim,None,1)
                if not offcurve or len(offcurve) > 1: 
                    dim -= 1.
                    count += 1
                    return self.op_check_offset(dim,curve,count,refcpt)
                else:
                    return offcurve[0] 
            except Exception as e:
                print "Error @ Shape_3D.op_check_offset"
                print e
    def op_offset(self,dim,curve,dir="courtyard",useoffcrv=False):
        try:
            rs.EnableRedraw(False)
            shapecurve = self.bottom_crv
            abort = False
            if not self.is_guid(curve):
                curve = sc.doc.Objects.AddCurve(curve)            
            if self.is_guid(shapecurve):
                shapecurve = rs.coercegeometry(rs.CopyObject(shapecurve))
            #curve = "let's break this fucker."
            cpt = rs.CurveAreaCentroid(curve)[0]
            #style[opt] = the corner style
            #0 = None, 1 = Sharp, 2 = Round, 3 = Smooth, 4 = Chamfer
            copy_curve = rs.CopyObject(curve)
            if not useoffcrv:
                check_curve = self.op_check_offset(dim,copy_curve,0,refcpt=cpt)
            else: check_curve = copy_curve
        
            if check_curve:
                if self.is_guid(check_curve): 
                    offcurve = rs.coercecurve(check_curve)
                else:
                    offcurve = check_curve
            else:
                print 'courtyard/terrace offset failed'
                diff_geom = None
                abort = True
            if dir=="courtyard" and not abort:
                ht = self.z_dist * 2.5
                geom = copy.copy(self.geom)
                geom = rs.coercegeometry(geom)
                diff_geom = rc.Geometry.Extrusion.Create(offcurve,ht,True)
                #diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
                diff_geom = rs.coercebrep(diff_geom)
            elif dir=="terrace" and not abort:
                ht = self.z_dist+1.
                offgeom = rc.Geometry.Extrusion.Create(offcurve,self.z_dist,True)
                offgeom = sc.doc.Objects.AddBrep(rs.coercebrep(offgeom))
                ext = rc.Geometry.Extrusion.Create(shapecurve,ht,True)
                diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
            elif dir=="terrace_3d" and not abort:
                ht = self.z_dist+1.
                offgeom = rc.Geometry.Extrusion.Create(offcurve,self.z_dist,True)
                offgeom = rs.coercebrep(offgeom)
                geom = copy.copy(self.geom)
                geom = rs.coercebrep(geom)
                ext = rc.Geometry.Extrusion.Create(shapecurve,ht,True)
                diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
            #if dir == "courtyard":
                #print diff_geom
            if not abort:
                try:
                    #if True:
                    if dir=="courtyard":
                        booldiff = rc.Geometry.Brep.CreateBooleanDifference(geom,diff_geom,TOL)
                        if len(booldiff) > 1:
                            self.geom = booldiff
                        else:
                            self.geom = booldiff[0]
                    elif dir=="terrace":
                        booldiff = rs.BooleanIntersection(diff_geom,offgeom,True)
                        #booldiff = map(lambda c: rs.coercegeometry(c),booldiff)
                        self.geom = booldiff[0]
                    elif dir=="terrace_3d":
                        booldiff = rc.Geometry.Brep.CreateBooleanIntersection(geom,offgeom,TOL)
                        booldiff = map(lambda c: sc.doc.Objects.AddBrep(c),booldiff)
                        diff_geom = offgeom
                        if len(booldiff) > 1:
                            self.geom = booldiff
                        else:
                            self.geom = booldiff[0]
                    self.reset()
                except Exception,e: 
                    print str(e)
                    print 'fail op_offset'
            rs.EnableRedraw(True)
            return diff_geom
        except Exception as e:
            print 'Error @ Shape_3D.op_offset'
            print e
            
    def op_solar_envelope(self,start_time,end_time,curve=None):
        try:
            if not curve: curve = self.bottom_crv
            if Shape.is_guid(self,curve): 
                curve = rs.coercecurve(curve)
            se = ghcomp.DIVA.SolarEnvelope(curve,43,start_time,end_time)
            #Solar = sc.sticky["Solar"]
            #monthRange = 1
            #timeperiod = end_time - start_time
            #S = Solar()
            #se = S.main_envelope(curve,timeperiod,monthRange)
            return se
        except Exception as e:
            print "Shape_3D.op_solar_envelope error"
            print e



if True:
    sc.sticky["Shape"] = Shape
    sc.sticky["Shape_2D"] = Shape_2D
    sc.sticky["Shape_3D"] = Shape_3D