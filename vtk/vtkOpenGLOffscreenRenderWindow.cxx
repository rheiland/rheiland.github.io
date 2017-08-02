/*=========================================================================

  Program:   Visualization Toolkit
  Module:    $RCSfile: vtkOpenGLOffscreenRenderWindow.cxx,v $
  Language:  C++
  Date:      $Date: 1999/04/19 23:11:55 $
  Version:   $Revision: 0.9 $

Copyright (c) 1993-1999 Ken Martin, Will Schroeder, Bill Lorensen.

This software is copyrighted by Ken Martin, Will Schroeder and Bill Lorensen.
The following terms apply to all files associated with the software unless
explicitly disclaimed in individual files. This copyright specifically does
not apply to the related textbook "The Visualization Toolkit" ISBN
013199837-4 published by Prentice Hall which is covered by its own copyright.

The authors hereby grant permission to use, copy, and distribute this
software and its documentation for any purpose, provided that existing
copyright notices are retained in all copies and that this notice is included
verbatim in any distributions. Additionally, the authors grant permission to
modify this software and its documentation for any purpose, provided that
such modifications are not distributed without the explicit consent of the
authors and that existing copyright notices are retained in all copies. Some
of the algorithms implemented by this software are patented, observe all
applicable patent law.

IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY FOR
DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY DERIVATIVES THEREOF,
EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE, AND NON-INFRINGEMENT.  THIS SOFTWARE IS PROVIDED ON AN
"AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE NO OBLIGATION TO PROVIDE
MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.


=========================================================================*/
// .NAME vtkOpenGLOffscreenRenderWindow - Render OpenGL scene offscreen.
// .SECTION Description
// Renders the entire 3D scene without need of an on-screen window.  
// This is very useful for client-server visualization. 
// .SECTION Caveats
//  There are two ways of doing this.  The most generic method is to 
//  render to an offscreen XPixmap and copy the pixels back to the 
//  client application.  While this implementation completely conforms
//  to the GLX standard, it forces the rendering to occur in software.
//  The SGI GLXPbuffer extension can be used to take advantage of
//  any available hardware graphics acceleration on the client side.
//  However it is very sgi-specific and there is no guarantee that
//  you will be able to find a properly matching visual type (this
//  is my fault because the matching is pretty rudimentary right now).
// 
//  Unfortunately these two modes of operation must be selected at 
//  compilation time.  Use Pbuffers by defining USE_PBUFFER.
//  Also some debugging information could not use the offDebugMacro()
//  so you must #define DEBUG_OFFSCREEN in order to turn on verbose
//  debugging.
//
// .SECTION see also
// vtkPBufferRenderWindow, vtkOpenGLRenderWindow, vtkWin32OffscreenRenderWindow

#include <stdlib.h>
#include <math.h>
#include <iostream.h>
#include "vtkOpenGLOffscreenRenderWindow.h"
#include "vtkOpenGLRenderer.h"
#include "vtkOpenGLProperty.h"
#include "vtkOpenGLTexture.h"
#include "vtkOpenGLCamera.h"
#include "vtkOpenGLLight.h"
#include "vtkOpenGLActor.h"
#include "vtkOpenGLPolyDataMapper.h"
#ifndef VTK_IMPLEMENT_MESA_CXX
#include "GL/gl.h"
#include "GL/glu.h"
#endif
#include "vtkObjectFactory.h"

#include <sys/types.h>
#include <time.h>


#define MAX_LIGHTS 8

#undef USE_PBUFFER

#define USE_JPEG

//#define DEBUG_OFFSCREEN
#ifdef DEBUG_OFFSCREEN
#define offDebugMacro(x) cerr x
#else
#define offDebugMacro(x) // nil
#endif

#define offErrorMacro(x) cerr x


#include <unistd.h>
#include <sys/time.h>
double getTime(void)
{
  static timeval tp;
  static int     initialized = 0;
  static double  startTime;

  if(!initialized) 
  {
    initialized = 1;    
    gettimeofday(&tp, NULL);
    startTime = tp.tv_sec + tp.tv_usec/1000000.0;
    return(0.0);  
  }
  gettimeofday(&tp, NULL);
  return((tp.tv_sec+tp.tv_usec/1000000.0)-startTime);
}

//------------------------------------------------------------------------------
vtkOpenGLOffscreenRenderWindow* vtkOpenGLOffscreenRenderWindow::New()
{
  // First try to create the object from the vtkObjectFactory
  vtkObject* ret = vtkObjectFactory::CreateInstance("vtkOpenGLOffscreenRenderWindow");
  if(ret)
    {
    cout << "vtkOpenGLOffscreenRenderWindow::New used vtkObjectFactory OK" << endl;
    return (vtkOpenGLOffscreenRenderWindow*)ret;
    }
  // If the factory was unable to create the object, then create it here.
  cout << "vtkOpenGLOffscreenRenderWindow::New  --- NOT using factory" << endl;
  return new vtkOpenGLOffscreenRenderWindow;
}


