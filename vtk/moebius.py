#!/usr/local/bin/python
#
# Moebius strip - simple but effective vis of half-twist
#   R.Heiland, NCSA/UIUC
#
# Usage:
#    moebius.py npts bigRadius smallRadius AAFrames winSize
# e.g:
#    moebius.py 100 6 2.5 0 400

from libVTKCommonPython import *
from libVTKGraphicsPython import *
#from libVTKImagingPython import *
#from libVTKPatentedPython import *
from math import *
import sys, string

argc = len(sys.argv)
print 'argc=',argc
if argc < 5:
  print 'Usage: ',sys.argv[0],' <npts> <bigR> <smallR> <AAFrames> <winSize>'
  print 'e.g., 100 6 2.5 0'
  raise ValueError, 'Too few input args'

npts = string.atoi(sys.argv[1])
bigR = string.atof(sys.argv[2])
smallR = string.atof(sys.argv[3])
naa = string.atoi(sys.argv[4])
winSize = string.atoi(sys.argv[5])

ren = vtkRenderer()
ren.SetBackground(1,1,1)
#ren.SetBackground(0,0,0)

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetAAFrames(naa)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# ------- Compute the points along the (single) edge of the strip
points = vtkPoints()
npts_2 = npts / 2
tdel = 4*3.1415 / (npts-1)
s0 = -smallR
s1 = smallR
sdel = (s1-s0) / (npts-1)
for i in range(0,npts):
  t = i*tdel
  t_4 = t/4
  s = s0 + i*sdel
  x = bigR + s*cos(t_4)
  y = 0.0
  z = s * sin(t_4)

  x2 = cos(t) * x - sin(t) * y
  y2 = sin(t) * x + cos(t) * y
#  z2 = cos(t) * x - sin(t) * y
#  print "t=", t, "cos(t)=", cos(t)
  points.InsertPoint(i,x2,y2,z)
#points.Print()

lines = vtkCellArray()
lines.InsertNextCell(npts)
for i in range(0,npts):
  lines.InsertCellPoint(i)

#---- one set of triangles
tris = vtkCellArray()
ioff = 0
for it in range(0,npts_2):
  tris.InsertNextCell(3) #number.of.points
  tris.InsertCellPoint(ioff)
  tris.InsertCellPoint(ioff+1)
  tris.InsertCellPoint(ioff+npts_2)
  ioff = ioff + 1

pd = vtkPolyData()
pd.SetPoints(points)
#pd.SetLines(lines)
pd.SetPolys(tris)

pdMap = vtkPolyDataMapper()
pdMap.SetInput(pd)

moeb = vtkActor()
moeb.SetMapper(pdMap)
moeb.GetProperty().SetColor(1.0,0.0,0.0)
#moeb.GetProperty().SetRepresentationToPoints()

#---- other set of triangles
tris2 = vtkCellArray()
ioff = 0
for it in range(0,npts_2):
  tris2.InsertNextCell(3) #number.of.points
  tris2.InsertCellPoint(ioff)
  tris2.InsertCellPoint(ioff+npts_2)
  tris2.InsertCellPoint(ioff+npts_2-1)
  ioff = ioff + 1

pd2 = vtkPolyData()
pd2.SetPoints(points)
pd2.SetPolys(tris2)

pd2Map = vtkPolyDataMapper()
pd2Map.SetInput(pd2)

moeb2 = vtkActor()
moeb2.SetMapper(pd2Map)
moeb2.GetProperty().SetColor(0.0,1.0,1.0)


#----------------------
axisPts = vtkPoints()
axisPts.InsertPoint(0, -bigR,0,0)
axisPts.InsertPoint(1, bigR,0,0)
axisPts.InsertPoint(2, 0,-bigR,0)
axisPts.InsertPoint(3, 0,bigR,0)

axisCA = vtkCellArray()
axisCA.InsertNextCell(2) #number.of.points
axisCA.InsertCellPoint(0)
axisCA.InsertCellPoint(1)
axisCA.InsertNextCell(2) #number.of.points
axisCA.InsertCellPoint(2)
axisCA.InsertCellPoint(3)

axisPD = vtkPolyData()
axisPD.SetPoints(axisPts)
axisPD.SetLines(axisCA)

axisMap = vtkPolyDataMapper()
axisMap.SetInput(axisPD)

axisActor = vtkActor()
axisActor.SetMapper(axisMap)
axisActor.GetProperty().SetColor(0.0,0.0,0.0)

#----------------------
ren.AddActor(moeb)
ren.AddActor(moeb2)
ren.AddActor(axisActor)

renWin.SetSize(winSize,winSize)

renWin.Render()
iren.Initialize()

w2if = vtkWindowToImageFilter()
w2if.SetInput(renWin)

#pnmw = vtkPNMWriter()
#pnmw.SetInput(w2if.GetOutput())
#pnmw.SetFileName("foo.pnm")
#pnmw.Write()

iren.Start()
