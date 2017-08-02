#!/usr/local/bin/python
#
# modified from sphereMap.py
#
import os,string,sys,math
try:
  VTK_DATA = os.environ['VTK_DATA']
except KeyError:
  VTK_DATA = '../../../vtkdata/'

argc = len(sys.argv)
print 'argc=',argc
if argc < 4:
    print 'Usage: ',sys.argv[0],' <ntps tolerance alpha>'
    raise ValueError, 'Too few input args'

idx=1
npts = string.atoi(sys.argv[idx])
idx=idx+1
print 'npts = ',npts
tol = string.atof(sys.argv[idx])
idx=idx+1
print 'tol = ',tol
alpha = string.atof(sys.argv[idx])
idx=idx+1
print 'alpha = ',alpha


from libVTKCommonPython import *
from libVTKGraphicsPython import *
from libVTKImagingPython import *
from libVTKContribPython import *

#------- Generate random pts on a sphere.
vmath = vtkMath()
vmath.RandomSeed(1234)


R=1
twoPi = 2.0*math.pi
print 'twoPi = ',twoPi

pts = vtkPoints()
verts = vtkCellArray()

center = (0,0,0)

for i in range(0,npts):
  z = center[2] + vmath.Random(-R,R)
#  print 'z = ',z
  phi = vmath.Random(0,twoPi)
#  print 'phi = ',phi

  theta = math.asin(z/R)

  x = center[0] + R*math.cos(theta)*math.cos(phi)
  y = center[1] + R*math.cos(theta)*math.sin(phi)
  pts.InsertPoint(i,x,y,z)
 
  verts.InsertNextCell( 1 )
  verts.InsertCellPoint( i )

center = (2.0,0,0)
for i in range(npts,2*npts):
  z = center[2] + vmath.Random(-R,R)
#  print 'z = ',z
  phi = vmath.Random(0,twoPi)
#  print 'phi = ',phi

  theta = math.asin(z/R)

  x = center[0] + R*math.cos(theta)*math.cos(phi)
  y = center[1] + R*math.cos(theta)*math.sin(phi)
  pts.InsertPoint(i,x,y,z)
 
  verts.InsertNextCell( 1 )
  verts.InsertCellPoint( i )


spherePD = vtkPolyData()
spherePD.SetPoints(pts)
spherePD.SetVerts(verts)

#---------------------------------------
delny = vtkDelaunay3D()
delny.SetInput(spherePD)
if tol > 0.0:
  delny.SetTolerance(tol)
delny.SetAlpha(alpha)


pdFilt = vtkGeometryFilter()
pdFilt.SetInput(delny.GetOutput())
#pdFilt.Update()

massProp = vtkMassProperties()
#massProp.SetInput(pdFilt.GetOutput())
#surfArea = massProp.GetSurfaceArea()
#print 'surfArea = ',surfArea
#print 'math.pi = ',math.pi
#print '4*pi*r^2 = ',4*math.pi*radius*radius

mapper = vtkDataSetMapper()
mapper.SetInput(delny.GetOutput())
#mapper.SetInput(pdFilt.GetOutput())
mapper.Update()

actor = vtkActor()
actor.SetMapper(mapper)
#actor.GetProperty().SetDiffuse(0.1)
#actor.GetProperty().SetAmbient(0.9)


              
# Create rendering stuff
ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

ren.AddActor(actor)
#ren.SetBackground(1,1,1)
renWin.SetSize(300,300)

ren.GetActiveCamera().Zoom(1.4)

renWin.Render()
renWin.SetFileName("scatSphDel.ppm")
renWin.SaveImageAsPPM()

iren.Start()