//----------------------------------------------------------------
#ifdef notdef
void vtkOpenGLOffscreenRenderWindow::MakeCurrent()
{
  Bool retval;
  offDebugMacro(<< "DEBUG: vtkOpenGLOffscreenRenderWindow::MakeCurrent\n");

  cout<<"  ==========================="<< endl;
  cout<<"  (MakeCurrent)this->DisplayId = "<< this->DisplayId <<endl;
  cout<<"  (MakeCurrent)this->WindowId = "<< this->WindowId <<endl;
  cout<<"  (MakeCurrent)this->ContextId = "<< this->ContextId <<endl;
  cout<<"  ==========================="<< endl;

  // set the current window 
  retval = glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

  if (!retval) {
    cout<<"vtkOpenGLOffscreenRenderWindow::MakeCurrent: glXMakeCurrent is FALSE"<<endl;
  }
  else {
    cout<<"vtkOpenGLOffscreenRenderWindow::MakeCurrent: glXMakeCurrent is TRUE"<<endl;
  }
}
#endif

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::WriteImage(char *filename)
{
  //XImage *img = this->GetImage(); 
  offDebugMacro(<< "DEBUG:  vtkOpenGLOffscreenRenderWindow::WriteImage\n");  
  int width = ((this->Size[0] > 0) ? this->Size[0] : 300);
  int height = ((this->Size[1] > 0) ? this->Size[1] : 300);
  offDebugMacro(<< "\tSize is " << width << ':' << height << "\n" );  
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId); 
  glFlush();

#ifdef USE_PBUFFER
  unsigned int *pixelbuffer = new unsigned int[width*height];
  offDebugMacro(<< "\nRead Pixels\n");  
  glReadPixels(0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,pixelbuffer);
  WritePPMPbuffer(filename,width,height,pixelbuffer);
  delete pixelbuffer;
  puts("done");

#else
  XFlush(this->DisplayId);
  offDebugMacro(<< "\nRead Pixels\n");  
  XImage *img = XGetImage(this->DisplayId,
			  this->pixmap,
			  0,0,
			  width,height,
			  AllPlanes,
			  XYPixmap);
  WritePPMXImage(filename,img);
  XDestroyImage(img);
