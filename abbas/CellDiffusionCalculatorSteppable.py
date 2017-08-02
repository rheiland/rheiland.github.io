from PySteppables import *
import CompuCell
import sys
import time
from math import *


class CellDiffusionCalculatorSteppable(SteppablePy):
   def __init__(self,_simulator,_frequency=1):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.frequ=_frequency
      #self.aa=[]
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.nTrackerPlugin=CompuCell.getNeighborTrackerPlugin()
      self.cellFieldG=self.simulator.getPotts().getCellFieldG()
      self.dim=self.cellFieldG.getDim()

      #self.output_file = open("cellDiffusionData.txt",'w')
      
   def start(self):
      for cell in self.cellList:
	if cell.type == 1 or cell.type == 2:
	    list_attrib=CompuCell.getPyAttrib(cell)
	    ptx=float(cell.xCM/float(cell.volume)) 
	    pty=float(cell.yCM/float(cell.volume)) 
	    list_attrib[0:2]=[ptx,pty]
      import CompuCellSetup
      self.pW=CompuCellSetup.viewManager.plotManager.getNewPlotWindow()
      if not self.pW:
          return
      #Plot Title - properties           
      self.pW.setTitle("Cell Diffusion")
      self.pW.setTitleSize(12)
      self.pW.setTitleColor("Green")
        
      #plot background
      self.pW.setPlotBackgroundColor("orange")
        
      # properties of x axis
      self.pW.setXAxisTitle("MonteCarlo Step (MCS)")
      self.pW.setXAxisTitleSize(10)      
      self.pW.setXAxisTitleColor("blue")              
        
      # properties of y axis
      self.pW.setYAxisTitle("<displacement^2>/4")        
      #self.pW.setYAxisLogScale()
      self.pW.setYAxisTitleSize(10)        
      self.pW.setYAxisTitleColor("red")                      
        
      self.pW.addPlot("Non-Condensing")
      self.pW.addPlot("Condensing")
      # plot MCS
      self.pW.changePlotProperty("Non-Condensing","LineWidth",1)
      self.pW.changePlotProperty("Non-Condensing","LineColor","red")     
      # plot MCS1
      self.pW.changePlotProperty("Condensing","LineWidth",1)
      self.pW.changePlotProperty("Condensing","LineColor","green")

      
      self.pW.addGrid()
      #adding automatically generated legend
      # default possition is at the bottom of the plot but here we put it at the top
      self.pW.addAutoLegend("top")

      self.pW2=CompuCellSetup.viewManager.plotManager.getNewPlotWindow()
      if not self.pW2:
          return
      #Plot Title - properties           
      self.pW2.setTitle("Cell Displacement/MCS")
      self.pW2.setTitleSize(12)
      self.pW2.setTitleColor("Green")
        
      #plot background
      self.pW2.setPlotBackgroundColor("orange")
        
      # properties of x axis
      self.pW2.setXAxisTitle("MonteCarlo Step (MCS)")
      self.pW2.setXAxisTitleSize(10)      
      self.pW2.setXAxisTitleColor("blue")              
        
      # properties of y axis
      self.pW2.setYAxisTitle("<Displacement>")        
      #self.pW.setYAxisLogScale()
      self.pW2.setYAxisTitleSize(10)        
      self.pW2.setYAxisTitleColor("red")                      
        
      self.pW2.addPlot("Non-Condensing")
      self.pW2.addPlot("Condensing")
      # plot MCS
      self.pW2.changePlotProperty("Non-Condensing","LineWidth",1)
      self.pW2.changePlotProperty("Non-Condensing","LineColor","red")     
      # plot MCS1
      self.pW2.changePlotProperty("Condensing","LineWidth",1)
      self.pW2.changePlotProperty("Condensing","LineColor","green")

      
      self.pW2.addGrid()
      #adding automatically generated legend
      # default possition is at the bottom of the plot but here we put it at the top
      self.pW2.addAutoLegend("top")


      self.pW3=CompuCellSetup.viewManager.plotManager.getNewPlotWindow()
      if not self.pW3:
          return
      #Plot Title - properties           
      self.pW3.setTitle("Average Volume")
      self.pW3.setTitleSize(12)
      self.pW3.setTitleColor("Green")
        
      #plot background
      self.pW3.setPlotBackgroundColor("orange")
        
      # properties of x axis
      self.pW3.setXAxisTitle("MonteCarlo Step (MCS)")
      self.pW3.setXAxisTitleSize(10)      
      self.pW3.setXAxisTitleColor("blue")              
        
      # properties of y axis
      self.pW3.setYAxisTitle("volume")        
      #self.pW.setYAxisLogScale()
      self.pW3.setYAxisTitleSize(10)        
      self.pW3.setYAxisTitleColor("red")                      
        
      self.pW3.addPlot("Non-Condensing")
      self.pW3.addPlot("Condensing")
      # plot MCS
      self.pW3.changePlotProperty("Non-Condensing","LineWidth",1)
      self.pW3.changePlotProperty("Non-Condensing","LineColor","red")     
      # plot MCS1
      self.pW3.changePlotProperty("Condensing","LineWidth",1)
      self.pW3.changePlotProperty("Condensing","LineColor","green")

      
      self.pW3.addGrid()
      #adding automatically generated legend
      # default possition is at the bottom of the plot but here we put it at the top
      self.pW3.addAutoLegend("top")

      self.pW4=CompuCellSetup.viewManager.plotManager.getNewPlotWindow()
      if not self.pW4:
          return
      #Plot Title - properties           
      self.pW4.setTitle("Average Surface Area")
      self.pW4.setTitleSize(12)
      self.pW4.setTitleColor("Green")
        
      #plot background
      self.pW4.setPlotBackgroundColor("orange")
        
      # properties of x axis
      self.pW4.setXAxisTitle("MonteCarlo Step (MCS)")
      self.pW4.setXAxisTitleSize(10)      
      self.pW4.setXAxisTitleColor("blue")              
        
      # properties of y axis
      self.pW4.setYAxisTitle("Surface Area")        
      #self.pW.setYAxisLogScale()
      self.pW4.setYAxisTitleSize(10)        
      self.pW4.setYAxisTitleColor("red")                      
        
      self.pW4.addPlot("Non-Condensing")
      self.pW4.addPlot("Condensing")
      # plot MCS
      self.pW4.changePlotProperty("Non-Condensing","LineWidth",1)
      self.pW4.changePlotProperty("Non-Condensing","LineColor","red")     
      # plot MCS1
      self.pW4.changePlotProperty("Condensing","LineWidth",1)
      self.pW4.changePlotProperty("Condensing","LineColor","green")

      
      self.pW4.addGrid()
      #adding automatically generated legend
      # default possition is at the bottom of the plot but here we put it at the top
      self.pW4.addAutoLegend("top")



   def step(self,mcs):
      self.Potts=self.simulator.getPotts()
      cell_counter1=0
      cell_counter2=0
      d2_CON=0
      d2_NONCON=0
      d_CON=0
      d_NONCON=0
      t1_volume=0
      t2_volume=0
      t1_surface=0
      t2_surface=0

	  
      for cell in self.cellList:
	if cell.type == 1:
	    list_attrib=CompuCell.getPyAttrib(cell)
	    cell_counter1+=1;
	    ptx=float(cell.xCM/float(cell.volume)) 
	    pty=float(cell.yCM/float(cell.volume)) 
	    pt2x=list_attrib[0] 
	    pt2y=list_attrib[1] 
	    dx2=(ptx-pt2x)**2
	    dy2=(pty-pt2y)**2
	    d2_CON+=(dx2+dy2)
	    d_CON+=(dx2+dy2)**(0.5)
	    list_attrib[0]=ptx
	    list_attrib[1]=pty
	    t1_volume += cell.volume
	    t1_surface += cell.surface

	if cell.type == 2:
	    list_attrib=CompuCell.getPyAttrib(cell)
	    cell_counter2+=1;
	    ptx=float(cell.xCM/float(cell.volume)) 
	    pty=float(cell.yCM/float(cell.volume)) 
	    pt2x=list_attrib[0]
	    pt2y=list_attrib[1]
	    dx2=(ptx-pt2x)**2
	    dy2=(pty-pt2y)**2
	    d2_NONCON+=(dx2+dy2)
	    d_NONCON+=(dx2+dy2)**(0.5)
	    list_attrib[0]=ptx
	    list_attrib[1]=pty
	    t2_volume += cell.volume
	    t2_surface += cell.surface



      AVE_d2_CON=d2_CON/cell_counter1/self.frequ
      AVE_d2_NONCON=d2_NONCON/cell_counter2/self.frequ
      AVE_d_CON=d_CON/cell_counter1/self.frequ
      AVE_d_NONCON=d_NONCON/cell_counter2/self.frequ
      if mcs%50==0:
	self.pW.addDataPoint("Condensing",mcs,AVE_d2_CON/4)
	self.pW.addDataPoint("Non-Condensing",mcs,AVE_d2_NONCON/4)
	self.pW.showAllPlots()
	self.pW2.addDataPoint("Condensing",mcs,AVE_d_CON)
	self.pW2.addDataPoint("Non-Condensing",mcs,AVE_d_NONCON)
	self.pW2.showAllPlots()
	self.pW3.addDataPoint("Condensing",mcs,t1_volume/cell_counter1)
	self.pW3.addDataPoint("Non-Condensing",mcs,t2_volume/cell_counter2)
	self.pW3.showAllPlots()
	self.pW4.addDataPoint("Condensing",mcs,t1_surface/cell_counter1)
	self.pW4.addDataPoint("Non-Condensing",mcs,t2_surface/cell_counter2)
	self.pW4.showAllPlots()


