#!/local/people/heiland/Python-2.0/python
####!/usr/local/bin/python
#
import os,string,sys,math
try:
  VTK_DATA = os.environ['VTK_DATA']
except KeyError:
  VTK_DATA = '../../../vtkdata/'

argc = len(sys.argv)
print 'argc=',argc
if argc < 2:
    print 'Usage: ',sys.argv[0],' <hullfname>'
    raise ValueError, 'Too few input args'

idx=1
fname = sys.argv[idx]
print 'fname = ',fname
idx=idx+1


from libVTKCommonPython import *
from libVTKGraphicsPython import *
from libVTKImagingPython import *
from libVTKContribPython import *
from libVTKPatentedPython import *

hullF = open(fname,'r')

#	OFF
# 64 122 0
#-0.29047217628 0.126195085618 0.948525547981
# ...
# 
#3 9 2 21 
# ...

hullF.readline()  # skip past 'OFF'
line = hullF.readline()
param = string.split(line)
npts = string.atoi(param[0])
npolys = string.atoi(param[1])
print 'npts,npolys = ',npts,npolys

pts = vtkPoints()
verts = vtkCellArray()

print '----------- loop for pts'
for i in range(0,npts):
  line = hullF.readline()
#  print 'line = ',line
  pt = string.split(line)
#  print 'pt = ',pt
  x = string.atof(pt[0])
  y = string.atof(pt[1])
  z = string.atof(pt[2])
#  print i,x,y,z
  pts.InsertPoint(i,x,y,z)

  verts.InsertNextCell( 1 )
  verts.InsertCellPoint( i )
 
print '----------- loop for polys'
polys = vtkCellArray()
for i in range(0,npolys):
  line = hullF.readline()
#  print 'line = ',line
  pline = string.split(line)
#  print 'pline = ',pline

  nverts = string.atoi(pline[0])
  polys.InsertNextCell( nverts )

  for j in range(0,nverts):
    idx = string.atoi(pline[j+1])
    polys.InsertCellPoint( idx )

spherePD = vtkPolyData()
spherePD.SetPoints(pts)
#spherePD.SetVerts(verts)
spherePD.SetPolys(polys)

#gf = vtkGeometryFilter()
#gf.SetInput(spherePD)

tri = vtkTriangleFilter()
#tri.SetInput(clean.GetOutput())
tri.SetInput(spherePD)

clean = vtkCleanPolyData()
#clean.SetInput(spherePD);
clean.SetInput(tri.GetOutput());

dec = vtkDecimate()
dec.SetInput(tri.GetOutput())
#dec.SetTargetReduction(0.1)

normals = vtkPolyDataNormals()
normals.SetInput(dec.GetOutput())

mapper = vtkPolyDataMapper()
#mapper.SetInput(spherePD)
#mapper.SetInput(gf.GetOutput())
mapper.SetInput(normals.GetOutput())
#mapper.SetInput(tri.GetOutput())
mapper.ScalarVisibilityOff()

#bds = spherePD.GetBounds()
bds = tri.GetOutput().GetBounds()
print 'bds = ',bds

massProp = vtkMassProperties()
#massProp.SetInput(tri.GetOutput())
massProp.SetInput(dec.GetOutput())
surfArea = massProp.GetSurfaceArea()
print 'surfArea = ',surfArea
#print 'math.pi = ',math.pi
radius = 1.0
print '4*pi*r^2 = ',4*math.pi*radius*radius

actor = vtkActor()
actor.SetMapper(mapper)
#actor.GetProperty().SetDiffuse(0.1)
#actor.GetProperty().SetAmbient(0.9)
actor.GetProperty().SetRepresentationToWireframe()

# Create rendering stuff
ren = vtkRenderer()
ren.TwoSidedLightingOn()

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

ren.AddActor(actor)
#ren.SetBackground(1,1,1)
renWin.SetSize(300,300)

ren.GetActiveCamera().Zoom(1.4)

renWin.Render()
renWin.SetFileName("clean.ppm")
renWin.SaveImageAsPPM()

iren.Start()