#endif
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::WritePPMPbuffer(char *filename,
					 int width,int height,
					 unsigned int *img)
{
  FILE *ppmFile;
  register int x,y;
  register short bindex;
  char bigbuffer[2048*3];
  // unsigned int *img=(unsigned int*)pbuffer;
  int idx;
  /* Attempt to open file */
  if (!(ppmFile = fopen(filename, "w"))){
    offErrorMacro(<< "vtkOpenGLOffscreenRenderWindow::WritePPMPbuffer Could not open file " << filename << "\n" );  
    return;
  }
  
  offDebugMacro(<< "opened " << filename << " for writing\n" );
  
  fprintf(ppmFile,"P6\n"); /* define as a PPM file */
  fprintf(ppmFile,"%d %d\n",width,height); /* width and height */
  fprintf(ppmFile,"255\n"); /* the maxval field */
  for(x=0,idx=0,bindex=0;x<width;x++){
    for(y=0;y<height;y++){
      unsigned int pixel = img[idx++];
#define PB_ALPHAPIXEL(p) (p & 0xFF)
#define PB_BLUEPIXEL(p) ((p>>8) & 0xFF)
#define PB_GREENPIXEL(p) ((p>>16) & 0xFF)
#define PB_REDPIXEL(p) ((p>>24) & 0xff)
      bigbuffer[bindex++] = PB_REDPIXEL(pixel);
      bigbuffer[bindex++] = PB_GREENPIXEL(pixel);
      bigbuffer[bindex++] = PB_BLUEPIXEL(pixel);
      /* idx++; */
      if(!(bindex%=sizeof(bigbuffer)))
	fwrite(bigbuffer,1,sizeof(bigbuffer),ppmFile);  /* hairy modulo buffering scheme 
							   lowers opsys call overhead */
    }
  }
  fwrite(bigbuffer,1,bindex,ppmFile); /* get the rest dumped */
  fclose(ppmFile);
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::WritePPMXImage(char *filename,XImage *img)
{
  FILE *ppmFile;
  register int x,y;
  register short bindex;
  unsigned char bigbuffer[3*2048];

  /* Attempt to open file */
  if (!(ppmFile = fopen(filename, "w"))){
    offErrorMacro(<< "writePPM: Can't open data file " << filename << "\n" );
    return;
  }
  
  offDebugMacro( << "opened " << filename << " for writing\n\tWidth=" << img->width << " Height=" << img->height << "\n" );
  
  fprintf(ppmFile,"P6\n"); /* define as a PPM file */
  fprintf(ppmFile,"%d %d\n",img->width,img->height); /* width and height */
  fprintf(ppmFile,"255\n"); /* the maxval field */
  offDebugMacro(<< "StartDump\n");
  for(y=0,bindex=0;y<img->height;y++){
    for(x=0;x<img->width;x++){
      unsigned long pixel = XGetPixel(img,x,img->height-y);
#define REDPIXEL(p) (p & 0xFF)
#define BLUEPIXEL(p) ((p>>8) & 0xFF)
#define GREENPIXEL(p) ((p>>16) & 0xFF)
#define ALPHAPIXEL(p) ((p>>24) & 0xff)
      bigbuffer[bindex++] = REDPIXEL(pixel);
      bigbuffer[bindex++] = GREENPIXEL(pixel);
      bigbuffer[bindex++] = BLUEPIXEL(pixel);
      /* idx++; */
      if(!(bindex%=sizeof(bigbuffer))){
	fwrite(bigbuffer,1,sizeof(bigbuffer),ppmFile);  /* hairy modulo buffering scheme 
							   lowers opsys call overhead */
	// printf("Dump[%u:%u] %u bytes\n",x,y,sizeof(bigbuffer));
      }
    }
  }
  if(bindex>0)
    fwrite(bigbuffer,1,bindex,ppmFile); /* get the rest dumped */
  fclose(ppmFile);
}


#ifdef USE_JPEG

extern "C"
{
  int openJPEGFile(char *);
  int updateJPEGFile(int,int,int,int,int,unsigned char *);
  unsigned char *writeJPEGMem( int xdim, int ydim, int cdim,
      int quality, unsigned char *img, int *size );
}

//----------------------------------------------------------------
int vtkOpenGLOffscreenRenderWindow::WriteJPEGFile(char *filename, int quality)
{
  offDebugMacro(<< " vtkOpenGLOffscreenRenderWindow::WriteJPEGFile\n");  
  int width = this->Size[0];
  int height = this->Size[1];
  offDebugMacro(<< "\tSize is " << width << ':' << height << "\n" );  
  unsigned char *rgbBuffer = this->GetPixelData(0,0,width-1,height-1,1);

  int fd = openJPEGFile(filename);
  if( fd == NULL)  {
    cout << "ERROR opening jpeg file" <<endl;
    return -1;
  }

  if (updateJPEGFile( fd, width, height, 3, quality, rgbBuffer ) == -1 )
    cout << "ERROR updateJPEGFile" <<endl;
  else
    cout << "updateJPEGFile success" <<endl;

  return 0;
}

//----------------------------------------------------------------
unsigned char* vtkOpenGLOffscreenRenderWindow::WriteJPEGMem(int quality, 
         int *size)
{
  unsigned char *jpegImgOut;

  offDebugMacro(<< " vtkOpenGLOffscreenRenderWindow::WriteJPEGMem\n");  
  int width = this->Size[0];
  int height = this->Size[1];
  offDebugMacro(<< "\tSize is " << width << ':' << height << "\n" );  
  unsigned char *rgbBuffer = this->GetPixelData(0,0,width-1,height-1,1);

  // Need some error checking here...
  jpegImgOut = writeJPEGMem( width, height, 3, quality, rgbBuffer, size );

  return jpegImgOut;
}
#endif


//----------------------------------------------------------------
XVisualInfo *vtkOpenGLOffscreenRenderWindow::GetDesiredVisualInfo()
{
  cout << " --- GetDesiredVisualInfo" << endl;

  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetDesiredVisualInfo\n");

  int attributeList[] = { GLX_RGBA, None };
  return glXChooseVisual(this->DisplayId,
			 DefaultScreen(this->DisplayId),attributeList);
}

//----------------------------------------------------------------
// Constructor
vtkOpenGLOffscreenRenderWindow::vtkOpenGLOffscreenRenderWindow()
{
#ifdef USE_PBUFFER
  cout << "vtkOpenGLOffscreenRenderWindow (constructor): using PBuffers..." << endl;
#else
  cout << "vtkOpenGLOffscreenRenderWindow (constructor): NOT using PBuffers - test..." << endl;
#endif

  offDebugMacro(<< "DEBUG: vtkOpenGLOffscreenRenderWindow::vtkOpenGLOffscreenRenderWindow\n");

  this->ContextId = NULL;
  this->MultiSamples = 8;
  this->DisplayId = (Display *)NULL;
  this->WindowId = (Window)NULL;
  this->NextWindowId = (Window)NULL;
  this->ColorMap = (Colormap)0;

  if ( this->WindowName ) {
    offDebugMacro(<< "DEBUG: pre delete\n");
    delete [] this->WindowName;
    offDebugMacro(<< "DEBUG: post delete\n");
  }
  this->WindowName = new char[strlen("Visualization Toolkit - OpenGL")+1];
  strcpy( this->WindowName, "Visualization Toolkit - OpenGL" );
}

//----------------------------------------------------------------
// Description:
// free up memory & close the window
vtkOpenGLOffscreenRenderWindow::~vtkOpenGLOffscreenRenderWindow()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow:  destructor...\n");

  /* first delete all the old lights */
  // make sure we have been initialized 

#ifdef notdef  // rwh - don't do "Pbuffer" anything  
  if (this->ContextId) {

    // disable all the lights
    for (short cur_light = GL_LIGHT0;
         cur_light < GL_LIGHT0+MAX_LIGHTS;
         cur_light++)
      glDisable((GLenum)cur_light);
    glXDestroyContext( this->DisplayId, this->ContextId);
    glXDestroyGLXPbufferSGIX(this->DisplayId, this->WindowId);
  }
#endif


  if(this->ContextId) { // window exists
    Destroy();
    WindowInitialize();
  }
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::Destroy()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow:  Destroy()...\n");

  if (this->ContextId) {
    glXDestroyContext( this->DisplayId, this->ContextId);
#ifdef USE_PBUFFER
    glXDestroyGLXPbufferSGIX(this->DisplayId, this->WindowId);
#else
    glXDestroyGLXPixmap(this->DisplayId,this->WindowId);
    XFreePixmap(this->DisplayId,this->pixmap);
    this->pixmap=0;
#endif
    this->WindowId=0; this->ContextId=0;
  }
}

