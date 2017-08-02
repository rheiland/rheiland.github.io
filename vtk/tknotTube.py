#!/usr/local/bin/python
#
# Toroidal knots - knots that lie on a torus; the orbit of a system of ODEs
#   R.Heiland, NCSA/UIUC
#
# Usage:
#    tube.py p0 p1 stepSize n0 nN nMod tubeRad nsides torusRad ppmFile
# e.g:
#    tknotTube.py 1 2 .001 1000 7500 40 0.2 16 .7 tk12.ppm
#    tknotTube.py 2 2 .001 1000 7500 40 0.2 16 .7 tk22.ppm
#    tknotTube.py 2 3 .001 1000 7500 40 0.2 16 .7 tk23.ppm
#    tknotTube.py 2 5 .001 1000 7500 20 0.2 16 .7 tk25.ppm
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
if argc < 11:
	print 'Usage: ',sys.argv[0],' <p0 p1 stepsize n0 nmax modnpts tubeRad nsides torusRad ppmFile>'
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

# tube radius
tubeRad = string.atof(sys.argv[7])
# number of sides for tube 
numSides = string.atoi(sys.argv[8])
torusRad = string.atof(sys.argv[9])

ppmFile = sys.argv[10]
print 'ppmFile=',ppmFile

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


# Generate the tube
tube1 = vtkTubeFilter()
tube1.SetInput(knotPD)
tube1.SetRadius(tubeRad)
tube1.SetNumberOfSides(numSides)

opac = 1.0
tube1Mapper = vtkPolyDataMapper()
tube1Mapper.SetInput(tube1.GetOutput())
tube1Mapper.ScalarVisibilityOff()

tube1Actor = vtkActor()
tube1Actor.SetMapper(tube1Mapper)
tube1Actor.GetProperty().SetColor(red[0],red[1],red[2])
tube1Actor.GetProperty().SetOpacity(opac)

ren.AddActor(tube1Actor)

#-----------------------------------------------
# the torus
torusPts = vtkPoints()
npts = 60
pi = 3.141567
delta = 2*pi / (npts-1)
print "delta=", delta
delta = delta + delta/200.0
r = 1.5
for i in range(0,npts):
  t = i*delta
#  print "t=", t, "cos(t)=", cos(t)
  torusPts.InsertPoint(i,r*cos(t),r*sin(t),0)
#torusPts.Print()

torusCA = vtkCellArray()
torusCA.InsertNextCell(npts) #number.of.points
for i in range(0,npts):
	torusCA.InsertCellPoint(i)

torusPD = vtkPolyData()
torusPD.SetPoints(torusPts)
torusPD.SetLines(torusCA)

torusMap = vtkPolyDataMapper()
#map.SetInput(extrude.GetOutput())
torusMap.SetInput(torusPD)

torusActor = vtkActor()
torusActor.SetMapper(torusMap)
torusActor.GetProperty().SetColor(0.0,1.0,1.0)

#ren.AddActor(torusActor)

# Generate the tube
torusTube = vtkTubeFilter()
torusTube.SetInput(torusPD)
torusTube.SetRadius(torusRad)
torusTube.SetNumberOfSides(numSides)

opac = 1.0
torusTubeMapper = vtkPolyDataMapper()
torusTubeMapper.SetInput(torusTube.GetOutput())
torusTubeMapper.ScalarVisibilityOff()

torusTubeActor = vtkActor()
torusTubeActor.SetMapper(torusTubeMapper)
torusTubeActor.GetProperty().SetColor(cyan[0],cyan[1],cyan[2])
torusTubeActor.GetProperty().SetOpacity(0.5)

ren.AddActor(torusTubeActor)

#---------------------------
wsize=100
renWin.SetSize(wsize,wsize)

cam1=ren.GetActiveCamera()
cam1.Zoom(1.6)

renWin.Render()

renWin.SetFileName( ppmFile )
renWin.SaveImageAsPPM()

# render the image
#
#iren.Initialize()

#iren.Start()
