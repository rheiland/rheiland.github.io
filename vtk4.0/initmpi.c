/**************************************************************************/
/* FILE   **************         initmpi.c         ************************/
/**************************************************************************/
/* Author: Patrick Miller January 26 2000  (patmiller@llnl.gov)           */
/* Support Authors:                                                       */
/*        - Martin Casado                                                 */
/*        - Yeechi Chen                                                   */
/*        - Eric Jones                                                    */
/*        - Chris Murray                                                  */
/* Copyright (C) 2000 University of California Regents                    */
/**************************************************************************/
/*                                                                        */
/* This work was produced at the University of California, Lawrence       */
/* Livermore National Laboratory (UC LLNL) under contract no.             */
/* W-7405-ENG-48 (Contract 48) between the U.S. Department of Energy (DOE)*/
/**************************************************************************/

/**************************************************************************/
/* FILE   **************         initmpi.c         ************************/
/**************************************************************************/
/* Author: Patrick Miller January 26 2000  (patmiller@llnl.gov)           */
/* Copyright (C) 2000 University of California Regents                    */
/**************************************************************************/
/*                                                                        */
/* This work was produced at the University of California, Lawrence       */
/* Livermore National Laboratory (UC LLNL) under contract no.             */
/* W-7405-ENG-48 (Contract 48) between the U.S. Department of Energy (DOE)*/
/* and The Regents of the University of California (University) for the   */
/* operation of UC LLNL. The rights of the Federal Government are reserved*/
/* under Contract 48 subject to the restrictions agreed upon by the DOE   */
/* and University as allowed under DOE Acquisition Letter 97-1.           */
/*                                                                        */
/* DISCLAIMER                                                             */
/*                                                                        */
/* This work was prepared as an account of work sponsored by an agency of */
/* the United States Government. Neither the United States Government nor */
/* the University of California nor any of their employees, makes any     */
/* warranty, express or implied, or assumes any liability or              */
/* responsibility for the accuracy, completeness, or usefulness of any    */
/* information, apparatus, product, or process disclosed, or represents   */
/* that its use would not infringe privately-owned rights.  Reference     */
/* herein to any specific commercial products, process, or service by     */
/* trade name, trademark, manufacturer or otherwise does not necessarily  */
/* constitute or imply its endorsement, recommendation, or favoring by the*/
/* United States Government or the University of California. The views and*/
/* opinions of authors expressed herein do not necessarily state or       */
/* reflect those of the United States Government or the University of     */
/* California, and shall not be used for advertising or product           */
/* endorsement purposes.                                                  */
/*                                                                        */
/* NOTIFICATION OF COMMERCIAL USE                                         */
/*                                                                        */
/* Commercialization of this product is prohibited without notifying the  */
/* Department of Energy (DOE) or Lawrence Livermore National Laboratory   */
/* (LLNL).                                                                */
/**************************************************************************/

/* (rwh) for VTK stuff */
extern int vtkSetup(int *argc, char ***argv);


#include "initmpi.h"
#if HAVE_UNISTD_H
#include <unistd.h>
#endif


/* ----------------------------------------------- */
/* AIX's POE has bogus output behavior             */
/* ----------------------------------------------- */
#ifdef _AIX
# undef  FORCEANEWLINE
# define FORCEANEWLINE
#endif


/* ----------------------------------------------- */
/* Some module member data and shared state        */
/* ----------------------------------------------- */
MPI_Comm PyMPI_COMM_WORLD = MPI_COMM_NULL;
MPI_Comm PyMPI_COMM_INPUT = MPI_COMM_NULL;
PyObject* PyMPI_pickleDumperFunction = 0;
PyObject* PyMPI_pickleLoaderFunction = 0;
MPI_Datatype PyMPI_pythonPickleType;
MPI_Datatype PyMPI_pythonFuncPickleType;
int (*PyMPI_finalizeMPI)() = MPI_Finalize;
PyObject* PyMPI_dictionary = 0;

static int someoneHasFinalizedMPI = 0;
static PyObject* overloadedInput = 0;
static char *(*Original_ReadlineFunctionPointer) Py_PROTO((char *)) = 0;
static PyObject* module  = 0;
static PyObject* sysExitfunc = 0;
static int worldRank = 0;
static int worldProcs = 0;
static int (*initializeMPI)(int *, char ***) = MPI_Init;

/* ----------------------------------------------- */
/* Things from Python  not in Python.h             */
/* ----------------------------------------------- */

/*rwh*/
/*extern "C" { } */
extern DL_IMPORT(char*) PyOS_StdioReadline Py_PROTO((char*));
extern DL_IMPORT(char*) Py_GetProgramName Py_PROTO((void));