//----------------------------------------------------------------
// Description:
// Begin the rendering process.
void vtkOpenGLOffscreenRenderWindow::Start(void)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::Start\n");

  // if the renderer has not been initialized, do so now
  if (!this->ContextId)
    {
      this->Initialize();
    }

  // set the current window 
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);
}

//----------------------------------------------------------------
// Description:
// End the rendering process and display the image.
void vtkOpenGLOffscreenRenderWindow::Frame(void)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::Frame\n");

  glFlush();
  if (!this->AbortRender && this->DoubleBuffer&&this->SwapBuffers)
    {
      offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::Frame swapbuffers\n");

      //glXSwapBuffers(this->DisplayId, this->WindowId);
      offDebugMacro(<< " glXSwapBuffers\n");
    }
}
 
//----------------------------------------------------------------
// Description:
// Update system if needed due to stereo rendering.
// STEREO RENDERING CURRENTLY NOT SUPPORTED
void vtkOpenGLOffscreenRenderWindow::StereoUpdate(void)
{
  return; // JMS: There is no stereo.  Now go away...
}

//----------------------------------------------------------------
// Description:
// Specify various window parameters.
void vtkOpenGLOffscreenRenderWindow::WindowConfigure()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::WindowConfigure\n");

  // this is all handled by the desiredVisualInfo method
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::QueryPbuffer(Display *dpy,GLXPbufferSGIX pbuf)
{
  unsigned int value;
  /* GLX_WIDTH_SGIX, GLX_HEIGHT_SGIX, GLX_LARGEST_PBUFFER_SGIX */
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow.cxx : QueryPbuffer() glXQueryGLXPbufferSGIX() Info\n");
  glXQueryGLXPbufferSGIX(dpy,pbuf,GLX_WIDTH_SGIX,&value);
  offDebugMacro(<< "\tpbuffer width   = " << value <<" \n");
  glXQueryGLXPbufferSGIX(dpy,pbuf,GLX_HEIGHT_SGIX,&value);
  offDebugMacro(<< "\tpbuffer height  = " << value << "\n");
  glXQueryGLXPbufferSGIX(dpy,pbuf,GLX_LARGEST_PBUFFER_SGIX,&value);
  offDebugMacro(<< "\tpbuffer largest = " << value << "\n");
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::QueryConfig(Display *dpy, GLXFBConfigSGIX config)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::QueryConfig() ... \n");

  int value;
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_BUFFER_SIZE
			   ,&value );
  offDebugMacro(<< "\tbuffersize(bits per cbuffer)=" << value << "\n");
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_LEVEL
			   ,&value );
  offDebugMacro(<< "\tOverlay buffer (0 is main buffer)=" << value << "\n");
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_RED_SIZE
			   ,&value );
  offDebugMacro(<< "\t\tRedsize=" << value << " : ");
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_BLUE_SIZE
			   ,&value );
  offDebugMacro(<< "Bluesize=" << value << " : ");
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_GREEN_SIZE
			   ,&value );
  offDebugMacro(<< "Greensize=" << value << " : ");
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_ALPHA_SIZE
			   ,&value );
  offDebugMacro(<< "Alphasize=" << value << "\n");
  
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_DEPTH_SIZE
			   ,&value );
  offDebugMacro(<< "\tDepth buffer size="<< value << "\n");
  
  
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_VISUAL_CAVEAT_EXT
			   ,&value );

  switch(value){
  case GLX_NONE_EXT:
    offDebugMacro(<< "\tNo Caveats\n");
    break;
  case GLX_SLOW_VISUAL_EXT:
    offDebugMacro(<< "\tSlow Visual\n");
    break;
    /* case GLX_NON_CONFORMANT_EXT:
       offDebugMacro(<< "\tNon_Conformant visual");
       break;*/
  default:
    offDebugMacro(<< "\tUnknown Caveat " << value << "\n");
    break;
  }
  glXGetFBConfigAttribSGIX(dpy,config,
			   GLX_RENDER_TYPE_SGIX
			   ,&value );
  if(value==GLX_RGBA_BIT_SGIX)
    offDebugMacro(<< "\tGLX_RGBA_BIT_SGIX\n");

  /*
    else if(value==GLX_COLOR_INDEX_SGIX)
    offDebugMacro(<< "\tGLX_COLOR_INDEX_SGIX"); */

  else offDebugMacro(<< "\tunknown (color index vs. rgba bit) " << value << "\n");
}

//----------------------------------------------------------------
// Description:
// Initialize the window for rendering.

