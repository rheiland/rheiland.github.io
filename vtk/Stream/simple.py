###!/usr/local/bin/python

from libVTKCommonPython import *
from libVTKGraphicsPython import *
from libVTKImagingPython import vtkPNMWriter,vtkScalarBarActor,vtkScaledTextActor,vtkTextMapper
from libVTKContribPython import *
from libVTKPatentedPython import *
from libVTKLocalPython import *
import os, math
# boiler.py

#----- boilerplate:  DO NOT CHANGE  -------------

#--- Create the renderer (only one now)
ren = vtkRenderer()
ren.SetBackground(0.0,0.0,0.0)
ren.TwoSidedLightingOn()

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(400,400)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

gridReader = vtkStructuredGridReader()
gridReader.SetFileName('simple.vtk')
gridReader.Update()
grid = gridReader.GetOutput()

vMaxNorm =  grid.GetPointData().GetVectors().GetMaxNorm()
print "vector max norm: ", vMaxNorm
#vector max norm:  1.0

#-------------------------------------
cone = vtkConeSource()
cone.SetResolution(1)   # 0=line, 1=tri, 2=2 crossed tris, >3=3D
cone.SetHeight(0.2)
cone.SetRadius(0.05)


glyph = vtkGlyph3D()
glyph.SetInput( grid )
glyph.SetSource(cone.GetOutput())
#glyph.SetScaleFactor( 0.06 )
glyph.ScalingOff()
#glyph.SetVectorModeToUseVector()
#glyph.SetColorModeToColorByVector()

glyphMapper = vtkPolyDataMapper()
glyphMapper.SetInput( glyph.GetOutput() )
glyphMapper.ScalarVisibilityOff()
glyphMapper.SetScalarRange(0.0, 1.0)

glyphActor = vtkLODActor()
glyphActor.SetMapper( glyphMapper )

#------
sline1IJKSeedFilter = vtkExtractGrid()
sline1IJKSeedFilter.SetInput(grid)
sline1IJKSeedFilter.SetVOI(0,0, 0,10000, 0,0)
sline1IJKSeedFilter.Update()
sline1IJKSeed = sline1IJKSeedFilter.GetOutput()

sline1IJKSeedMapper = vtkDataSetMapper()
sline1IJKSeedMapper.SetInput(sline1IJKSeed)

sline1IJKSeedActor = vtkActor()
sline1IJKSeedActor.SetMapper(sline1IJKSeedMapper)
sline1IJKSeedMapper.ScalarVisibilityOff()
sline1IJKSeedActor.GetProperty().SetColor(0.0,1.0,0.0)

#-------------------------------------
rk4 = vtkRungeKutta4()

sline1 =  vtkStreamLine()
sline1.SetIntegrator(rk4)
sline1.SetInput( grid )
sline1.SetSource( sline1IJKSeed )
#sline1.SetSource( grid )
sline1.SetIntegrationDirectionToForward()
#sline1.SetIntegrationDirectionToBackward()
#sline1.SetIntegrationDirectionToIntegrateBothDirections()
sline1.SetMaximumPropagationTime(100.0)
sline1.SetStepLength(0.0001)

sline1Mapper = vtkPolyDataMapper()
sline1Mapper.SetInput(sline1.GetOutput())
sline1Mapper.ScalarVisibilityOff()

sline1Actor = vtkActor()
sline1Actor.SetMapper(sline1Mapper)
sline1Actor.GetProperty().SetColor(1,1,1)

#-------------------------------------
ren.AddActor(sline1IJKSeedActor)
ren.AddActor(glyphActor)
ren.AddActor(sline1Actor)

ren.ResetCamera()

iren.Initialize()
iren.Start()
