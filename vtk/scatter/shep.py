#!/usr/local/bin/python
#
# Randy Heiland, NCSA/UIUC

import sys, string, regex, re
from random import *
from libVTKCommonPython import *
from libVTKGraphicsPython import *

argc = len(sys.argv)
print 'argc=',argc
if argc < 4:
	print 'Usage: ',sys.argv[0],' <npts> <maxDist> <sample>'
	raise ValueError, 'Too few input args'

npts = string.atof(sys.argv[1])
maxDist = string.atof(sys.argv[2])
print 'maxDist = ',maxDist
sample = string.atoi(sys.argv[3])
print 'sample = ',sample


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


pd = vtkPolyData()
pd.SetPoints(pts)
pd.GetPointData().SetScalars(scalars)
pd.Update()
srange = pd.GetPointData().GetScalars().GetRange()
print 'srange = ',srange
print 'srange[0] = ',srange[0]

shepard = vtkShepardMethod()
shepard.SetInput(pd)
#shepard.SetModelBounds(-xoff,xoff,-yoff,yoff,0,0.01)
#shepard.SetModelBounds(-xoff,xoff,-yoff,yoff,0,0)
#shepard.SetModelBounds(-xoff,xoff,-yoff,yoff,0,0.5)
#shepard.SetMaximumDistance(1.0)
#shepard.SetMaximumDistance(0.1)
shepard.SetMaximumDistance(maxDist)
shepard.SetNullValue(1)
shepard.SetSampleDimensions(sample,sample,2)
shepard.Update()

# Since we really only had/want 2D data, we need to extract a single slice
# from the 3D results of vtkShepardMethod
slice = vtkExtractVOI()
slice.SetInput(shepard.GetOutput())
slice.SetVOI(0,sample-1,0,sample-1,0,0)

mapper = vtkDataSetMapper()
#mapper.SetInput(shepard.GetOutput())
mapper.SetInput(slice.GetOutput())
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
renWin.SetFileName( "shep.ppm")
renWin.SaveImageAsPPM()
iren.Start()

