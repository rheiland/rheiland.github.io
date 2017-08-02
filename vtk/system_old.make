VTK_OBJ       = /home/heiland/vtk

RANLIB        = :
CC            = /usr/bin/cc
CFLAGS        = -fPIC  \
                 -D_HP_NO_FAST_MACROS \
		-DHAVE_LIMITS_H	-DHAVE_UNISTD_H 

CXX           = /usr/bin/c++
CXXFLAGS      = -fPIC  \
                  \
		-D_HP_NO_FAST_MACROS -DHAVE_LIMITS_H -DHAVE_UNISTD_H

USER_CFLAGS   = -g -O2
USER_CXXFLAGS = -g -O2

X_EXTRA_LIBS  = 
X_PRE_LIBS    =  -lSM -lICE
XLIBS         =  -L/usr/X11R6/lib
prefix        = /usr/local
exec_prefix   = ${prefix}
LIB_RUNTIME_DIR = ${prefix}/lib

BUILD_TCL     = build_tcl
CLEAN_TCL     = clean_tcl
BUILD_JAVA    = build_java
CLEAN_JAVA    = clean_java
BUILD_PYTHON    = build_python
CLEAN_PYTHON    = clean_python

USE_GRAPHICS_LIBS   = -L${VTK_OBJ}/graphics -lVTKGraphicsTcl -lVTKGraphics
USE_IMAGING_LIBS    = -L${VTK_OBJ}/imaging -lVTKImagingTcl -lVTKImaging
USE_PATENTED_LIBS   = -L${VTK_OBJ}/patented -lVTKPatentedTcl -lVTKPatented
USE_CONTRIB_LIBS    = -L${VTK_OBJ}/contrib -lVTKContribTcl -lVTKContrib 
USE_LOCAL_LIBS      = 

USE_GRAPHICS_PYTHON   = -L${VTK_OBJ}/graphics -lVTKGraphicsPython 
USE_IMAGING_PYTHON    = -L${VTK_OBJ}/imaging -lVTKImagingPython
USE_PATENTED_PYTHON   = -L${VTK_OBJ}/patented -lVTKPatentedPython
USE_CONTRIB_PYTHON    = -L${VTK_OBJ}/contrib -lVTKContribPython 
USE_LOCAL_PYTHON      = 

USE_GRAPHICS_JAVA   = -L${VTK_OBJ}/graphics -lVTKGraphicsJava -lVTKGraphics
USE_IMAGING_JAVA    = -L${VTK_OBJ}/imaging -lVTKImagingJava -lVTKImaging
USE_PATENTED_JAVA   = -L${VTK_OBJ}/patented -lVTKPatentedJava -lVTKPatented
USE_CONTRIB_JAVA    = -L${VTK_OBJ}/contrib -lVTKContribJava -lVTKContrib 
USE_LOCAL_JAVA      = 

USE_TOOLKIT_FLAGS    =  -I${srcdir}/../graphics -DVTK_USE_GRAPHICS -I${srcdir}/../imaging -DVTK_USE_IMAGING -I${srcdir}/../patented -DVTK_USE_PATENTED -I${srcdir}/../contrib -DVTK_USE_CONTRIB 
TOOLKIT_DEPENDS      = 

VTK_TCL_SHLIB_TARGET = vtktcl
VTK_SHLIB_BUILD_FLAGS = -shared
VTK_SHLIB_LINK_FLAGS = -rdynamic
VTK_LIB_EXT          = .so
DL_LIBS              = -ldl
SHLIB_LD_LIBS        = 
SHLIB_SUFFIX         = .so

THREAD_LIBS          = 

GRAPHICS_API_OBJ     =  ${MESA_OBJ}
GRAPHICS_API_FLAGS   =  ${MESA_INCLUDE} -DVTK_USE_MESA   -I/usr/X11R6/include
GRAPHICS_API_LIBS    =  -L/usr/X11R6/lib ${MESA_LIB}

CONTROLLER_API_OBJ     = 
CONTROLLER_API_FLAGS   = 
CONTROLLER_API_LIBS    = 



# install support
#
# The following definition can be set to non-null for special systems
# like AFS with replication.  It allows the pathnames used for installation
# to be different than those used for actually reference files at
# run-time.  INSTALL_ROOT is prepended to $prefix and $exec_prefix
# when installing files.
INSTALL_ROOT    =
INSTALL         = /usr/bin/install -c
LIB_INSTALL_DIR = $(INSTALL_ROOT)$(exec_prefix)/lib
BIN_INSTALL_DIR = $(INSTALL_ROOT)$(exec_prefix)/bin

