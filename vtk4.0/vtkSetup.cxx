//
// Mimic what was done for  /VTK/Parallel/paraTkAppInit.cxx
//
// compile something like:
//  g++ -c vtkSetup.cxx -I/pathto/VTK -I/pathto/VTK/Common -I/pathto/VTK/Parallel -I/pathto/mpich-1.2.2.2/include

#define USE_VTK

#ifdef USE_VTK
#include "vtkSystemIncludes.h" // in /VTK/Common
#include "vtkToolkits.h"       // in /VTK
#include "vtkMPIController.h"  // in /VTK/Parallel
#endif


#ifdef USE_VTK
void vtkSetup_cpp(int *argc, char ***argv)
{
  ios::sync_with_stdio();

  vtkMPIController* controller = vtkMPIController::New();
  controller->Initialize(argc, argv);   // does MPI_Init(argc,argv) !!
  vtkMultiProcessController::SetGlobalController(controller);

  // Tcl, yukk...
//  Tk_Main(argc, argv, Tcl_AppInit);

  // hmm,  need to figure out where this should get done
//  controller->Delete();
}
#endif

extern "C" {
#ifdef USE_VTK
  int vtkSetup(int *argc, char ***argv) { vtkSetup_cpp(argc,argv); return 1;}
#else
  int vtkSetup(int *argc, char ***argv) { return 0; }
#endif
}
