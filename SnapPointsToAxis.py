import c4d
from c4d import gui
from c4d import utils
import numpy as np
import operator

# Welcome to the world of Python

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


# Main function
def main():
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    points = []
    p_positions = []
    p_normals = []
    axis = getAxis()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    normal_axis=[c4d.Vector(1,0,0),c4d.Vector(0,1,0),c4d.Vector(0,0,1)]

    
    for o in selected_objects:
        for ID in getSelectedPointIDs(o):
            p=o.GetPoint(ID) # Position of the point
            n=getPointNormal(o,ID) # Average normal of the point
            dictionary = {'id':ID, 'position': p , 'normal': n}
            points.append(dictionary) # Points is dictionary containing all selected vertices

        if len(points):
            
            if axis!=None:
                normal = normal_axis[axis] # to the input axis
                p_positions.sort(key=operator.itemgetter(axis)) # Sort the points based on the input axis 
            else:
                normals = [p['normal'] for p in points]
                normal=getAverageNormal(normals) #Set the alignment axis to the Average the surface normals of all the points

            #Define plane
            planeNormal = np.array([ normal[0], normal[1], normal[2] ])
            planePoint = np.array( [points[0]['position'][0],points[0]['position'][1],points[0]['position'][2]]) #Any point on the plane
            rayDirection = np.array([ normal[0], normal[1], normal[2] ])*-1

            for p in points:
                #Define ray
                rayPoint = np.array( [p['position'][0],p['position'][1],p['position'][2]]) #Current position of the point
                
                Psi = LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint) # This is where the point projects on to the plane
                intersection =c4d.Vector( Psi[0],Psi[1],Psi[2])
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, o)
                o.SetPoint( p['id'], intersection ) # Set the position of the point to position of the intersection 
                o.Message(c4d.MSG_UPDATE)
        else:
            print ("no points selected")
    doc.EndUndo()

def getAverageNormal(normals):
        if len(normals):
            avg_normal = (sum(normals) / len(normals)).GetNormalized()
            return avg_normal
        else:
            return c4d.Vector(0,0,0)


def getAxis():
    bc = c4d.BaseContainer()
    axis = None
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, 120, bc):
        if bc[c4d.BFM_INPUT_VALUE]:
           axis = 0
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, 121, bc):
        if bc[c4d.BFM_INPUT_VALUE]:
           axis = 1
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, 122, bc):
        if bc[c4d.BFM_INPUT_VALUE]:
           axis = 2
    return axis


def getSelectedPointIDs(obj):
    point_indices = []
    selected_points = obj.GetPointS()
    max_length = obj.GetPointCount()
    for i, p in enumerate(selected_points.GetAll(max_length)):
        if p:
            point_indices.append(i)
    return point_indices

def getPointNormal(obj,ID):
    nb = c4d.utils.Neighbor()
    nb.Init(obj)
    polys = nb.GetPointPolys(ID)
    normals = []
    for poly in polys:
        v0 = obj.GetPoint(obj.GetPolygon(poly).a)
        v1 = obj.GetPoint(obj.GetPolygon(poly).b)
        v3 = obj.GetPoint(obj.GetPolygon(poly).d)
        normals.append((v1 - v0).Cross(v3 - v0))
        avg_normal = (sum(normals) / len(normals))
    return avg_normal.GetNormalized()

def LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon:
        raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoint
    return Psi


# Execute main()
if __name__=='__main__':
    print "___________________________________________"
    main()
    c4d.EventAdd()