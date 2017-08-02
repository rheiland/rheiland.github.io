# Create some (x,y,z) points on the outer ring and display sphere "glyphs" there
import math         # this will let us use the sin and cos functions, etc.
from vtk import *   # this will let us use some graphics objects
from array import *


ninetyDegRad = math.pi / 2.0   # 90 degs (in radians)
thetaStart = -ninetyDegRad     # we want to start at the bottom
thetaStop  = ninetyDegRad * 3  # stop at bottom
numPts = 21     # number of points we want to display
thetaDelta = (thetaStop - thetaStart) / (numPts-1)

c1 = array('f',[])    # we will store pts in an array
c1pts = vtkPoints()   # the 'pts' object will hold all our points (x,y,z)
theta = thetaStart
z = 0.0
R = 280
for i in range(0, numPts):  # explain 'range' (0,1,...,numPts-1)
    x = R*math.cos(theta)  # Notice we use the namespace "math" due to our import
    y = R*math.sin(theta)
    print i,x,y,z
    c1.append(x)
    c1.append(y)
    c1.append(z)
    c1pts.InsertPoint(i, x, y, z)
    theta = theta + thetaDelta

# The following section will create spherical glyphs at the points
c1pd = vtkPolyData()
c1pd.SetPoints(c1pts)

# Use sphere as glyph source.
spheres = vtkSphereSource()
spheres.SetRadius(12.)
spheres.SetPhiResolution(10)
spheres.SetThetaResolution(10)

c1g = vtkGlyph3D()
c1g.SetInput(c1pd)
c1g.SetSource(spheres.GetOutput())

c1gm = vtkPolyDataMapper()
c1gm.SetInputConnection(c1g.GetOutputPort())

c1ga = vtkActor()
c1ga.SetMapper(c1gm)
c1ga.GetProperty().SetColor(1.0, 0.0, 0.0)  # set (red,green,blue) colors

#-------------
# Display the 3D axes too
aa = vtkAxesActor()
alen = 150
aa.SetTotalLength(alen,alen,alen)

#-------------
# Now create the RenderWindow, Renderer and Interactor
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#-------------
# Add the actors
ren.AddActor(c1ga)
ren.AddActor(aa)

renWin.SetSize(400, 400)

iren.Initialize()
renWin.Render()
iren.Start()