void vtkOpenGLOffscreenRenderWindow::WindowInitialize (void)
{
  cout << " --- WindowInitialize" << endl;

  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::WindowInitialize() ... \n");

  XVisualInfo  *v;

  int width = ((this->Size[0] > 0) ? this->Size[0] : 300);
  int height = ((this->Size[1] > 0) ? this->Size[1] : 300);
  this->Size[0]=width;
  this->Size[1]=height;
  // this->SetSize(width,height);

  // get the default display connection 
  if (!this->DisplayId)
    {
      this->DisplayId = XOpenDisplay((char *)NULL); 
      if (this->DisplayId == NULL) 
	{
	  vtkErrorMacro(<< "bad X server connection.\n");
	}
    }
  // if(this->ContextId) return; // don't do a cotton pickin thing!
  // get visual info and set up pixmap buffer
  // v = this->GetDesiredVisualInfo();


//---------------------------
//  int attributeList[] = { GLX_RGBA, None };
//rwh:  hardcode depth (Ack)

// Note: depthValue=24 works for tetons, but not for cassatt.
//                 =23 works for both.

  int depthValue = 23;
  int attributeList[] = { GLX_RGBA, GLX_DEPTH_SIZE, depthValue, None };
//  printf("glxChooseVis DPY=%u SCRN=%u \n",(unsigned int)(this->DisplayId),DefaultScreen(this->DisplayId));
  printf("glXChooseVisual DPY=%d SCRN=%d \n",this->DisplayId, DefaultScreen(this->DisplayId));

  v = glXChooseVisual(this->DisplayId,
		      DefaultScreen(this->DisplayId),attributeList);

  //this->ContextId = glXCreateContext(dpy,vi,0,GL_FALSE);
  /* this->WindowId = CreateOffscreenPixmap(dpy,vi,&pixmap,width,height); */
  


  /* create offscreen pixmap to render to (same depth as RootThis->Window of dpy) */
  this->pixmap = XCreatePixmap(this->DisplayId,
			       RootWindow(this->DisplayId,v->screen),
			       width,
			       height,
			       v->depth);
  this->ContextId = glXCreateContext(this->DisplayId,v,0,GL_FALSE);

  /*  make gl understand it as a window */
  this->WindowId = glXCreateGLXPixmap(this->DisplayId,v,this->pixmap); 

  /* this->ColorMap = XCreateColormap(this->DisplayId,
     RootWindow( this->DisplayId, v->screen),
     v->visual, AllocNone );*/

  /*this->ContextId = glXCreateContext(this->DisplayId, v, 0, GL_TRUE);
    this->pixmap = XCreatePixmap(this->DisplayId,
    RootWindow(this->DisplayId,v->screen),
    width,height,
    v->depth); */

  //this->WindowId = glXCreateGLXPixmap(this->DisplayId, v, this->pixmap);


//rwh
/*
  cout<<"  ==========================="<< endl;
  cout<<"  (WindowInitialize)this->DisplayId = "<< this->DisplayId <<endl;
  cout<<"  (WindowInitialize)this->WindowId = "<< this->WindowId <<endl;
  cout<<"  (WindowInitialize)this->ContextId = "<< this->ContextId <<endl;
  cout<<"  ==========================="<< endl;
*/
  
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

  // initialize GL state
  //glMatrixMode( GL_MODELVIEW );
  //glDepthFunc( GL_LEQUAL );
  //glEnable( GL_DEPTH_TEST );
  //glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
  //glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

  // Paul!
  //glEnable(GL_BLEND);
  //glEnable( GL_NORMALIZE );
  //glAlphaFunc(GL_GREATER,0);
  offDebugMacro(<< " glMatrixMode ModelView\n");
  glMatrixMode( GL_MODELVIEW );
  offDebugMacro(<< " zbuffer enabled\n");
  glDepthFunc( GL_LEQUAL );
  glEnable( GL_DEPTH_TEST );

  offDebugMacro(<< " texture stuff\n");
  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );

  // initialize blending for transparency
  offDebugMacro(<< " blend func stuff\n");
  glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
  glEnable(GL_BLEND);
  glEnable( GL_NORMALIZE );
  glAlphaFunc(GL_GREATER,0);
  
  this->Mapped = 0; // if its mapped, then it trys windowgetattributes which fails!
  this->SwapBuffers = 0;
  this->DoubleBuffer = 0;

  // free the visual info
  if (v)
    {
      XFree(v);
    }
  cout << " --- leaving WindowInitialize" << endl;
}

//----------------------------------------------------------------
// Description:
// Initialize the rendering window.
void vtkOpenGLOffscreenRenderWindow::Initialize (void)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::Initialize\n");

  // make sure we havent already been initialized 
  if (this->ContextId)
    return;

  // now initialize the window 
  this->WindowInitialize();
}

//----------------------------------------------------------------
// Description:
// Change the window to fill the entire screen.
void vtkOpenGLOffscreenRenderWindow::SetFullScreen(int arg)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetFullScreen\n");
  PrefFullScreen(); // Danger McFly!!
  return;
}

