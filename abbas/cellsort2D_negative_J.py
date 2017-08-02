def configureSimulation(sim):
   import CompuCellSetup
   from XMLUtils import ElementCC3D

   cc3d=ElementCC3D("CompuCell3D")
   potts=cc3d.ElementCC3D("Potts")
   potts.ElementCC3D("Dimensions",{"x":100,"y":100,"z":1})
   potts.ElementCC3D("Steps",{},1000000)
   potts.ElementCC3D("Anneal",{},10)
   potts.ElementCC3D("Temperature",{},10)
   potts.ElementCC3D("Flip2DimRatio",{},1)
   potts.ElementCC3D("NeighborOrder",{},2)

   cellType=cc3d.ElementCC3D("Plugin",{"Name":"CellType"})
   cellType.ElementCC3D("CellType", {"TypeName":"Medium", "TypeId":"0"})
   cellType.ElementCC3D("CellType", {"TypeName":"Condensing", "TypeId":"1"})
   cellType.ElementCC3D("CellType", {"TypeName":"NonCondensing", "TypeId":"2"})

   volume=cc3d.ElementCC3D("Plugin",{"Name":"Volume"})
   volume.ElementCC3D("TargetVolume",{},25)
   volume.ElementCC3D("LambdaVolume",{},5.0)

   volume=cc3d.ElementCC3D("Plugin",{"Name":"Surface"})
   volume.ElementCC3D("TargetSurface",{},25)
   volume.ElementCC3D("LambdaSurface",{},5.0)

   centerOfMass=cc3d.ElementCC3D("Plugin",{"Name":"CenterOfMass"})

   contact=cc3d.ElementCC3D("Plugin",{"Name":"Contact"})
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2":"Medium"},0)
   contact.ElementCC3D("Energy", {"Type1":"NonCondensing", "Type2":"NonCondensing"},-3)
   contact.ElementCC3D("Energy", {"Type1":"Condensing", "Type2":"Condensing"},-10)
   contact.ElementCC3D("Energy",{"Type1":"NonCondensing", "Type2":"Condensing"},-2)
   contact.ElementCC3D("Energy", {"Type1":"NonCondensing", "Type2":"Medium"},1)
   contact.ElementCC3D("Energy", {"Type1":"Condensing", "Type2":"Medium"},1)
   contact.ElementCC3D("NeighborOrder", {}, 2)
   
   chemotaxis=cc3d.ElementCC3D("Plugin",{"Name":"Chemotaxis"})
   chemicalField=chemotaxis.ElementCC3D("ChemicalField", {"Source":"FlexibleDiffusionSolverFE", "Name":"FGF"})
   chemicalField.ElementCC3D("ChemotaxisByType", {"Type":"Condensing" ,"Lambda":3})

   flexDiffSolver=cc3d.ElementCC3D("Steppable",{"Type":"FlexibleDiffusionSolverFE"})
   diffusionField=flexDiffSolver.ElementCC3D("DiffusionField")
   diffusionData=diffusionField.ElementCC3D("DiffusionData")
   diffusionData.ElementCC3D("FieldName",{},"FGF")
   diffusionData.ElementCC3D("DiffusionConstant",{},0.2)
   diffusionData.ElementCC3D("DecayConstant",{},0.01)
   secretionData=diffusionField.ElementCC3D("SecretionData")
   secretionData.ElementCC3D("Secretion",{"Type":"Condensing"},0.0)


   uniform = cc3d.ElementCC3D("Steppable",{"Type":"UniformInitializer"})                                            
   region = uniform.ElementCC3D("Region")
   region.ElementCC3D("BoxMin",{"x":0,  "y":0,  "z":0})                                                
   region.ElementCC3D("BoxMax",{"x":100,  "y":100,  "z":1})                                          
   region.ElementCC3D("Types",{}, "NonCondensing,Condensing")                                                                     
   region.ElementCC3D("Width", {}, 5)


   CompuCellSetup.setSimulationXMLDescription(cc3d)
   
import sys
from os import environ
import string
sys.path.append(environ["PYTHON_MODULE_PATH"])
   
import CompuCellSetup

sim,simthread = CompuCellSetup.getCoreSimulationObjects()

#Create extra player fields here or add attributes
pyAttributeAdder,listAdder=CompuCellSetup.attachListToCells(sim)

configureSimulation(sim)

CompuCellSetup.initializeSimulationObjects(sim,simthread)


from PySteppables import SteppableRegistry
steppableRegistry=SteppableRegistry()
from CellDiffusionCalculatorSteppable import *
CellDiffusionCalculator=CellDiffusionCalculatorSteppable(_simulator=sim,_frequency=50)
steppableRegistry.registerSteppable(CellDiffusionCalculator)

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)


