from vtk import *
database = vtkSQLDatabase.CreateFromURL("mysql://root@localhost/enron")
database.Open(None)

edge_query = database.GetQueryInstance()
edge_query.SetQuery("select sendID, recvID, weight from email_arcs_lastnames")

vertex_query = database.GetQueryInstance()
vertex_query.SetQuery("select firstName, lastName, eid from employeelist")

edge_table = vtkRowQueryToTable()
edge_table.SetQuery(edge_query)
edge_table.Update()
et = edge_table.GetOutput()
print 'et # rows= ',et.GetNumberOfRows()
print 'et # cols= ',et.GetNumberOfColumns()

vertex_table = vtkRowQueryToTable()
vertex_table.SetQuery(vertex_query)
vertex_table.Update()
vt = vertex_table.GetOutput()
print 'vt # rows= ',vt.GetNumberOfRows()
print 'vt # cols= ',vt.GetNumberOfColumns()

va = vtkVariantArray()
va = vt.GetRow(0)
print " --- variant array info ---"
print 'name = ',va.GetName()
print 'num comp = ',va.GetNumberOfComponents()
print 'num tup = ',va.GetNumberOfTuples()
print 'num val = ',va.GetNumberOfValues()


source = vtkTableToGraph()
source.AddInputConnection(edge_table.GetOutputPort())
source.AddLinkVertex("sendID", "eid", False)
source.AddLinkVertex("recvID", "eid", False)
source.AddLinkEdge("sendID", "recvID")
source.SetVertexTableConnection(vertex_table.GetOutputPort())

view = vtkGraphLayoutView()
view.AddRepresentationFromInputConnection(source.GetOutputPort())
view.SetVertexLabelArrayName("lastName")
view.SetVertexLabelVisibility(True)
view.SetEdgeColorArrayName("weight")
view.SetColorEdges(True)

theme = vtkViewTheme.CreateMellowTheme()
theme.SetCellValueRange(0, 0)
theme.SetCellAlphaRange(0.1, 2)
theme.SetCellOpacity(1)
view.ApplyViewTheme(theme)

window = vtkRenderWindow()
window.SetSize(600, 600)
view.SetupRenderWindow(window)
window.GetInteractor().Start()   # need to hit the 'r' key to make verts visible; 'e' will exit


