#!/usr/local/bin/python

#
# borromean.py
#
# Borromean rings: no 2 are interlocking, but all 3 are!
#  R.Heiland, NCSA/UIUC
#
# Uses vtkImplicitModeller + vtkContourFilter to get tubes
# (purely for example usage; for speed, would use vtkTubeFilter instead)
#

#  libs from VTK pkg (config'd with Python)
from libVTKCommonPython import *
from libVTKGraphicsPython import *
#   colors.py - part of VTK pkg (in /graphics/examplesPython)
from colors import *
from math import *

# Create the RenderWindow, Renderer and both Actors
#
ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renWin.SetSize(300,300)
ren.SetBackground(1,1,1)

# Radii for basic ellipse
r1 = 2.0
r2 = 1.0
npts = 20
delta = 2*3.1415 / (npts-1)

# Names of vtk objs: point, polyline, polydata, mapper, actor, etc. 
pts = ['r1Pts', 'r2Pts', 'r3Pts']
pl = ['r1PL', 'r2PL', 'r3PL']
pd = ['r1PD', 'r2PD', 'r3PD']
mapper = ['r1Map', 'r2Map', 'r3Map']
actor = ['r1Actor', 'r2Actor', 'r3Actor']
tube = ['tube1', 'tube2', 'tube3']
contour = ['contour1', 'contour2', 'contour3']
tubeMapper = ['tubeMap1', 'tubeMap2', 'tubeMap3']
tubeActor = ['tubeActor1', 'tubeActor2', 'tubeActor3']

for iring in range(0,3):

  # Points for rings
  pts[iring] = vtkPoints()

  for i in range(0,npts):
    t = i*delta
#    print "t=", t, "cos(t)=", cos(t)
    if iring == 0:
      pts[iring].InsertPoint(i,0,r1*cos(t),r2*sin(t))
    elif iring == 1:
      pts[iring].InsertPoint(i,r2*cos(t),0,r1*sin(t))
    else:
      pts[iring].InsertPoint(i,r1*cos(t),r2*sin(t),0)

  # Polylines
  pl[iring] = vtkCellArray()
  pl[iring].InsertNextCell(npts) 
  for i in range(0,npts):
    pl[iring].InsertCellPoint(i)

  # PolyData
  pd[iring] = vtkPolyData()
  pd[iring].SetPoints(pts[iring])
  pd[iring].SetLines(pl[iring])

  # Mapper
  mapper[iring] = vtkPolyDataMapper()
  mapper[iring].SetInput(pd[iring])

  actor[iring] = vtkActor()
  actor[iring].SetMapper(mapper[iring])
  actor[iring].GetProperty().SetColor(1.0,0.0,0.0)

  # Add the actor to the renderer
  ren.AddActor(actor[iring])

  # create implicit models of rings (to get tubes via vtkContourFilter;
  #  would really want to use :
  tube[iring] = vtkImplicitModeller()
  tube[iring].SetInput(pd[iring])
  tube[iring].SetSampleDimensions(50,50,50)
  tube[iring].SetMaximumDistance(0.25)

  r= 2.5
  tube[iring].SetModelBounds(-r,r,-r,r,-r,r)

  contour[iring] = vtkContourFilter()
  contour[iring].SetInput(tube[iring].GetOutput())
  contour[iring].SetValue(0,0.25)

  opac = 1.0
  tubeMapper[iring] = vtkPolyDataMapper()
  tubeMapper[iring].SetInput(contour[iring].GetOutput())
  tubeMapper[iring].ScalarVisibilityOff()

  tubeActor[iring] = vtkActor()
  tubeActor[iring].SetMapper(tubeMapper[iring])
  if iring == 0:
    tubeActor[iring].GetProperty().SetColor(red[0],red[1],red[2])
  elif iring == 1:
    tubeActor[iring].GetProperty().SetColor(green[0],green[1],green[2])
  else:
    tubeActor[iring].GetProperty().SetColor(blue[0],blue[1],blue[2])

  tubeActor[iring].GetProperty().SetOpacity(opac)

  ren.AddActor(tubeActor[iring])


renWin.Render()
iren.Initialize()
iren.Start()
