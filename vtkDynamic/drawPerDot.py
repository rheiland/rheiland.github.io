from vtk import *
import os,string,sys,math
try:
  VTK_DATA = os.environ['VTK_DATA']
except KeyError:
  VTK_DATA = '../../../vtkdata/'

argc = len(sys.argv)
print 'argc=',argc
if argc < 2:
    print 'Usage: ',sys.argv[0],' <maxShell>'
    raise ValueError, 'Too few input args'

idx=1
maxShell = string.atoi(sys.argv[idx])
print 'maxShell =',maxShell
idx=idx+1
xctr = maxShell/2
yctr = -maxShell/2

# if we're hardwiring the # of shells (e.g. 50)
xctr = 25
yctr = -xctr

points = vtk.vtkPoints()
#verts = vtk.vtkCellArray()
scalars = vtk.vtkFloatArray()
maxPts = 20
xval = yval = 0.0
print xval,yval
zval = 0.0
npts = 0
points.InsertNextPoint(xval,yval,zval)
scalars.InsertNextValue(npts)

#  points.InsertPoint(idx,xval,yval,zval)
#  scalars.InsertNextValue(float(idx)/maxPts)
#  scalars.InsertNextValue(idx)
#  verts.InsertNextCell(1)
#  verts.InsertCellPoint(0)

#-------- LUTs ---------------
cmapSize = 512
cmapSize = 256
# fire
lutFire = vtkLookupTable()
lutFire.SetHueRange(0.0,0.333)
lutFire.SetSaturationRange(1.0,0.0)
#lutFire.SetValueRange(1.0,1.0)
lutFire.SetNumberOfColors(cmapSize)
lutFire.Build()

# fire-inv
lutFireInv = vtkLookupTable()
lutFireInv.SetHueRange(0.333,0.0)
lutFireInv.SetSaturationRange(0.0,1.0)
#lutFireInv.SetValueRange(1.0,1.0)
lutFireInv.SetNumberOfColors(cmapSize)
lutFireInv.Build()
#-----------------------------

polyData = vtk.vtkPolyData()
polyData.SetPoints(points)
#polyData.SetVerts(verts)
polyData.GetPointData().SetScalars(scalars)

#mapper = vtk.vtkPolyDataMapper()
#mapper.SetInput(polyData)

#actor = vtk.vtkActor()
#actor.SetMapper(mapper)
#actor.GetProperty().SetPointSize(8)
#ren1.AddViewProp(actor)


glyphSource = vtkGlyphSource2D()
glyphSource.SetGlyphTypeToCircle()
#glyphSource.SetGlyphTypeToTriangle()

glyphs = vtkGlyph3D()  # however, should really compare w/ vtkVertexGlyphFilter
glyphs.SetInput(polyData)
glyphs.SetSource(glyphSource.GetOutput())
#glyphs.SetScaleFactor( 10. )
#glyphs.SetIndexModeToScalar()
#glyphs.SetRange(0,2)

glyphs.SetScaleModeToDataScalingOff()
glyphs.SetColorModeToColorByScalar()
#glyphs.SetScaleModeToScaleByScalar()

glyphsMapper = vtkDataSetMapper()
glyphsMapper.SetInput(glyphs.GetOutput())
#glyphsMapper.SetScalarModeToUseCellFieldData()
#glyphsMapper.SelectColorArray("cellType")
#glyphsMapper.SetScalarRange(0,1.0)
#  glyphsMapper.SetScalarRange(minTypeVal,maxTypeVal)
glyphsMapper.SetScalarRange(0,npts)
glyphsMapper.ScalarVisibilityOn()
glyphsMapper.SetLookupTable(lutFire)
glyphsMapper.Update()

glyphsActor = vtkActor()
glyphsActor.SetMapper(glyphsMapper)
#glyphsActor.GetProperty().SetRepresentationToWireframe()
#glyphsActor.GetProperty().SetAmbient(0.7)
#glyphsActor.GetProperty().SetDiffuse(0.0)

#vertsActor = vtkActor()
#vertsActor.SetMapper(glyphsMapper)

ren1 = vtkRenderer()
ren1.SetBackground(0,0,0)

renWin = vtkRenderWindow()
renWin.AddRenderer(ren1)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#------------------------
ren1.AddActor(glyphsActor)
#renWin.SetPosition(512,512)
renWin.SetSize(512,512)

camera = vtk.vtkCamera()
#camera.SetClippingRange(1.81325, 90.6627)
camera.SetFocalPoint(xctr, yctr, 0)
camera.SetPosition(xctr, yctr, 5)
#camera.SetViewUp(0, 1, 0)
camera.ParallelProjectionOn()
camera.Zoom(0.03)
ren1.SetActiveCamera(camera)

renWin.Render()

xval = 1
yval = 1
#maxShell = 5

def updateSceneAfterShell():
  global npts
  glyphsMapper.SetScalarRange(0,npts)  # need to update the LUT range
  polyData.Modified()
  renWin.Render()

def updateScene():
  global xval,yval,zval,npts
  points.InsertNextPoint(xval,yval,zval)
  npts += 1
  scalars.InsertNextValue(npts)

  glyphsMapper.SetScalarRange(0,npts)  # need to update the LUT range
  polyData.Modified()
  renWin.Render()


for shell in range(1,maxShell):
#  print '-------- shell ',shell
  if (shell % 2) > 0:   # odd  -------------------
    xval = shell
    yval = 1
    xdel = 0
    ydel = -1
    for idx in range(shell):  # 1st half (leading up to corner of shell)
      xval += xdel
      yval += ydel
#      print xval,yval
      updateScene()
#      points.InsertNextPoint(xval,yval,zval)
#      npts += 1
#      scalars.InsertNextValue(npts)

    xval += xdel
    yval += ydel
#    print xval,yval
    updateScene()
#    points.InsertNextPoint(xval,yval,zval)
#    npts += 1
#    scalars.InsertNextValue(npts)

    xdel = -1
    ydel = 0
    for idx in range(shell):  # 2nd half
      xval += xdel
      yval += ydel
#      print xval,yval
      updateScene()
#      points.InsertNextPoint(xval,yval,zval)
#      npts += 1
#      scalars.InsertNextValue(npts)

  else:   # even  -------------------
    xval = -1
    yval = -shell
    xdel = 1
    ydel = 0
    for idx in range(shell):  # 1st half (leading up to corner of shell)
      xval += xdel
      yval += ydel
#      print xval,yval
      updateScene()
#      points.InsertNextPoint(xval,yval,zval)
#      npts += 1
#      scalars.InsertNextValue(npts)

    xval += xdel
    yval += ydel
#    print xval,yval
    updateScene()
#    points.InsertNextPoint(xval,yval,zval)
#    npts += 1
#    scalars.InsertNextValue(npts)

    xdel = 0
    ydel = 1
    for idx in range(shell):  # 2nd half
      xval += xdel
      yval += ydel
#      print xval,yval
      updateScene()
#      points.InsertNextPoint(xval,yval,zval)
#      npts += 1
#      scalars.InsertNextValue(npts)

#  glyphsMapper.SetScalarRange(0,npts)  # need to update the 
#  polyData.Modified()
#  scalars.Modified()
#  points.Modified()
#  renWin.Render()

#  updateSceneAfterShell():

print 'npts = ',npts

#iren.Start()  # comment this out for 'time' test