//----------------------------------------------------------------
// Description:
// Set the preferred window size to full screen.
void vtkOpenGLOffscreenRenderWindow::PrefFullScreen()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::PrefFullScreen\n");

  int *size = this->GetScreenSize();
  this->Position[0] = 0;
  this->Position[1] = 0;
  this->Size[0] = size[0];
  this->Size[1] = size[1];
  this->Borders = 0;
  return;
}

//----------------------------------------------------------------
// Description:
// Resize the window.
void vtkOpenGLOffscreenRenderWindow::WindowRemap()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::WindowRemap\n");

  short cur_light;

  /* first delete all the old lights */
  for (cur_light = GL_LIGHT0; cur_light < GL_LIGHT0+MAX_LIGHTS; cur_light++)
    {
      glDisable((GLenum)cur_light);
    }
  
  glXDestroyContext( this->DisplayId, this->ContextId);
  // then close the old window 
  if (this->OwnWindow)
    {
      XDestroyWindow(this->DisplayId,this->WindowId);
    }
  
  // set the default windowid 
  this->WindowId = this->NextWindowId;
  this->NextWindowId = (Window)NULL;

  // configure the window 
  this->WindowInitialize();
}
#ifdef notdef
//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::SetPosition(int p[2])
{
  this->SetPosition(p[0],p[1]);
}
//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::SetPosition(int x,int y)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetPosition\n");
  this->Position[0]=x;
  this->Position[1]=y;
  // JMS:  but there is nothing to remap here... 
  // just preventing some other parent class from doing that.
}
#endif

//----------------------------------------------------------------
// Description:
// Specify the size of the rendering window.
void vtkOpenGLOffscreenRenderWindow::SetSize(int x,int y)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetSize\n");
  if ((this->Size[0] != x)||(this->Size[1] != y)){
    this->Modified();
    this->Size[0] = x;
    this->Size[1] = y;
  }
  cout << "  (2)" << endl;
  if(this->ContextId) { // window exists
  cout << "  (3)" << endl;
    Destroy();
  cout << "  (4)" << endl;
    WindowInitialize();
  cout << "  (5)" << endl;
  }
  //JMS: need to figure out how to resize this
  // well, maybe not just yet...  Gotta fix the resizing
  //XResizeWindow(this->DisplayId,this->WindowId,x,y);
  //XSync(this->DisplayId,False);
  cout << "  leaving SetSize " << endl;
}

//----------------------------------------------------------------
int *vtkOpenGLOffscreenRenderWindow::GetSize()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetSize() " << Size[0] << ":" << Size[1] << "\n");
  return this->Size;
}

//----------------------------------------------------------------
int vtkOpenGLOffscreenRenderWindow::GetDesiredDepth()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetDesiredDepth\n");
  XVisualInfo *v;
  // get the default visual to use 
  v = this->GetDesiredVisualInfo();
  return v->depth;  
}

//----------------------------------------------------------------
// Description:
// Get a visual from the windowing system.
Visual *vtkOpenGLOffscreenRenderWindow::GetDesiredVisual ()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetDesiredVisual\n");
  XVisualInfo *v;
  // get the default visual to use 
  v = this->GetDesiredVisualInfo();
  return v->visual;  
}

//----------------------------------------------------------------
// Description:
// Get a colormap from the windowing system.
Colormap vtkOpenGLOffscreenRenderWindow::GetDesiredColormap ()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetDesiredColormap (JMS: This is *VERY* problematic for Pbuffers!!!!\n Find a way to avoid doing this\n");
  XVisualInfo *v;
  if (this->ColorMap) return this->ColorMap;
  // get the default visual to use 
  v = this->GetDesiredVisualInfo();
  this->ColorMap = XCreateColormap(this->DisplayId,
				   RootWindow( this->DisplayId, v->screen),
				   v->visual, AllocNone );
  return this->ColorMap;  
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::PrintSelf(ostream& os, vtkIndent indent)
{
  this->vtkXRenderWindow::PrintSelf(os,indent);
  os << indent << "ContextId: " << this->ContextId << "\n";
  os << indent << "MultiSamples: " << this->MultiSamples << "\n";
}


//----------------------------------------------------------------
unsigned char *vtkOpenGLOffscreenRenderWindow::GetPixelData(int x1, int y1, int x2, int y2, 
						int front)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetPixelData\n");
//  long     xloop,yloop;
//  int     x_low, y_low;
  int     x_hi, y_hi;
//  unsigned char   *buffer;
  unsigned char   *data = NULL;
//  unsigned char   *p_data = NULL;

/*
  cout<<"  ==========================="<< endl;
  cout<<"  (GetPixelData)this->DisplayId = "<< this->DisplayId <<endl;
  cout<<"  (GetPixelData)this->WindowId = "<< this->WindowId <<endl;
  cout<<"  (GetPixelData)this->ContextId = "<< this->ContextId <<endl;
  cout<<"  ==========================="<< endl;
*/

//  double startTime = getTime();
//  printf("time: %f\n", startTime);

  // set the current window 
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

//  printf("time1: %f\n", getTime()-startTime);
//  printf("time2: %f\n", getTime()-startTime);
  if (y1 < y2) {
//      y_low = y1; 
      y_hi  = y2;
    }
  else {
//      y_low = y2; 
      y_hi  = y1;
    }

  if (x1 < x2) {
//      x_low = x1; 
      x_hi  = x2;
    }
  else {
//      x_low = x2; 
      x_hi  = x1;
    }

  if (front) {
      glReadBuffer(GL_FRONT);
    }
  else {
      glReadBuffer(GL_BACK);
    }

//  printf("time3: %f\n", getTime()-startTime);

  //buffer = new unsigned char [4*(abs(x2 - x1)+1)*(abs(y2 - y1) + 1)];
  data = new unsigned char[(abs(x2 - x1) + 1)*(abs(y2 - y1) + 1)*3];

/*
  p_data = data;
  for (yloop = y_low; yloop <= y_hi; yloop++) {
      // read in a row of pixels 
      glReadPixels(x_low,yloop,(x_hi-x_low+1),1, 
		   GL_RGBA, GL_UNSIGNED_BYTE, buffer);
      for (xloop = 0; xloop <= (abs(x2-x1)); xloop++) {
	    *p_data = buffer[xloop*4]; p_data++;
	    *p_data = buffer[xloop*4+1]; p_data++;
	    *p_data = buffer[xloop*4+2]; p_data++;
	  }
    }
  delete [] buffer;
*/

  int height = y_hi+1;
  int width = x_hi+1;
//  cerr << "height: " << height << "  width: " << width << endl;

  glPixelStorei(GL_PACK_ALIGNMENT, 1);
  glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, data);

