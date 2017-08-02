#!/usr/local/bin/python
#
# Randy Heiland, NCSA/UIUC

import sys, string, regex, re
from random import *
from libVTKCommonPython import *
from libVTKGraphicsPython import *

argc = len(sys.argv)
print 'argc=',argc
if argc < 2:
	print 'Usage: ',sys.argv[0],' <npts>'
	raise ValueError, 'Too few input args'

npts = string.atof(sys.argv[1])


ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#-------------------
sval=1.0
xoff=0.0
pts = vtkPoints()
aVertex = vtkVertex()
scalars = vtkScalars()

math = vtkMath()
math.RandomSeed(1234)

pts.SetNumberOfPoints(npts)
for ipt in range(0,npts):
#  xval = random() - 0.5    # random() in [0..1]
#  yval = random() - 0.5
  # or via VTK's class
  xval =  math.Random(-0.5,0.5)
  yval =  math.Random(-0.5,0.5)
#  print 'x,y = ',ipt,xval,yval
#  print xval,yval,math.Random(-0.5,0.5)
  pts.InsertPoint(ipt,xval,yval,0)
#  aVertex.GetPointIds().SetId(ipt,ipt)
  # scalar = distance (squared)
  sval = xval*xval + yval*yval
  scalars.InsertScalar(ipt, sval)

# add corner pts if desired
xoff = 0.5
yoff = 0.5
pts.InsertPoint(npts,-xoff,-yoff,0)
pts.InsertPoint(npts+1,xoff,-yoff,0)
pts.InsertPoint(npts+2,xoff,yoff,0)
pts.InsertPoint(npts+3,-xoff,yoff,0)

#  and their scalars
sval = xoff*xoff + yoff*yoff
scalars.InsertScalar(npts, sval)
scalars.InsertScalar(npts+1, sval)
scalars.InsertScalar(npts+2, sval)
scalars.InsertScalar(npts+3, sval)


ptsPD = vtkPolyData()
ptsPD.SetPoints(pts)
ptsPD.GetPointData().SetScalars(scalars)
ptsPD.Update()
srange = ptsPD.GetPointData().GetScalars().GetRange()
print 'srange = ',srange
print 'srange[0] = ',srange[0]


delny = vtkDelaunay2D()
delny.SetInput(ptsPD)
#delny.BoundingTriangulationOn()
delny.SetTolerance(0.001)
#delny.SetAlpha(0.0)
#delny.Update()

smooth = vtkSmoothPolyDataFilter()
smooth.SetInput(delny.GetOutput())

mapper = vtkPolyDataMapper()
#mapper.SetInput(delny.GetOutput())
mapper.SetInput(smooth.GetOutput())
mapper.ScalarVisibilityOn()
mapper.SetScalarRange(srange[0],srange[1])

actor = vtkActor()
actor.SetMapper(mapper)
#actor.GetProperty().BackfaceCullingOn()
#actor.GetProperty().SetRepresentationToWireframe()
ren.AddActor(actor)

#---------------------------
wsize=300
renWin.SetSize(wsize,wsize)

#ren.SetBackground(0.5,0.5,0.5)
ren.GetActiveCamera().Zoom(1.4)

renWin.Render()
renWin.SetFileName( "del.ppm")
renWin.SaveImageAsPPM()

iren.Start()
