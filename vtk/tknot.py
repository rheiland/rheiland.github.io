#!/usr/local/bin/python
#
# Toroidal knots - knots that lie on a torus; the orbit of a system of ODEs
#   R.Heiland, NCSA/UIUC
#
# Usage:
#    tknot.py p0 p1 stepSize n0 nN nMod contourVal
# e.g:
#    tknot.py 1 2 .001 1000 7500 40 0.25
#    tknot.py 2 2 .001 1000 7500 40 0.25
#    tknot.py 2 3 .001 1000 7500 40 0.25
#    tknot.py 2 5 .001 1000 7500 40 0.15
#

import sys, string, regex, re
#from scanfile import scanner

from libVTKCommonPython import *
from libVTKGraphicsPython import *
from colors import *
from math import *

#------------------------
argc = len(sys.argv)
print 'argc=',argc
if argc < 8:
	print 'Usage: ',sys.argv[0],' <p0 p1 stepsize n0 nmax modnpts contVal>'
	raise ValueError, 'Too few input args'

# Params for system of ODEs
p0 = string.atof(sys.argv[1])
p1 = string.atof(sys.argv[2])

stepSize = string.atof(sys.argv[3])
# Iteration # to begin orbit (allows skipping past transients)
n0 = string.atof(sys.argv[4])
nmax = string.atof(sys.argv[5])

# Only keep modulo # of pts on orbit
imod = string.atoi(sys.argv[6])

# Contour value for implicit model
contVal = string.atof(sys.argv[7])

#------------------------
# Define the basic system of ODEs:  X' = f(X)
def tknot(flag,x,y,z,p0,p1):
  if flag < 0:
    return( -p0*y + p1*x*z )
  elif flag == 0:
    return( p0*x + p1*y*z )
  else:
    return( (p1/2.0) * (1.0 + z*z - x*x - y*y) )

#------------------------
#stepSize = 0.01
#p0 = 2.0
#p1 = 3.0

# Initial condition
x0 = 1.0
y0 = 1.0
z0 = 1.0

# Create the RenderWindow, Renderer and both Actors
#
ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#
# Create polylines (vtkPolyData) 
#
knotPts = vtkPoints()

#nmax = 20
kpts = 0
xmin=1.e30
xmax= -xmin
#imod= 20

#  Euler integration (ackkk)
for i in range(0,nmax):
  x = x0 + stepSize * tknot(-1,x0,y0,z0,p0,p1)
  y = y0 + stepSize * tknot(0,x0,y0,z0,p0,p1)
  z = z0 + stepSize * tknot(1,x0,y0,z0,p0,p1)
  x0 = x
  y0 = y
  z0 = z
  if (i >= n0):
    if ((i%imod) == 0):
      knotPts.InsertPoint(kpts,x,y,z)
      kpts = kpts + 1

print 'kpts=', kpts
#print 'bounds=', knotPts.GetBounds()
bounds = knotPts.GetBounds()
print 'bounds=', bounds
print 'bounds[1]=', bounds[1]
#bounds= (-2.38745927811, 1.84893298149, -1.84781503677, 2.40681290627, -1.04142177105, 1.03351640701)

# polylines
knotPL = vtkCellArray()
knotPL.InsertNextCell(kpts) 
for i in range(0,kpts):
  knotPL.InsertCellPoint(i)

# polyData
knotPD = vtkPolyData()
knotPD.SetPoints(knotPts)
knotPD.SetLines(knotPL)

knotMap = vtkPolyDataMapper()
knotMap.SetInput(knotPD)

knotActor = vtkActor()
knotActor.SetMapper(knotMap)
knotActor.GetProperty().SetColor(1.0,0.0,0.0)

# Add the actors to the renderer, set the background and size
#
ren.AddActor(knotActor)
ren.SetBackground(1,1,1)
#ren.SetBackground(0,0,0)


#---- create implicit models of rings:
tube1 = vtkImplicitModeller()
tube1.SetInput(knotPD)
#tube1.SetSampleDimensions(50,50,50)
d=50
tube1.SetSampleDimensions(d,d,d)
#dmax= 0.25
dmax= 0.125
tube1.SetMaximumDistance(dmax)

r= 2.0
#tube1.SetModelBounds(-r,r,-r,r,-r,r)
#bounds= (-2.38745927811, 1.84893298149, -1.84781503677, 2.40681290627, -1.04142177105, 1.03351640701)
#tube1.SetModelBounds(bounds)
#tube1.SetModelBounds(-3,2,-2,3,-1.2,1.2)
tube1.SetModelBounds(-3,3,-3,3,-2,2)

contour1 = vtkContourFilter()
contour1.SetInput(tube1.GetOutput())
#contVal = 0.25
contour1.SetValue(0,contVal)

opac = 1.0
tube1Mapper = vtkPolyDataMapper()
tube1Mapper.SetInput(contour1.GetOutput())
tube1Mapper.ScalarVisibilityOff()
tube1Actor = vtkActor()
tube1Actor.SetMapper(tube1Mapper)
tube1Actor.GetProperty().SetColor(red[0],red[1],red[2])
tube1Actor.GetProperty().SetOpacity(opac)

ren.AddActor(tube1Actor)

wsize=300
renWin.SetSize(wsize,wsize)

renWin.Render()
# render the image
#
iren.Initialize()

iren.Start()