/* #     #
   #     #   #####     #    #          #     #####     #    ######   ####
   #     #     #       #    #          #       #       #    #       #
   #     #     #       #    #          #       #       #    #####    ####
   #     #     #       #    #          #       #       #    #            #
   #     #     #       #    #          #       #       #    #       #    #
    #####      #       #    ######     #       #       #    ######   #### */


/**************************************************************************/
/* LOCAL  **************    DocStringFromMethods   ************************/
/**************************************************************************/
/* Build a general description from an (optional) overview and a method   */
/* table.                                                                 */
/**************************************************************************/
static char* DocStringFromMethods( PyMethodDef* table, char* overview ) {
    char* buffer = 0;
    int size = 0;
    PyMethodDef* methodPtr;

    if ( !overview ) overview = "";

    /* ----------------------------------------------- */
    /* Make a guess at appropriate length.  We need to */
    /* allocate for the overview, the members, and the */
    /* member descriptions.                            */
    /* ----------------------------------------------- */
    size += strlen(overview);
    for( methodPtr = table; methodPtr && methodPtr->ml_name; ++methodPtr) {
        if ( methodPtr->ml_name ) size += strlen(methodPtr->ml_name);
        if ( methodPtr->ml_doc ) size += strlen(methodPtr->ml_doc);
        size += 16; /* Just for extras */
    }
    buffer = (char*)malloc(size);

    /* ----------------------------------------------- */
    /* Stick in the overview                           */
    /* ----------------------------------------------- */
    strcpy(buffer,overview);

    /* ----------------------------------------------- */
    /* Append method definitions                       */
    /* ----------------------------------------------- */
    for( methodPtr = table; methodPtr && methodPtr->ml_name; ++methodPtr) {
        if ( methodPtr->ml_name ) {
            strcat(buffer,methodPtr->ml_name);
            strcat(buffer,": ");
        }
        if ( methodPtr->ml_doc ) {
            strcat(buffer,methodPtr->ml_doc);
            strcat(buffer,"\n");
        }
        strcat(buffer,"\n");
    }

    return buffer;
}

/**************************************************************************/
/* LOCAL  ************** PyString_ConcatFromString ************************/
/**************************************************************************/
/* Append a null terminated C string to a Python String.  We handle the   */
/* ref count within the routine.                                          */
/**************************************************************************/
static void PyString_ConcatFromString(PyObject** strPtr, char* addend) {
   PyObject* pyAddend = 0;
   
   Assert(strPtr);
   if ( !addend ) return;

   /* ----------------------------------------------- */
   /* Build a Py string from the addend               */
   /* ----------------------------------------------- */
   pyAddend = PyString_FromString(addend);
   PyString_ConcatAndDel(strPtr,pyAddend);
   pyAddend = 0;
}

/**************************************************************************/
/* LOCAL  **************       adjustedPrompt      ************************/
/**************************************************************************/
/* Adds a newline to the character string on some systems                 */
/**************************************************************************/
static char* adjustedPrompt(char* prompt) {
#ifdef FORCEANEWLINE
   char* modprompt;
   int len = strlen(prompt);
   modprompt = malloc(strlen(prompt)+2);
   strcpy(modprompt,prompt);
   strcat(modprompt,"\n");
   return modprompt;
#else
   return prompt;
#endif
}

/**************************************************************************/
/* LOCAL  **************    deleteAdjustedPrompt   ************************/
/**************************************************************************/
/* Delete the prompt we malloc'd in adustedPrompt()                       */
/**************************************************************************/
/*ARGSUSED*/
static void deleteAdjustedPrompt(char* prompt) {
#ifdef FORCEANEWLINE
   free(prompt);
#else
   return;
#endif
}

/**************************************************************************/
/* GLOBAL **************  PyMPI_UnrestrictedOutput ************************/
/************************************************************************ */
/* This function turns on unrestricted output on current processor        */
/**************************************************************************/
void PyMPI_UnrestrictedOutput(int stream) {
    PyObject* pyOutput = 0;
    PyObject* pyErrput = 0;

    if(stream & 0x01)
    {
        PYCHECK( pyOutput = PySys_GetObject("__stdout__"));
        Py_INCREF(pyOutput);
        PYCHECK( PySys_SetObject("stdout",pyOutput));
        Py_INCREF(Py_None);
        PYCHECK( PyDict_SetItemString(PyMPI_dictionary,"outputQueueFile",Py_None));
    }

    if(stream & 0x02)
    {
        PYCHECK( pyErrput = PySys_GetObject("__stderr__"));
        Py_INCREF(pyErrput);
        PYCHECK( PySys_SetObject("stderr",pyErrput));
        Py_INCREF(Py_None);
        PYCHECK( PyDict_SetItemString(PyMPI_dictionary,"errputQueueFile",Py_None));
    }

    /* Fall through */
pythonError:
    return;
}


