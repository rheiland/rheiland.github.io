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
renWin.SetSize(300,300)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

gridReader = vtkStructuredGridReader()
gridReader.SetFileName('smallerGrid.vtk')
gridReader.Update()
grid = gridReader.GetOutput()

vMaxNorm =  grid.GetPointData().GetVectors().GetMaxNorm()
print "vector max norm: ", vMaxNorm

dims = grid.GetDimensions()
print "------- dims= ", dims
bds = grid.GetBounds()
print "------- bds= ", bds

#------- dims=  (51, 25, 11)
#------- bds=  (2.565000057220459, 4.5872001647949219, 0.0, 0.99929898977279663, -1.4660500288009644, -0.95183098316192627)


#---------------------------------------
Kgrid = vtkExtractGrid()
Kgrid.SetInput( grid )
#Kgrid.SetVOI(50,150, 0,10000,110,110)
#Kgrid.SetVOI(50,150, 0,10000,5,5)
Kgrid.SetVOI(0,10000, 0,10000,5,5)
Kgrid.SetSampleRate(1,1,1)
#Kgrid.Update()

KgridMapper = vtkDataSetMapper()
KgridMapper.SetInput( Kgrid.GetOutput() )
KgridMapper.ScalarVisibilityOff()

KgridActor = vtkActor()
KgridActor.SetMapper( KgridMapper )
KgridActor.GetProperty().SetColor(1,1,0)
KgridActor.GetProperty().SetAmbient(0.5)
KgridActor.GetProperty().SetRepresentationToWireframe()

#-------------------------------------
cone = vtkConeSource()
cone.SetResolution(1)   # 0=line, 1=tri, 2=2 crossed tris, >3=3D
cone.SetHeight(0.01)
cone.SetRadius(0.003)


glyph = vtkGlyph3D()
glyph.SetInput( Kgrid.GetOutput() )
glyph.SetSource(cone.GetOutput())
#glyph.SetVectorModeToUseNormal()
#glyph.SetScaleModeToScaleByVector()
glyph.SetScaleFactor( 0.04 )
glyph.SetScaleFactor( 0.08 )
#glyph.ScalingOff()
#glyph.SetScaleModeToDataScalingOff()
glyph.ScalingOff()
glyph.SetVectorModeToUseVector 
#glyph.ReleaseDataFlagOn()

glyphMapper = vtkPolyDataMapper()
glyphMapper.SetInput( glyph.GetOutput() )
glyphMapper.ScalarVisibilityOn()
glyphMapper.SetScalarRange(0.0, 1.0)

glyphActor = vtkLODActor()
glyphActor.SetMapper( glyphMapper )
glyphActor.GetProperty().SetColor(1,0,0)

#------
sline1IJKSeedFilter = vtkExtractGrid()
sline1IJKSeedFilter.SetInput( grid )
#sline1IJKSeedFilter.SetVOI(2,2,23,24,5,5)
sline1IJKSeedFilter.SetVOI(2,2,23,23,5,5)
sline1IJKSeedFilter.SetSampleRate(1,1,1)

sline1IJKSeed = sline1IJKSeedFilter.GetOutput()
#sline1IJKSeed.Update()
sline1IJKSeedMapper = vtkDataSetMapper()
sline1IJKSeedMapper.SetInput(sline1IJKSeed)

sline1IJKSeedActor = vtkActor()
sline1IJKSeedActor.SetMapper(sline1IJKSeedMapper)
sline1IJKSeedMapper.ScalarVisibilityOff()
sline1IJKSeedActor.GetProperty().SetColor(0.0,1.0,0.0)
#-------------------------------------
rk4 = vtkRungeKutta4()
rk2 = vtkRungeKutta2()

sline1 =  vtkStreamLine()
sline1.SetIntegrator(rk2)
#sline1.DebugOn()
sline1.SetInput( grid )
sline1.SetIntegrationDirectionToForward()
#sline1.SetIntegrationDirectionToBackward()
#sline1.SetIntegrationDirectionToIntegrateBothDirections()

sline1.SetSource(sline1IJKSeedFilter.GetOutput())
sline1.SetMaximumPropagationTime(1000.0)
#sline1.SetStepLength(0.020)
sline1.SetStepLength(0.10)
#sline1.SetIntegrationStepLength(0.1)
#sline1.Update()
tspeed = sline1.GetTerminalSpeed()
print 'tspeed = ',tspeed


sline1Mapper = vtkPolyDataMapper()
sline1Mapper.SetInput(sline1.GetOutput())
sline1Mapper.ScalarVisibilityOff()


sline1Actor = vtkActor()
sline1Actor.SetMapper(sline1Mapper)
sline1Actor.GetProperty().SetColor(0.9,0.9,0.9)

#-------------------------------------
print 'doing outline'
outline = vtkStructuredGridOutlineFilter()
outline.SetInput( grid )
outlineMapper = vtkPolyDataMapper()
outlineMapper.SetInput(outline.GetOutput())
outlineActor = vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(1.0,1.0,0.0)


#-------------------------------------
ren.AddActor(sline1IJKSeedActor)
#ren.AddActor(glyphActor)
ren.AddActor(sline1Actor)
ren.AddActor(outlineActor)
ren.AddActor(KgridActor)

ren.ResetCamera()

iren.Initialize()
iren.Start()
