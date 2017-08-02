from vtk import *
import os,sys

layout = ["pass through","circular","simple 2d","force directed","fast 2d","clustering 2d","random","community 2d"]
argc = len(os.sys.argv)
argv = os.sys.argv
print 'argc = ',argc
print 'argv = ',argv
layoutIdx = 0
if argc < 2:
  print "Usage: %s layoutIdx where layout=%s: " % (argv[0],layout)
  sys.exit()
else:
  layoutIdx = int(argv[1])
  print 'layout = ',layout[layoutIdx]

database = vtkSQLDatabase.CreateFromURL("mysql://root@localhost/enron")
database.Open(None)

edge_query = database.GetQueryInstance()
#edge_query.SetQuery("select sendID, recvID, weight from email_arcs_temp2")
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
# following takes exactly 3 args
source.AddLinkVertex("sendID", "lastName", False)
source.AddLinkVertex("recvID", "lastName", False)

# following results in: vtkTableToGraph (0x69dfc0): TableToGraph does not currently support edges between hidden vertices.
#source.AddLinkVertex("sendID", "eid", True)
#source.AddLinkVertex("recvID", "eid", True)

source.AddLinkEdge("sendID", "recvID")
#source.AddLinkEdge("recvID","sendID")

# following is required 
source.SetVertexTableConnection(vertex_table.GetOutputPort())

# Get some useful info
#print '----- source -----',source.GetOutput()   

print 'IsA UG? ',source.GetOutput().IsA('vtkUndirectedGraph')
print 'IsA DG? ',source.GetOutput().IsA('vtkDirectedGraph')

ug = source.GetOutput()
ug.Update()
print 'numverts=',ug.GetNumberOfVertices()  # 151L
print 'numedges=',ug.GetNumberOfEdges()  # 2234L

vdata = ug.GetVertexData()
vdata.GetNumberOfTuples()    # 151

#va_pids = vdata.GetPedigreeIds()  # libvtkCommonPython.vtkVariantArray
#va_pids.GetNumberOfValues()  # 151

#ug.FindVertex( const vtkVariant &pedigreeID  	 ) 

print 'distG helper=',ug.GetDistributedGraphHelper()  # --> None

vit = vtkVertexListIterator()
ug.GetVertices(vit)
numV=0
numE=0
outEdges = vtkOutEdgeIterator()
#outEdges = vtkGraphEdge()
while vit.HasNext():
  v = vit.Next()  # type(v) -> 'long'; 'vtkIdType' is not defined
  numV += 1
  #print 'numV=',numV
  ug.GetOutEdges(v,outEdges)
  while outEdges.HasNext():
    #e = outEdges.Next()
    e = outEdges.NextGraphEdge()
    numE += 1
 
print 'numV = ',numV
print 'numE = ',numE

view = vtkGraphLayoutView()
view.SetLayoutStrategy(layout[layoutIdx])
elayout=["arc parallel"]
layoutGet=view.GetLayoutStrategy()
#print 'GetLayout= ',layoutGet
view.AddRepresentationFromInputConnection(source.GetOutputPort())
view.SetVertexLabelArrayName("lastName")
view.SetVertexLabelVisibility(True)
view.SetEdgeColorArrayName("weight")
view.SetColorEdges(True)
#view.SetColorEdges(False)

view.SetVertexColorArrayName("weight")
view.SetColorVertices(True)

theme = vtkViewTheme.CreateMellowTheme()
theme.SetCellValueRange(0, 0)
theme.SetCellAlphaRange(0.1, 2)
theme.SetCellOpacity(1)
view.ApplyViewTheme(theme)

window = vtkRenderWindow()
wsize=400
window.SetSize(wsize, wsize)
view.SetupRenderWindow(window)
window.GetInteractor().Start()
# 'r' reset the graph; 'e' exit; 'q' quit(e.g. back to python shell; re-do ...Start()