/* #     # ######    ###
   ##   ## #     #    #       ##    #####   #####            ####   #    #   ####
   # # # # #     #    #      #  #   #    #  #    #          #    #  ##   #  #
   #  #  # ######     #     #    #  #    #  #    #  #####   #    #  # #  #   ####
   #     # #          #     ######  #    #  #    #          #    #  #  # #       #
   #     # #          #     #    #  #    #  #    #          #    #  #   ##  #    #
   #     # #         ###    #    #  #####   #####            ####   #    #   #### */


/**************************************************************************/
/* LOCAL  **************      PyMPI_Finalized      ************************/
/**************************************************************************/
/* IBM doesn't provide a good way to see if MPI Finalize has really been  */
/* called.  Here we provide the interface, but it does not guard against  */
/* dual finalization very well.                                           */
/**************************************************************************/
int PyMPI_Finalized(int* result) {

#ifndef MPI_FINALIZED
   *result = someoneHasFinalizedMPI;
   return MPI_SUCCESS;
#else
   return MPI_Finalized(result);
#endif

}

/**************************************************************************/
/* GLOBAL **************     IHaveFinalizedMPI     ************************/
/**************************************************************************/
/* Use this to tell this module that MPI was finalized by someone else.   */
/* In a more perfect world, MPI_Finalized() would work, but we cannot     */
/* count on that behavior.                                                */
/**************************************************************************/
void PyMPI_IHaveFinalizedMPI() {
#ifdef MPI_FINALIZED
   MPI_Finalized(&someoneHasFinalizedMPI);
   if ( !someoneHasFinalizedMPI ) PyMPI_finalizeMPI();
#endif
   someoneHasFinalizedMPI = 1;
}


/* ######                  ######
   #     #   #   #         #     #  #####    ####   #    #  #####    #####
   #     #    # #          #     #  #    #  #    #  ##  ##  #    #     #
   ######      #           ######   #    #  #    #  # ## #  #    #     #
   #           #           #        #####   #    #  #    #  #####      #
   #           #           #        #   #   #    #  #    #  #          #
   #           #           #        #    #   ####   #    #  #          # */


/**************************************************************************/
/* LOCAL  ************** MPI_ReadlineFunctionPointer **********************/
/**************************************************************************/
/* PURPOSE:  This handles interactive output using the standard mechanism */
/*           on the master which gets the buffer to broadcast to slaves.  */
/*                                                                        */
/* Localization:  AIX's POE environment is forcibly line buffered, so the */
/*                prompt must be flushed with a newline                   */
/**************************************************************************/
static char* MPI_ReadlineFunctionPointer(char* prompt) {
   char* result = 0;
   int stringSize = 0;

   Assert(Original_ReadlineFunctionPointer);
   Assert(prompt);
   if ( worldRank == 0 ) {
      prompt = adjustedPrompt(prompt); /* Apply localization */
      result = Original_ReadlineFunctionPointer(prompt);
      deleteAdjustedPrompt(prompt); /* Release adjusted prompt */
      
      if ( !result ) {
         stringSize = PYTHONBROADCAST_EOT; /* i.e. No Data */
         MPICHECK( PyMPI_COMM_INPUT,
                   MPI_Bcast(&stringSize,1,MPI_INT,0,PyMPI_COMM_INPUT)  );
      } else {
         stringSize = strlen(result);
         MPICHECK( PyMPI_COMM_INPUT,
                   MPI_Bcast(&stringSize,1,MPI_INT,0,PyMPI_COMM_INPUT)  );
         MPICHECK( PyMPI_COMM_INPUT,
                   MPI_Bcast(result,stringSize+1,MPI_CHAR,0,PyMPI_COMM_INPUT)  );
      }
   }

   /* ----------------------------------------------- */
   /* Slaves will be making calls 1-1 with master     */
   /* ----------------------------------------------- */
   else {
     int finalized = 0;
     MPICHECKCOMMLESS( PyMPI_Finalized(&finalized) );
     if ( finalized ) return 0;

      /* Figure out the buffer size */
      MPICHECK( PyMPI_COMM_INPUT,
                MPI_Bcast(&stringSize,1,MPI_INT,0,PyMPI_COMM_INPUT)  );
      if ( stringSize < 0 ) {
         result = 0; /* Error of some sort */
      } else {
         result = (char*)malloc(stringSize+1);
         MPICHECK( PyMPI_COMM_INPUT,
                   MPI_Bcast(result,stringSize+1,MPI_CHAR,0,PyMPI_COMM_INPUT)  );
      }
   }
   return result;

 pythonError:
   if ( result ) free(result);
   return 0;
}

