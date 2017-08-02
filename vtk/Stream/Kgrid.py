###!/usr/local/bin/python

from libVTKCommonPython import *
from libVTKGraphicsPython import *
from libVTKContribPython import *
from libVTKPatentedPython import *
from libVTKLocalPython import *
import os, math

ren = vtkRenderer()
ren.SetBackground(0.0,0.0,0.0)
ren.TwoSidedLightingOn()

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(400,400)

iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

gridReader = vtkStructuredGridReader()
gridReader.SetFileName('Kgrid.vtk')
gridReader.Update()
grid = gridReader.GetOutput()

vMaxNorm =  grid.GetPointData().GetVectors().GetMaxNorm()
print "vector max norm: ", vMaxNorm
#vector max norm:  1.0

#-------------------------------------
KgridFilter = vtkExtractGrid()
KgridFilter.SetInput(grid)
KgridFilter.SetVOI(0,10000, 0,10000, 2,2)
KgridFilter.SetVOI(0,10000, 0,10, 2,2)
KgridFilter.SetSampleRate(1,1,1)
Kgrid = KgridFilter.GetOutput()

#-------------------------------------
cone = vtkConeSource()
cone.SetResolution(1)   # 0=line, 1=tri, 2=2 crossed tris, >3=3D
cone.SetHeight(0.01)
cone.SetRadius(0.003)


glyph = vtkGlyph3D()
glyph.SetInput( Kgrid )
glyph.SetSource(cone.GetOutput())
glyph.SetScaleFactor( 0.06 )
glyph.ScalingOff()
glyph.SetVectorModeToUseVector()
glyph.SetColorModeToColorByVector()

glyphMapper = vtkPolyDataMapper()
glyphMapper.SetInput( glyph.GetOutput() )
glyphMapper.ScalarVisibilityOn()
glyphMapper.SetScalarRange(0.0, 1.0)

glyphActor = vtkLODActor()
glyphActor.SetMapper( glyphMapper )

#------
sline1IJKSeedFilter = vtkExtractGrid()
sline1IJKSeedFilter.SetInput(Kgrid)
sline1IJKSeedFilter.SetVOI(5,5, 0,10,0,0)
#sline1IJKSeedFilter.SetSampleRate(1,1,1)
sline1IJKSeedFilter.Update()
sline1IJKSeed = sline1IJKSeedFilter.GetOutput()

sline1IJKSeedMapper = vtkDataSetMapper()
sline1IJKSeedMapper.SetInput(sline1IJKSeed)

sline1IJKSeedActor = vtkActor()
sline1IJKSeedActor.SetMapper(sline1IJKSeedMapper)
sline1IJKSeedMapper.ScalarVisibilityOff()
sline1IJKSeedActor.GetProperty().SetColor(0.0,1.0,0.0)

#-------------------------------------
sline1 =  vtkStreamLine()
sline1.SetInput( grid )
sline1.SetSource( sline1IJKSeed )
sline1.SetIntegrationDirectionToForward()
#sline1.SetIntegrationDirectionToBackward()
#sline1.SetIntegrationDirectionToIntegrateBothDirections()
sline1.SetMaximumPropagationTime(500.0)
sline1.SetStepLength(0.005)

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
