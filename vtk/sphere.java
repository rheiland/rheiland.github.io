//
//  Display a VTK sphere
//   (still not sure why I seem to need the "vtk." prefix to the vtk classes
//    if I "import vtk.*")
//
import vtk.*;
import java.awt.*;
import java.awt.event.*;

public class sphere extends Frame implements ActionListener {

  public sphere()
  {
    // Set the title for the Frame
    super("sphere");

    // add a menu
    MenuBar menuBar = new MenuBar();
    setMenuBar(menuBar);
    Menu fileMenu = new Menu("File");
    menuBar.add(fileMenu);
    MenuItem item = new MenuItem("Exit");
    fileMenu.add(item);
    item.addActionListener(this);

    // add the vtkPanel object
    addNotify();
    vtk.vtkPanel renPanel = new vtk.vtkPanel();
    renPanel.setSize(400,400);
    removeAll();
    add(renPanel);

    vtk.vtkSphere sphere = new vtk.vtkSphere();
      sphere.SetRadius(1);
    vtk.vtkSampleFunction sample = new vtk.vtkSampleFunction();
      sample.SetImplicitFunction(sphere);
    vtk.vtkContourFilter iso = new vtk.vtkContourFilter();
      iso.SetInput(sample.GetOutput());
      iso.SetValue(0,0.0);
    vtk.vtkPolyDataMapper isoMapper = new vtk.vtkPolyDataMapper();
      isoMapper.SetInput(iso.GetOutput());
      isoMapper.ScalarVisibilityOff();
    vtk.vtkActor isoActor = new vtk.vtkActor();
      isoActor.SetMapper(isoMapper);
//      isoActor.GetProperty().SetColor(peacock[0],peacock[1],peacock[2])
      isoActor.GetProperty().SetColor(1,0,0);

    vtk.vtkOutlineFilter outline = new vtk.vtkOutlineFilter();
      outline.SetInput(sample.GetOutput());
    vtk.vtkPolyDataMapper outlineMapper = new vtk.vtkPolyDataMapper();
      outlineMapper.SetInput(outline.GetOutput());
    vtk.vtkActor outlineActor = new vtk.vtkActor();
      outlineActor.SetMapper(outlineMapper);
      outlineActor.GetProperty().SetColor(0,0,0);


      // Add actors to renderer
      vtk.vtkRenderer ren = renPanel.getRenderer();
      ren.AddActor(outlineActor);
      ren.AddActor(isoActor);
//          ren.AddVolume(volume);
      ren.SetBackground(0.1, 0.2, 0.4);

      enableEvents(AWTEvent.WINDOW_EVENT_MASK);
      pack();
  }  // end sphere

  public void actionPerformed(ActionEvent e) {
    if (e.getActionCommand().equals("Exit")) {
        dispose();
        System.exit(0);
    }
  }

  protected void processWindowEvent(WindowEvent e) {
      if (e.getID() == WindowEvent.WINDOW_CLOSING) {
          dispose();
          System.exit(0);
      }
      super.processWindowEvent(e);
  }

  public static void main (String[] args) {
      sphere obj = new sphere();
      obj.setVisible(true);
  }
}
