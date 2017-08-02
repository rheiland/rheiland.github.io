/*=========================================================================

  Program:   Visualization Toolkit
  Module:    $RCSfile: vtkOpenGLOffscreenTexture.h,v $
  Language:  C++
  Date:      $Date: 1999/10/11 15:07:05 $
  Version:   $Revision: 1.12 $


Copyright (c) 1993-1998 Ken Martin, Will Schroeder, Bill Lorensen.

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
// .NAME vtkOpenGLOffscreenTexture - OpenGL texture map
// .SECTION Description
// vtkOpenGLOffscreenTexture is a concrete implementation of the abstract class 
// vtkTexture. vtkOpenGLOffscreenTexture interfaces to the OpenGL rendering library.

#ifndef __vtkOpenGLOffscreenTexture_h
#define __vtkOpenGLOffscreenTexture_h

#include "vtkTexture.h"

class vtkWindow;
class vtkOpenGLRenderer;
class vtkRenderWindow;

class VTK_EXPORT vtkOpenGLOffscreenTexture : public vtkTexture
{
public:
  static vtkOpenGLOffscreenTexture *New();
  const char *GetClassName() {return "vtkOpenGLOffscreenTexture";};

  // Description:
  // Implement base class method.
  void Load(vtkRenderer *ren);
  
  // Description:
  // Release any graphics resources that are being consumed by this texture.
  // The parameter window could be used to determine which graphic
  // resources to release. Using the same texture object in multiple
  // render windows is NOT currently supported. 
  void ReleaseGraphicsResources(vtkWindow *);

protected:
  vtkOpenGLOffscreenTexture();
  ~vtkOpenGLOffscreenTexture();
  vtkOpenGLOffscreenTexture(const vtkOpenGLOffscreenTexture&) {};
  void operator=(const vtkOpenGLOffscreenTexture&) {};

  unsigned char *ResampleToPowerOfTwo(int &xsize, int &ysize, 
                                      unsigned char *dptr, int bpp);

  vtkTimeStamp   LoadTime;
  long          Index;
  static   long GlobalIndex;
  vtkRenderWindow *RenderWindow;   // RenderWindow used for previous render
};

#endif