/**************************************************************************/
/* LOCAL  **************        communicator       ************************/
/************************************************************************ **/
/*  */
/**************************************************************************/
static PyObject* communicator(PyObject* self, PyObject* args) {
   long integerValue = 0;
   PyObject* result = 0;

   Assert(args);
   PYCHECK( PyArg_ParseTuple(args,"i",&integerValue) );
   PYCHECK( result = PyMPI_Comm((MPI_Comm)integerValue) );

   return result;
 pythonError:
   return 0;
}

/**************************************************************************/
/* LOCAL  **************          finalize         ************************/
/**************************************************************************/
/* Implements MPI_FINALIZE() -- See also lastwish()                       */
/**************************************************************************/
/*ARGSUSED*/
static PyObject* finalize(PyObject* pySelf, PyObject* args) {
   static int finalized = 0;
   /* ----------------------------------------------- */
   /* MPI better be in ready state                    */
   /* ----------------------------------------------- */
   NOARGUMENTS();
   RAISEIFNOMPI();

   /* ----------------------------------------------- */
   /* Don't call multiple times                       */
   /* ----------------------------------------------- */
   MPICHECKCOMMLESS( PyMPI_Finalized(&finalized) );
   if ( !finalized ) {
      Assert(PyMPI_finalizeMPI);
      MPICHECKCOMMLESS( PyMPI_finalizeMPI() ); /* Normally MPI_Finalize */
      PyMPI_IHaveFinalizedMPI();
   }
   
   Py_XINCREF(Py_None);
   return Py_None;

 pythonError:
   return 0;
}


/**************************************************************************/
/* LOCAL  **************         finalized         ************************/
/**************************************************************************/
/* Implements MPI_Finalized() (may use the builtin version)               */
/**************************************************************************/
/*ARGSUSED*/
static PyObject* finalized(PyObject* pySelf, PyObject* args) {
   int finalizedFlag = 0;
   PyObject* result = 0;

   /* ----------------------------------------------- */
   /* Does not need MPI to answer                     */
   /* ----------------------------------------------- */
   NOARGUMENTS();

   MPICHECKCOMMLESS( PyMPI_Finalized(&finalizedFlag) );
   PYCHECK( result = PyInt_FromLong(finalizedFlag) );
   return result;

 pythonError:
   return 0;
   
}

/**************************************************************************/
/* LOCAL  **************        initialized        ************************/
/************************************************************************ **/
/*  */
/**************************************************************************/
/*ARGSUSED*/
static PyObject* initialized(PyObject* pySelf, PyObject* args) {
   PyObject* result = 0;
   
   NOARGUMENTS();

   PYCHECK( result = PyInt_FromLong( mpiReady()) );
   return result;

 pythonError:
   return 0;
}

/**************************************************************************/
/* LOCAL  **************           wtick           ************************/
/************************************************************************ **/
/*  */
/**************************************************************************/
/*ARGSUSED*/
static PyObject* wtick(PyObject* pySelf, PyObject* args) {
   double theTick = 0.0;
   PyObject* result = 0;

   NOARGUMENTS();

   theTick = MPI_Wtick();
   PYCHECK( result = PyFloat_FromDouble(theTick) );
   return result;

 pythonError:
   return 0;
}

/**************************************************************************/
/* LOCAL  **************           wtime           ************************/
/**************************************************************************/
/* Implements MPI_Wtime() to get high fidelity system timer               */
/**************************************************************************/
/*ARGSUSED*/
static PyObject* wtime(PyObject* pySelf, PyObject* args) {
   double theTime = 0.0;
   PyObject* result = 0;

   NOARGUMENTS();

   theTime = MPI_Wtime();
   PYCHECK( result = PyFloat_FromDouble(theTime) );
   return result;

 pythonError:
   return 0;
}

/**************************************************************************/
/* GLOBAL **************          initmpi          ************************/
/************************************************************************ **/
/*  */
/**************************************************************************/
static PyMethodDef MPI_methods[] = {
   {"communicator",communicator,METH_VARARGS,"Build a communicator object from an established communicator handle\n  communicator(int)"},
   {"finalize",finalize,METH_VARARGS,"Turn off MPI.  It is called at shutdown unless already finalized\n  finalize()"},
   {"finalized",finalized,METH_VARARGS,"equivalent to MPI_Finalized() for MPICH, else best guess\n  finalized()"},
   {"initialized",initialized,METH_VARARGS,"equivalent to MPI_Initialized()\n  initialized()"},
   {"wtick",wtick,METH_VARARGS,"Use MPI_Wtick to get tick time of high resolution timer\n  See also tick\n  wtick()"},
   {"wtime",wtime,METH_VARARGS,"Use MPI_Wtime to get value of high resolution timer\n  See also deltaT()\n  wtime()"},
   {0,0}
};


