//
//  VTKPanel.java - 
//
//  Author(s): Randy Heiland
//  Email: heiland@ncsa.uiuc.edu
//  WWW: http://www.ncsa.uiuc.edu/People/heiland
//
//  Description:
//
//====================================================================
// Copyright (C) 1999 Board of Trustees of the University of Illinois
//
// This software, both binary and source, is copyrighted by The
// Board of Trustees of the University of Illinois.  Ownership
// remains with the Univerity. For more information, contact:
//
//     Visualization and Virtual Environments
//     National Center for Supercomputing Applications
//     University of Illinois
//     405 North Mathews Ave.
//     Urbana, IL 61801
//====================================================================
import java.awt.*;
import java.awt.event.*;
import java.io.File;
import javax.swing.*;

import vtk.*;


class VTKPanel
  extends 	JPanel
  implements  ActionListener
{
  private vtk.vtkPanel renPanel;
  private vtkRenderer ren;
  private vtkRenderWindow renWin;
  private vtkConeSource cone;
  private vtkPolyDataMapper mapper;
  private vtkActor actor;

  public VTKPanel()
  {
    renPanel = new vtk.vtkPanel();
    renPanel.setSize(700,700);
    setLayout( new BorderLayout() );
    add(renPanel, BorderLayout.CENTER);

    cone = new vtkConeSource();
    mapper = new vtkPolyDataMapper();
      mapper.SetInput(cone.GetOutput());

    actor = new vtkActor();
      actor.SetMapper(mapper);
      actor.GetProperty().SetColor(1,0,0);

    // Add actors to renderer
//    ren = renPanel.getRenderer();
// It seems 'get' has been changed to 'Get' in more recent versions of VTK
      ren = renPanel.GetRenderer();
      ren.SetBackground(1.0, 1.0, 1.0);
      ren.TwoSidedLightingOn();
//      ren.AddActor( (vtkProp)(outlineActor));
      ren.AddActor(actor);

    enableEvents(AWTEvent.WINDOW_EVENT_MASK);
  }

  //---------------------------------------
  public void updatePipeline()
  {
    renPanel.Render();
  }

  //------------------------------------------
  public void actionPerformed (ActionEvent event) 
  {
    String s = event.getActionCommand();
    System.out.println ("actionPerformed: " + s);
  }
}
