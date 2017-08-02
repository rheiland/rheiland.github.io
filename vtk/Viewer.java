//
//  Viewer.java - 
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
import javax.swing.border.*;
import javax.swing.event.*;


class Viewer extends JFrame 
  implements ActionListener
{
  // private

  JPanel topPanel;
  private JTabbedPane guiTabbedPane;

  // The vis objects & params panel
  private JPanel visObjPanel;

  // The vis (rendering) panel (vtkPanel)
  private JPanel visPanel;

  private JButton quitBtn;

  // public
//linux (comment out)
  static public VTKPanel vtkVisPanel;


  //-----------------------------
  public JPanel makeDataPanel()
  {
    JPanel dataPanel = new JPanel();
    dataPanel.setLayout(new BorderLayout());

    JTree tree = new JTree();
    dataPanel.add( tree, BorderLayout.CENTER );

    quitBtn = new JButton("Quit");
    dataPanel.add( quitBtn, BorderLayout.SOUTH );
    quitBtn.addActionListener(this);


    return dataPanel;
  } 

  //-----------------------------
  public Viewer()
  {
    setTitle( "VTK Viewer" );
    setBackground( Color.gray );

    topPanel = new JPanel();
    topPanel.setLayout( new BorderLayout() );
//    topPanel.setLayout( new FlowLayout() );
    getContentPane().add( topPanel );


    guiTabbedPane = new JTabbedPane();

    JPanel dataPanel = makeDataPanel();
    guiTabbedPane.addTab( "Data", dataPanel );

    JPanel visPanel = new JPanel();
    visPanel.setLayout( new BorderLayout() );
///* linux
    vtkVisPanel = new VTKPanel();
//    visPanel.add( vtkVisPanel, BorderLayout.CENTER );


    topPanel.add(guiTabbedPane, BorderLayout.WEST);
    topPanel.add(vtkVisPanel, BorderLayout.CENTER);
  }


  //-----------------------------------------
  public void actionPerformed (ActionEvent e) 
//      throws  InterruptedException
  {
    String s = e.getActionCommand();
    System.out.println ("actionPerformed: " + s);
    Object src = e.getSource();
    System.out.println ("src= " + src);

    if (src == quitBtn) {
      System.exit(1);
    }

  }

  public static void main( String args[] )
  {
    // Create an instance of the test application
    Viewer mainFrame = new Viewer();
    mainFrame.pack();
    mainFrame.setVisible( true );
  }
}