/* #                                       #     #
   #          ##     ####    #####         #  #  #     #     ####   #    #
   #         #  #   #          #           #  #  #     #    #       #    #
   #        #    #   ####      #           #  #  #     #     ####   ######
   #        ######       #     #           #  #  #     #         #  #    #
   #        #    #  #    #     #           #  #  #     #    #    #  #    #
   #######  #    #   ####      #            ## ##      #     ####   #    # */

/**************************************************************************/
/* LOCAL  **************          lastwish         ************************/
/**************************************************************************/
/* This function is called when the system is shutdown.  It calls any     */
/* previous stub and then calls the finalize function (side effect is to  */
/* call MPI_Finalize() if it has not yet been called.                     */
/*                                                                        */
/* We ignore all errors since it is shutdown time                         */
/**************************************************************************/
static PyObject* lastwish(PyObject* self, PyObject* args) {
   PyObject* result = 0;

   /* ----------------------------------------------- */
   /* Call any previous last wish we saved            */
   /* ----------------------------------------------- */
   if ( sysExitfunc && PyCallable_Check(sysExitfunc) ) {
      result = PyObject_CallObject(sysExitfunc,0);
      Py_XDECREF(sysExitfunc);
      sysExitfunc = 0;
   } else {
      Py_XINCREF(Py_None);
      result =  Py_None;
   }
   PyErr_Clear();

   /* ----------------------------------------------- */
   /* Do the important work                           */
   /* ----------------------------------------------- */
   finalize(self,args);
   PyErr_Clear();

   return result;
}

/**************************************************************************/
/* LOCAL  **************      lastwishMethods      ************************/
/**************************************************************************/
/* Table used to initialized a lastwish function object                   */
/**************************************************************************/
static PyMethodDef lastwishMethods = {
   "lastwish",lastwish,METH_VARARGS,"Clean up MPI module"
};

/*--------------------------------------------------------------------------
* method:  initmpi
* Scope:   Global (called from patched main) 
* Purpose: Initialize mpi
*
* Notes: This method is the first thing called in Pymain, the reasons for this
* are as follows.
*
* 1) MPI_Init has issues if it is not called right away, before any file
* descriptors are modified in the process
* 2) MPI_Init usually cleans up the argument list which tends to trip up
* the getopt() loop in patchedmain.c on some systems
*
* Therefore, this method gets called BEFORE python actually gets intialized,
* hence we cannot use any python calls within it.
* ---------------------------------------------------------------------------*/
void initmpi(int* argc,char*** argv)
{
    int MPIisReady;
    int myRank = 0;

    /* ----------------------------------------------- */
    /* Assemble the argc and argv arrays               */
    /* and initialize MPI (if not already done)        */
    /* I have a stub here for alternate startup        */
    /* We use PETSC which must initialize MPI          */
    /* ----------------------------------------------- */
    PyAlternateMPIStartup(&initializeMPI,&PyMPI_finalizeMPI);
    if ( MPI_Initialized(&MPIisReady) != MPI_SUCCESS ) {
        fprintf(stderr,"MPI Failure, MPI_Initialized()\n");
        exit(1);
    }

    if(MPIisReady)
    {   
        printf("pyMPI: MPI already initialized, continuing\n");
    }else{

        /* call MPI_Init or alternate Startup function here! */

        /* (rwh) Have VTK do MPI_Init and init global controller ... */
        if ( !vtkSetup(argc, argv) )
        {
          if(initializeMPI(argc,argv) != MPI_SUCCESS)
          {
            fprintf(stderr,"MPI Failure, MPI_Init()\n");
            exit(1);
          }
        }

    }
    MPI_Comm_rank( MPI_COMM_WORLD, &myRank );
}


/************************************************************************* 
 * method: initpympi
 * This is called right after python has been initialized.  MPI has already
 * been initialized here 
 * ************************************************************************/
