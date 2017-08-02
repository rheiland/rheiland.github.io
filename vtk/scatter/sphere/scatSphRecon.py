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
    print 'Usage: ',sys.argv[0],' <ntps nbVal spaceVal>'
    raise ValueError, 'Too few input args'

idx=1
npts = string.atoi(sys.argv[idx])
idx=idx+1
print 'npts = ',npts
nbVal = string.atoi(sys.argv[idx])
idx=idx+1
print 'nbVal = ',nbVal
spaceVal = string.atof(sys.argv[idx])
idx=idx+1
print 'spaceVal = ',spaceVal


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
#  print x,y,z

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
surf = vtkSurfaceReconstructionFilter()
surf.SetInput(spherePD)
surf.Update()
print '----default:'
nb = surf.GetNeighborhoodSize()
ss = surf.GetSampleSpacing()
print 'nb=',nb
print 'ss=',ss
print '----new:'
if nbVal > 0:
  surf.SetNeighborhoodSize(nbVal)
if spaceVal > 0.0:
  surf.SetSampleSpacing(spaceVal)
nb = surf.GetNeighborhoodSize()
ss = surf.GetSampleSpacing()
surf.Update()
print 'nb=',nb
print 'ss=',ss

cf = vtkContourFilter()
cf.SetInput(surf.GetOutput())
cf.SetValue(0,0.0)

#smooth = vtkSmoothPolyDataFilter()
#smooth.SetInput(cf.GetOutput())
#smooth.SetNumberOfIterations(50)
#smooth.BoundarySmoothingOn()
#smooth.SetFeatureAngle(120)
#smooth.SetEdgeAngle(90)
#smooth.SetRelaxationFactor(.025)

#decim = vtkDecimatePro()
#decim.SetInput(smooth.GetOutput())

normals = vtkPolyDataNormals()
normals.SetInput(cf.GetOutput())
#normals.SetInput(smooth.GetOutput())
#normals.SetInput(decim.GetOutput())



massProp = vtkMassProperties()
#massProp.SetInput(pdFilt.GetOutput())
#surfArea = massProp.GetSurfaceArea()
#print 'surfArea = ',surfArea
#print 'math.pi = ',math.pi
#print '4*pi*r^2 = ',4*math.pi*radius*radius

#reverse = vtkReverseSense() 
#reverse.SetInput(cf.GetOutput())
#reverse.ReverseCellsOn()
#reverse.ReverseNormalsOn()

mapper = vtkPolyDataMapper()
#mapper.SetInput(cf.GetOutput())
#mapper.SetInput(reverse.GetOutput())
#mapper.SetInput(smooth.GetOutput())
mapper.SetInput(normals.GetOutput())
mapper.ScalarVisibilityOff()


actor = vtkActor()
actor.SetMapper(mapper)

              
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
renWin.SetFileName("scatSphRecon.ppm")
renWin.SaveImageAsPPM()

iren.Start()