//  printf("time4: %f\n", getTime()-startTime);

/*
  glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, buffer);
  for(int i=0; i<width*height; i++)
  {
    data[i*3]   = buffer[i*4]; 
    data[i*3+1] = buffer[i*4+1];
    data[i*3+2] = buffer[i*4+2];
  }
  delete [] buffer;
*/


/*
  // dump the data to a PPM
  char header[20];
  sprintf(header, "P6 %d %d 255\n", width, height);
  FILE* outfile = fopen("test.ppm", "wb");
  fwrite(header, 1, strlen(header), outfile);
  fwrite(data, 1, width*height*3, outfile);
  fclose(outfile);
  cerr << "dumped the ppm" << endl;
*/

  return data;
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::SetPixelData(int x1,int y1,int x2,int y2,
				      unsigned char *data, int front)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetPixelData\n");

  int     y_low, y_hi;
  int     x_low, x_hi;
  int     xloop,yloop;
  unsigned char   *buffer;
  unsigned char   *p_data = NULL;

  // set the current window 
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

  if (front) 
      glDrawBuffer(GL_FRONT);
  else 
      glDrawBuffer(GL_BACK);

  buffer = new unsigned char [4*(abs(x2 - x1)+1)];

  if (y1 < y2) {
      y_low = y1; 
      y_hi  = y2;
    }
  else {
      y_low = y2; 
      y_hi  = y1;
    }
  
  if (x1 < x2) {
      x_low = x1; 
      x_hi  = x2;
    }
  else {
      x_low = x2; 
      x_hi  = x1;
    }
  
  // now write the binary info one row at a time 
  p_data = data;
  for (yloop = y_low; yloop <= y_hi; yloop++) {
      for (xloop = 0; xloop <= (abs(x2-x1)); xloop++)
	{
	  buffer[xloop*4] = *p_data; p_data++; 
	  buffer[xloop*4+1] = *p_data; p_data++;
	  buffer[xloop*4+2] = *p_data; p_data++;
	  buffer[xloop*4+3] = 0xff;
	}
      /* write out a row of pixels */
      glMatrixMode( GL_MODELVIEW );
      glPushMatrix();
      glLoadIdentity();
      glMatrixMode( GL_PROJECTION );
      glPushMatrix();
      glLoadIdentity();
      glRasterPos3f( (2.0 * (GLfloat)(x_low) / this->Size[0] - 1), 
		     (2.0 * (GLfloat)(yloop) / this->Size[1] - 1),
		     -1.0 );
      glMatrixMode( GL_MODELVIEW );
      glPopMatrix();
      glMatrixMode( GL_PROJECTION );
      glPopMatrix();

      glDrawPixels((x_hi-x_low+1),1, GL_RGBA, GL_UNSIGNED_BYTE, buffer);
    }
  delete [] buffer;
}

