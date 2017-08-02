#
# python torus.py
#
from libvtkCommonPython import *
from libvtkGraphicsPython import *
from libvtkRenderingPython import *
from libvtkImagingPython import *
from math import *

ren = vtkRenderer()
renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

points = vtkPoints()
npts = 20  # pts per big and small radii
totpts = npts*npts

# Scalars assoc'd with each point
sval = vtkFloatArray()
sval.SetNumberOfTuples(totpts)

points.SetNumberOfPoints( totpts )
c = 2
a = 0.5
k = 0
delta = 2*3.1415 / (npts-1)
# rf.  http://mathworld.wolfram.com/Torus.html
for iv in range(0,npts):
  v = iv*delta
  zval = a*sin(v)
  const = c + a*cos(v)
  for iu in range(0,npts):
    u = iu*delta
    points.InsertPoint(k, const*cos(u), const*sin(u), zval)
    sval.SetValue(k, zval)
    k = k+1

print 'sval range = ',sval.GetRange()

verts = vtkCellArray()
for i in range(0,totpts):
  verts.InsertNextCell( 1 )
  verts.InsertCellPoint( i )

pd = vtkPolyData()
pd.SetPoints( points )
pd.SetVerts( verts )
pd.GetPointData().SetScalars(sval)
pd.Update()
print 'pd range = ',pd.GetPointData().GetScalars().GetRange()
        
pdMapper = vtkPolyDataMapper()
pdMapper.SetInput(pd)
actor = vtkActor()
actor.SetMapper(pdMapper)

surf = vtkDelaunay3D() 
surf.SetInput(pd)
surf.SetAlpha(0.5)

mapper = vtkDataSetMapper()
mapper.SetInput(surf.GetOutput())
mapper.ScalarVisibilityOn()
mapper.SetScalarModeToUsePointData()
mapper.SetColorModeToMapScalars()
mapper.SetScalarRange( -.5, .5) 

surfActor = vtkActor()
surfActor.SetMapper(mapper)

ren.AddActor(actor)
ren.AddActor(surfActor)

renWin.Render()
iren.Start()
