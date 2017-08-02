#!/usr/local/bin/python
#
#  dodec.py - construct a dodecahedron
#
from math import *
from libVTKCommonPython import *
from libVTKGraphicsPython import *

ren = vtkRenderer()
ren.SetBackground(1,1,1)
winSize = 100
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(winSize,winSize)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)



#-----------------------
# make a pentagon
origPts = vtkPoints()
#print 'pi = ',pi
twoPi = 2.0*pi
npts = 5
delta = 2.0*pi/npts
deltaDegs = delta*360.0/ twoPi   # convert to degs
xmid = 0.0
ymid = 0.0
for idx in range(0,npts):
  xval = cos(idx*delta)
  yval = sin(idx*delta)
  if idx < 2:
    xmid = xmid + xval
    ymid = ymid + yval
  origPts.InsertPoint(idx,xval,yval,0)
xmid = xmid / 2
ymid = ymid / 2
#print 'x,ymid = ',xmid,ymid
midDist = sqrt(xmid*xmid + ymid*ymid)
print 'midDist=',midDist

origCA = vtkCellArray()
origCA.InsertNextCell(5) #number of points
for idx in range(0,npts):
  origCA.InsertCellPoint(idx)

origPD = vtkPolyData()
origPD.SetPoints(origPts)
origPD.SetPolys(origCA)

origPDMap = vtkPolyDataMapper()
origPDMap.SetInput(origPD)

origPentActor = vtkActor()
origPentActor.SetMapper(origPDMap)
#origPentActor.AddPosition(-d/2.0,-d/2.0,-d/2.0)
origPentActor.GetProperty().SetColor(1.0,0.0,0.0)
#origPentActor.GetProperty().SetRepresentationToWireframe()

#-------------------------
rotOffset = (delta/2.0)*360.0/ twoPi   # convert to degs
#print 'rotOffset= ',rotOffset
nfaces = 1
nfaces = 5
pentsPts = vtkPoints()
faceAngle = 63.435   # dihed angle = acos(-1/sqrt(5)) =~ 116.565
for iface in range(0,nfaces):
  pts = 'pts'+str(iface)
  pts = vtkPoints()

  xform = 'xform' + str(iface)
  xform=vtkTransform()
  xform.Identity()
  zdegs = iface*deltaDegs + rotOffset
#   -- to get vert for 2nd crucial pt
#  zdegs = iface*deltaDegs
#  print 'zdegs = ',zdegs
  xform.RotateZ(zdegs)
  xform.Translate(2*midDist,0,0)
  xform.Translate(-midDist,0,0)
  xform.RotateY(-faceAngle)
  xform.Translate(midDist,0,0)
#   -- to get vert for 2nd crucial pt
#  xform.Translate(2*midDist,0,0)
  xform.Update()

  xform.MultiplyPoints(origPts,pts)
#  print '---- '
  for ipt in range(0, npts):
    xyz = pts.GetPoint(ipt)
#    print 'xyz = ',xyz[0],xyz[1],xyz[2]
    pentsPts.InsertNextPoint(xyz[0],xyz[1],xyz[2])

# crucial pt of interest (to which we need to translate a rotated copy to)
#xyz =  -0.809017002583 2.4898982048 0.0

# 2nd crucial pt of interest
#xyz =  -0.309017002583 -2.12662696838 0.0


#------------------------------
ca = vtkCellArray()
for iface in range(0,nfaces):
#  print 'iface = ',iface
  ca.InsertNextCell(npts) #number of points
  istart = iface*npts
  for idx in range(istart,istart+5):
    ca.InsertCellPoint(idx)
#    print '  idx = ',idx

pd = vtkPolyData()
pd.SetPoints(pentsPts)
pd.SetPolys(ca)

pdMap = vtkPolyDataMapper()
pdMap.SetInput(pd)

pentsActor = vtkActor()
pentsActor.SetMapper(pdMap)
pentsActor.GetProperty().SetColor(1.0,0.0,0.0)
#pentsActor.GetProperty().SetRepresentationToWireframe()

#-----------------------------
pent2Actor = vtkActor()
pent2Actor.SetMapper(pdMap)
pent2Actor.GetProperty().SetColor(0.0,0.0,1.0)
#pent2Actor.GetProperty().SetRepresentationToWireframe()

xform=vtkTransform()
xform.Translate(0, 0, 1+midDist+midDist)
#xform.RotateZ(-rotOffset)
xform.RotateY(-180)
pent2Actor.SetUserMatrix(xform.GetMatrix())

orig2Actor = vtkActor()
orig2Actor.SetMapper(origPDMap)
orig2Actor.GetProperty().SetColor(0.0,0.0,1.0)
orig2Actor.SetUserMatrix(xform.GetMatrix())
#orig2Actor.GetProperty().SetRepresentationToWireframe()

#-----------------------------
Axes = vtkAxes()
#Axes.SetOrigin(0,0,0)
sfactor = 1.0
Axes.SetScaleFactor(sfactor)

AxesTube = vtkTubeFilter()
AxesTube.SetInput(Axes.GetOutput())
AxesTube.SetRadius(0.05)
AxesTube.SetNumberOfSides(8)

AxesTubeMapper = vtkDataSetMapper()
#AxesMapper.SetInput(Axes.GetOutput())
AxesTubeMapper.SetInput(AxesTube.GetOutput())

AxesTubeActor = vtkActor()
AxesTubeActor.SetMapper(AxesTubeMapper)

#----------------------
ren.AddActor(origPentActor)
ren.AddActor(orig2Actor)
ren.AddActor(pentsActor)
ren.AddActor(pent2Actor)
#ren.AddActor(AxesTubeActor)

renWin.Render()
iren.Initialize()
iren.Start()
