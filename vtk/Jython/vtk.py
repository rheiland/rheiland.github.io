# from Jody Winston <jody@ldeo.columbia.edu>
def add(module):
    """Add the module to the namespace without the vtk prefix"""
    for key in module.__dict__.keys():
	if key[:2] != "__":
            if key[:3] == "vtk":
                globals()[key[3:]] = module.__dict__[key]

    return

try:
    import vtkpython
    add(vtkpython)
    del vtkpython
except ImportError:
    import libVTKGraphicsPython
    add(libVTKGraphicsPython)
    del libVTKGraphicsPython
    
    import libVTKCommonPython
    add(libVTKCommonPython)
    del libVTKCommonPython
    
    import libVTKImagingPython
    add(libVTKImagingPython)
    del libVTKImagingPython