void initpympi() 
{
    PyObject* mpiName = 0;
    char versionString[32];
    PyObject* lastWish = 0;
    int version;
    int subversion;
    PyObject* pickleModule = 0;
    PyObject* pickleDict = 0;
    PyObject* docString = 0;
    PyObject* pyWorld = 0;
    PyObject* member = 0;
    PyMethodDef* methodPtr = 0;
    char* docExtra = 0;
    int myRank = 0;
    int result = MPI_Comm_rank(MPI_COMM_WORLD, &myRank );

    /* ----------------------------------------------- */
    /* The IBM poe environment is brain dead           */
    /* ----------------------------------------------- */
#ifdef _AIX
    Py_InteractiveFlag++;
#endif

    /* ----------------------------------------------- */
    /* Cover our butts on assumptions                  */
    /* ----------------------------------------------- */
    Assert( sizeof(MPI_Comm) <= sizeof(long) );

    /* ----------------------------------------------- */
    /* We subvert the input stream to handle broadcast */
    /* ----------------------------------------------- */
    Original_ReadlineFunctionPointer = PyOS_ReadlineFunctionPointer;
    if ( !Original_ReadlineFunctionPointer ) {
        Original_ReadlineFunctionPointer = PyOS_StdioReadline;
    }

    PyOS_ReadlineFunctionPointer = MPI_ReadlineFunctionPointer;

    /* ----------------------------------------------- */
    /* Setup the initial mpi module                    */
    /* ----------------------------------------------- */
    module = Py_InitModule("mpi",MPI_methods);
    Assert(module);
    PyMPI_dictionary = PyModule_GetDict(module);
    Assert(PyMPI_dictionary);

    /* ----------------------------------------------- */
    /* Set up a docstring for the mpi module itself    */
    /* ----------------------------------------------- */
    docExtra = DocStringFromMethods(MPI_methods,"mpi\n\nBasic mpi calls\n\n");
    Assert(docExtra);
    docString = PyString_FromString(docExtra);
    free(docExtra);

    /* ----------------------------------------------- */
    /* We start off with errors handled with flag      */
    /* ----------------------------------------------- */
    if ( MPI_Errhandler_set(MPI_COMM_WORLD,MPI_ERRORS_RETURN)
            != MPI_SUCCESS ) {
        PYCHECK( PyErr_SetString(PyExc_SystemError,"MPI Failure -- MPI_Errhandler_set()") );
    }

    /* ----------------------------------------------- */
    /* See if we conform!                              */
    /* ----------------------------------------------- */
    MPICHECKCOMMLESS( MPI_Get_version(&version,&subversion) );
    Assert(version == MPI_VERSION && subversion == MPI_SUBVERSION);

    /* ----------------------------------------------- */
    /* We have some cleanup work to do on exit         */
    /* ----------------------------------------------- */
    PYCHECK( lastWish = PyCFunction_New(&lastwishMethods,module) );
    Assert(lastWish);
    sysExitfunc = PySys_GetObject("exitfunc");
    PyErr_Clear();
    PYCHECK( PySys_SetObject("exitfunc",lastWish) );

    /* ----------------------------------------------- */
    /* Set common attributes                           */
    /* ----------------------------------------------- */
    PYCHECK( PyDict_SetItemString(PyMPI_dictionary,"stdout",Py_None) );
    Py_INCREF(Py_None);

    PYCHECK( PyString_ConcatFromString(&docString,"name: Name of MPI model (MPICH, LAM, mpi)") );
#ifdef MPICH_NAME
    PYCHECK( mpiName = PyString_FromString("MPICH") );
#else
# ifdef LAM_MPI
    PYCHECK( mpiName = PyString_FromString("LAM") );
# else
    PYCHECK( mpiName = PyString_FromString("mpi") );
# endif
#endif
    PYCHECK( PyDict_SetItemString(PyMPI_dictionary,"name",mpiName) );

    PYCHECK( PyString_ConcatFromString(&docString,"rank: Rank of MPI_COMM_WORLD communicator\n") );
    MPICHECK( MPI_COMM_WORLD,
            MPI_Comm_rank(MPI_COMM_WORLD,&worldRank));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"rank",
                PyInt_FromLong((long)worldRank)));

    PYCHECK(PyString_ConcatFromString(&docString,"procs: Size of MPI_COMM_WORLD communicator\n"));
    MPICHECK( MPI_COMM_WORLD,
            MPI_Comm_size(MPI_COMM_WORLD,&worldProcs));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"procs",
                PyInt_FromLong((long)worldProcs)));

    PYCHECK(PyString_ConcatFromString(&docString,"tick: Tick size of high-resolution timer\n"));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"tick",
                PyFloat_FromDouble(MPI_Wtick())));

    PYCHECK(PyString_ConcatFromString(&docString,"version: String showing mpi version\n"));
    sprintf(versionString,"%d.%d",MPI_VERSION,MPI_SUBVERSION);
