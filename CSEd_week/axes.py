from vtk import *
aa=vtkAxesActor()
ren=vtkRenderer()
renWin=vtkRenderWindow()
renWin.AddRenderer(ren)
ren.AddActor(aa)
renWin.Render()
iren=vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.Initialize()
#iren.Start()  # comment out this line if 'run' from ipython; else uncomment