//----------------------------------------------------------------
float *vtkOpenGLOffscreenRenderWindow::GetRGBAPixelData(int x1, int y1, int x2, int y2, int front)
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetRGBAPixelData\n");

  int     y_low, y_hi;
  int     x_low, x_hi;
  int     width, height;
  float   *data = NULL;

  // set the current window 
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

  if (y1 < y2) {
      y_low = y1; 
      y_hi  = y2;
    }
  else {
      y_low = y2; 
      y_hi  = y1;
    }

  if (x1 < x2) {
      x_low = x1; 
      x_hi  = x2;
    }
  else {
      x_low = x2; 
      x_hi  = x1;
    }

  if (front) 
      glReadBuffer(GL_FRONT);
  else 
      glReadBuffer(GL_BACK);

  width  = abs(x_hi - x_low) + 1;
  height = abs(y_hi - y_low) + 1;

  data = new float[ (width*height*4) ];

  glReadPixels( x_low, y_low, width, height, GL_RGBA, GL_FLOAT, data);

  return data;
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::SetRGBAPixelData(int x1, int y1, 
       int x2, int y2, float *data, int front, int blend)
{
  cout << "vtkOpenGLOffscreenRenderWindow::SetRGBAPixelData\n";
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetRGBAPixelData\n");

  int     y_low, y_hi;
  int     x_low, x_hi;
  int     width, height;

  // set the current window 
  glXMakeCurrent(this->DisplayId,this->WindowId,this->ContextId);

  if (front) 
      glDrawBuffer(GL_FRONT);
  else 
      glDrawBuffer(GL_BACK);

  if (y1 < y2) {
      y_low = y1; 
      y_hi  = y2;
    }
  else {
      y_low = y2; 
      y_hi  = y1;
    }
  
  if (x1 < x2) {
      x_low = x1; 
      x_hi  = x2;
    }
  else {
      x_low = x2; 
      x_hi  = x1;
    }
  
  width  = abs(x_hi-x_low) + 1;
  height = abs(y_hi-y_low) + 1;

  /* write out a row of pixels */
  glMatrixMode( GL_MODELVIEW );
  glPushMatrix();
  glLoadIdentity();
  glMatrixMode( GL_PROJECTION );
  glPushMatrix();
  glLoadIdentity();
  glRasterPos3f( (2.0 * (GLfloat)(x_low) / this->Size[0] - 1), 
                 (2.0 * (GLfloat)(y_low) / this->Size[1] - 1),
		 -1.0 );
  glMatrixMode( GL_MODELVIEW );
  glPopMatrix();
  glMatrixMode( GL_PROJECTION );
  glPopMatrix();

  glDrawPixels( width, height, GL_RGBA, GL_FLOAT, data);
}

//----------------------------------------------------------------
float *vtkOpenGLOffscreenRenderWindow::GetZbufferData( int x1, int y1, int x2, int y2  )
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetZbufferData\n");

  int             y_low;
  int             x_low;
  int             width, height;
  float           *z_data = NULL;

  // set the current window 
  this->MakeCurrent();

  if (y1 < y2) {
      y_low = y1; 
//      y_hi  = y2;
    }
  else {
      y_low = y2; 
//      y_hi  = y1;
    }

  if (x1 < x2) {
      x_low = x1; 
//      x_hi  = x2;
    }
  else {
      x_low = x2; 
//      x_hi  = x1;
    }

  width =  abs(x2 - x1)+1;
  height = abs(y2 - y1)+1;

  z_data = new float[width*height];

  glReadPixels( x_low, y_low, 
		width, height,
		GL_DEPTH_COMPONENT, GL_FLOAT,
		z_data );

  return z_data;
}

//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::SetZbufferData( int x1, int y1, int x2, int y2,
					 float *buffer )
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::SetZbufferData\n");

  int             y_low;
  int             x_low;
  int             width, height;

  // set the current window 
  this->MakeCurrent();

  if (y1 < y2) {
      y_low = y1; 
//      y_hi  = y2;
    }
  else {
      y_low = y2; 
//      y_hi  = y1;
    }

  if (x1 < x2) {
      x_low = x1; 
//      x_hi  = x2;
    }
  else {
      x_low = x2; 
//      x_hi  = x1;
    }

  width =  abs(x2 - x1)+1;
  height = abs(y2 - y1)+1;

  glMatrixMode( GL_MODELVIEW );
  glPushMatrix();
  glLoadIdentity();
  glMatrixMode( GL_PROJECTION );
  glPushMatrix();
  glLoadIdentity();
  glRasterPos2f( 2.0 * (GLfloat)(x_low) / this->Size[0] - 1, 
                 2.0 * (GLfloat)(y_low) / this->Size[1] - 1);
  glMatrixMode( GL_MODELVIEW );
  glPopMatrix();
  glMatrixMode( GL_PROJECTION );
  glPopMatrix();

  glDrawPixels( width, height, GL_DEPTH_COMPONENT, GL_FLOAT, buffer);
}

//----------------------------------------------------------------
// return the current framebuffer as a JPG image
XImage *vtkOpenGLOffscreenRenderWindow::GetImage()
{
  offDebugMacro(<< "vtkOpenGLOffscreenRenderWindow::GetImage\n");

  int width = ((this->Size[0] > 0) ? this->Size[0] : 300);
  int height = ((this->Size[1] > 0) ? this->Size[1] : 300);
  XImage *img = XGetImage(this->DisplayId,
			  this->pixmap,
			  0, 0, width, height, AllPlanes, XYPixmap);
  // return new dlImage(img);
  return img;
}
//----------------------------------------------------------------
void vtkOpenGLOffscreenRenderWindow::RegisterTextureResource (GLuint id)
{
  cout <<endl;
  cout<<"----> vtkOpenGLOffscreenRenderWindow::RegisterTextureResource"<<endl;  
  cout <<endl;
  this->TextureResourceIds->InsertNextId ((int) id);
}
