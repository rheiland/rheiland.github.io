
// (R.Heiland)  Manually inserted... not something that's auto-wrapped -------
static PyObject *PyvtkOpenGLRenderWindow_GetPixelData(PyObject *self,
                                                      PyObject *args)
{
  int error;
  vtkOpenGLRenderWindow *op;
  op = (vtkOpenGLRenderWindow *)vtkPythonGetPointerFromObject(self,"vtkOpenGLRenderWindow");

  {
  int x0,y0,x1,y1,frontFlag;
  unsigned char *buffer;
  int buffer_size;

  PyErr_Clear();
  error = 0;
  if (PyArg_ParseTuple(args, "iiiii", &x0,&y0, &x1,&y1, &frontFlag))
    {
    if (!error)
      {
      buffer_size = (x1-x0+1)*(y1-y0+1) * 3;
      buffer = (unsigned char *)op->GetPixelData(x0,y0,x1,y1,frontFlag);
      return Py_BuildValue("s#", buffer, buffer_size);
      }
    }
  }
  return NULL;
}
