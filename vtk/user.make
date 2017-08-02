# this file can be used to override any of the values selected
# by configure in system.make.  At a minimum you should set
# the following Tcl/Tk values if you are planning to use Tcl/Tk

TCL_INCLUDE=-I/usr/packages/tcl8.3.0/generic
TCL_LIB=/usr/packages/tcl8.3.0/unix/libtcl8.3.so

TK_INCLUDE=-I/usr/packages/tk8.3.0/generic
TK_LIB=/usr/packages/tk8.3.0/unix/libtk8.3.so

MESA_INCLUDE=-I/usr/packages/Mesa-3.1/include
#MESA_LIB=/home/martink/storage/Mesa-1.2.6/lib-sun4-solaris/libMesaGL.a
#MESA_LIB=/usr/lib/libGL.so.1 /usr/packages/Mesa-3.1/src/OSmesa/libMesaOS.la
MESA_LIB=/usr/lib/libGL.so.1 /usr/packages/Mesa-3.1/src/OSmesa/osmesa.lo

# for python you must set this 
PYTHON_INCLUDES=-I/usr/packages/Python-1.5.2/Include -I/usr/packages/Python-1.5.2

# Add additional CFLAGS and CXXFLAGS for compilation
# uncomment the following two lines to set your own flags
#USER_CFLAGS =  
#USER_CXXFLAGS = 

# if you want to try the java support you'll need to set the following
# variables to match your environment and uncomment them
#
JDKHOME=/usr/packages/jdk1.2.2
JAVAC=${JDKHOME}/bin/javac
#JAVA_CLASS_HOME=${JDKHOME}
JAVA_CLASS_HOME=/home/heiland/vtk/java/vtk
JAVAH=${JDKHOME}/bin/javah
JAVA_INCLUDES=-I${JDKHOME}/include -I${JDKHOME}/include/linux
#JAVA_CXX_LIB=/common/software/g++-2.7.1/sun4/5.4/lib/libiberty.a /common/software/g++-2.7.1/sun4/5.4/lib/libstdc++.a /common/software/g++-2.7.1/sun4/5.4/lib/gcc-lib/sparc-sun-solaris2.4/2.7.1/libgcc.a