#if defined(MPICH_NAME) && MPI_VERSION == 1 && MPI_SUBVERSION == 1 && MPI_STATUS_SIZE == 5
    strcat(versionString,".2"); /* MPICH 1.1.2 is evil */
#endif
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"version",
                PyString_FromString(versionString)));

    PYCHECK(PyString_ConcatFromString(&docString,"COMM_WORLD: MPI_COMM_WORLD communicator\n"));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"COMM_WORLD",
                PyMPI_Comm(MPI_COMM_WORLD)));

    PYCHECK(PyString_ConcatFromString(&docString,"COMM_NULL: MPI_COMM_NULL communicator (non-functional)\n"));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"COMM_NULL",
                PyMPI_Comm(MPI_COMM_NULL)));

    PYCHECK(PyString_ConcatFromString(&docString,"MAX: MPI_MAX\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MAX",
      PyInt_FromLong((long)MPI_MAX)));*/
    reduceOpLookup[eMaxOp] = MPI_MAX;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MAX",
                PyInt_FromLong((long)eMaxOp)));

    PYCHECK(PyString_ConcatFromString(&docString,"MIN: MPI_MIN\n"));

    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MIN",
      PyInt_FromLong((long)MPI_MIN)));*/
    reduceOpLookup[eMinOp] = MPI_MIN;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MIN",
                PyInt_FromLong((long)eMinOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"SUM: MPI_SUM\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"SUM",
      PyInt_FromLong((long)MPI_SUM)));*/
    reduceOpLookup[eSumOp] = MPI_SUM;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"SUM",
                PyInt_FromLong((long)eSumOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"PROD: MPI_PROD\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"PROD",
      PyInt_FromLong((long)MPI_PROD)));*/
    reduceOpLookup[eProdOp] = MPI_PROD;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"PROD",
                PyInt_FromLong((long)eProdOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"LAND: MPI_LAND\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LAND",
      PyInt_FromLong((long)MPI_LAND)));*/
    reduceOpLookup[eLandOp] = MPI_LAND;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LAND",
                PyInt_FromLong((long)eLandOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"BAND: MPI_BAND\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BAND",
      PyInt_FromLong((long)MPI_BAND)));*/
    reduceOpLookup[eBandOp] = MPI_BAND;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BAND",
                PyInt_FromLong((long)eBandOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"LOR: MPI_LOR\n"));
    /*PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LOR",
      PyInt_FromLong((long)MPI_LOR)));*/
    reduceOpLookup[eLorOp] = MPI_LOR;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LOR",
                PyInt_FromLong((long)eLorOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"BOR: MPI_BOR\n"));
    /*   PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BOR",
         PyInt_FromLong((long)MPI_BOR)));*/
    reduceOpLookup[eBorOp] = MPI_BOR;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BOR",
                PyInt_FromLong((long)eBorOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"LXOR: MPI_LXOR\n"));
    /*   PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LXOR",
         PyInt_FromLong((long)MPI_LXOR)));*/
    reduceOpLookup[eLxorOp] = MPI_LXOR;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"LXOR",
                PyInt_FromLong((long)eLxorOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"BXOR: MPI_BXOR\n"));
    /*   PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BXOR",
         PyInt_FromLong((long)MPI_BXOR)));*/
    reduceOpLookup[eBxorOp] = MPI_BXOR;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"BXOR",
                PyInt_FromLong((long)eBxorOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"MINLOC: MPI_MINLOC\n"));
    /*   PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MINLOC",
         PyInt_FromLong((long)MPI_MINLOC)));*/
    reduceOpLookup[eMinlocOp] = MPI_MINLOC;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MINLOC",
                PyInt_FromLong((long)eMinlocOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"MAXLOC: MPI_MAXLOC\n"));
    /*   PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MAXLOC",
         PyInt_FromLong((long)MPI_MAXLOC)));*/
    reduceOpLookup[eMaxlocOp] = MPI_MAXLOC;
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"MAXLOC",
                PyInt_FromLong((long)eMaxlocOp)));

    PYCHECK(   PyString_ConcatFromString(&docString,"ANY_SOURCE: MPI_ANY_SOURCE (used for untargeted recv)\n"));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"ANY_SOURCE",
                PyInt_FromLong((long)MPI_ANY_SOURCE)));

    PYCHECK(   PyString_ConcatFromString(&docString,"ANY_TAG: MPI_ANY_TAG (used for untargeted recv)\n"));
    PYCHECK(PyDict_SetItemString(PyMPI_dictionary,"ANY_TAG",
                PyInt_FromLong((long)MPI_ANY_TAG)));

    /* ----------------------------------------------- */
    /* We set up an internal communicator for PYTHON   */
    /* messaging and another for Python I/O            */
    /* ----------------------------------------------- */
    MPICHECK( MPI_COMM_WORLD,
            MPI_Comm_dup(MPI_COMM_WORLD,&PyMPI_COMM_WORLD));
    MPICHECK( MPI_COMM_WORLD,
            MPI_Comm_dup(MPI_COMM_WORLD,&PyMPI_COMM_INPUT));
    PYCHECK( PyString_ConcatFromString(&docString,"WORLD: Internal Python communicator\n") );
    PYCHECK( pyWorld = PyMPI_Comm(PyMPI_COMM_WORLD) );
    PYCHECK( PyDict_SetItemString(PyMPI_dictionary,"WORLD",pyWorld) );

    /* ----------------------------------------------- */
    /* Fetch member functions to appear as mpi.xxxx    */
    /* Make pyWorld immortal to avoid dealloc issues   */
    /* Magic Rating: 10/10                             */
    /* ----------------------------------------------- */
    Py_INCREF(pyWorld);
    for(methodPtr = PyMPIMethods_Comm; methodPtr->ml_name; ++methodPtr) {
        PYCHECK( member = PyObject_GetAttrString(pyWorld,methodPtr->ml_name) );
        Py_INCREF(member);
        PYCHECK( PyDict_SetItemString(PyMPI_dictionary,methodPtr->ml_name,member) );
    }

    /* ----------------------------------------------- */
    /* Set up the overloaded input                     */
    /* ----------------------------------------------- */
    PYCHECK( overloadedInput = PyMPI_File(worldRank != 0,PySys_GetObject("stdin"),PyMPI_COMM_INPUT) );
    Py_INCREF(overloadedInput);
    PyDict_SetItemString(PyMPI_dictionary,"stdin",overloadedInput);
    PySys_SetObject("stdin",overloadedInput);

    /* ----------------------------------------------- */
    /* Initial model is no output throttle             */
    /* ----------------------------------------------- */
    PYCHECK( PyMPI_UnrestrictedOutput(3) );

    /* ----------------------------------------------- */
    /* Have to set up some stuff for communicating     */
    /* arbitrary python objects                        */
    /* ----------------------------------------------- */

    /* -- set up PyMPI_pythonPickleType  -- */
    MPICHECKCOMMLESS( MPI_Type_contiguous(1,MPI_CHAR,&PyMPI_pythonPickleType) );
    MPICHECKCOMMLESS( MPI_Type_commit(&PyMPI_pythonPickleType) );
    Assert( PyMPI_pythonPickleType != MPI_CHAR );
    /* -- set up PyMPI_pythonFuncPickleType  -- */
    MPICHECKCOMMLESS( MPI_Type_contiguous(1,MPI_CHAR,&PyMPI_pythonFuncPickleType) );
    MPICHECKCOMMLESS( MPI_Type_commit(&PyMPI_pythonFuncPickleType) );
    Assert( PyMPI_pythonFuncPickleType != MPI_CHAR );

    /* -- set up PyMPI_pythonFuncPickleType  -- */
    pickleModule = PyImport_ImportModule("cPickle");
    if ( !pickleModule || PyErr_Occurred() ) {
        PyErr_Clear();
    } else {
        PYCHECK( pickleDict = PyModule_GetDict(pickleModule) );
        PYCHECK( PyMPI_pickleDumperFunction = PyDict_GetItemString(pickleDict,"dumps") );
        PYCHECK( PyMPI_pickleLoaderFunction = PyDict_GetItemString(pickleDict,"loads") );
    }

    /* ----------------------------------------------- */
    /* Set up the __doc__ string of the communicator   */
    /* type with more info (based on list)             */
    /* ----------------------------------------------- */
    PyMPIObject_Communicator_Type.tp_doc =
        DocStringFromMethods(PyMPIMethods_Comm,
                PyMPIObject_Communicator_Type.tp_doc);

    /* ----------------------------------------------- */
    /* Set up same info in module doc                  */
    /* ----------------------------------------------- */
    docExtra = 
        DocStringFromMethods(PyMPIMethods_Comm,
                "\nAnd these communicator methods map to the Python world communicator (not MPI_COMM_WORLD)\n\n");
    Assert(docExtra);
    PYCHECK( PyString_ConcatFromString(&docString,docExtra) );
    free(docExtra);

    /* ----------------------------------------------- */
    /* Stick in the doc string and we're ready to go   */
    /* ----------------------------------------------- */
    PYCHECK( PyDict_SetItemString(PyMPI_dictionary, "__doc__", docString) );

    return;

pythonError:
    Assert( PyErr_Occurred() );
    return; /* We have set a Python exception, let Python handle it */
}
