import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import vtk.*;
import vtkPanel;

public class VText extends JPanel implements ActionListener {
    static JFrame frame;

    Button exitButton;

    public VText() {
	// Create the buttons.
	vtkPanel renWin = new vtkPanel();

        vtkVectorText atext = new vtkVectorText();
        atext.SetText("Test");
        vtkPolyDataMapper followMapper = new vtkPolyDataMapper();
        followMapper.SetInput(atext.GetOutput());
        vtkFollower followActor = new vtkFollower();
        followActor.SetMapper(followMapper);
        followActor.SetScale( 0.2, 0.2, 0.2);
        followActor.GetProperty().SetColor( 1, 0.2, 0.2);
        followActor.SetPosition(0, -0.2, 0);

//        renderer.AddActor(followActor);
        renWin.GetRenderer().AddActor(followActor);

        exitButton = new Button("Exit");
        exitButton.addActionListener(this);

	add(renWin);
	add(exitButton);
    }


    /** An ActionListener that listens to the radio buttons. */
    public void actionPerformed(ActionEvent e) 
    {
        if (e.getSource().equals(exitButton)) 
            {
                System.exit(0);
            }
    }

    public static void main(String s[]) 
    {
	VText panel = new VText();
	
	frame = new JFrame("VText");
	frame.addWindowListener(new WindowAdapter() 
            {
                public void windowClosing(WindowEvent e) {System.exit(0);}
            });
	frame.getContentPane().add("Center", panel);
	frame.pack();
	frame.setVisible(true);
    }
}
