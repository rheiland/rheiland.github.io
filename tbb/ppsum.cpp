// g++ -O3 -DNDEBUG  -arch i386 -mmacosx-version-min=10.4 -msse3 -ftree-vectorize -I<path-to-tbb-headers> -L<path-to-tbb-libs> ppsum.cpp -ltbb -ltbbmalloc  -o ppsum

#include <iostream>
#include "tbb/tick_count.h"
#include "tbb/blocked_range.h"
#include "tbb/task_scheduler_init.h"
#include "tbb/parallel_for.h"

using namespace std;

static int nx=10000;
static int ny=10000;
double sum=0.0;
static float *vp;

struct UpdateSum {
  void operator() (const tbb::blocked_range<int>& range) const {
//    float *v = my_v;
    sum = 0.0;
    for (int i=range.begin(); i!=range.end(); ++i) {
      sum += *vp;
      vp++;
    }
  }
};

static void ParallelUpdateSum() {
  int maxIndex = nx*ny;
  tbb::parallel_for( tbb::blocked_range<int>(0, maxIndex),
                     UpdateSum());
}

int main()
{
  tbb::task_scheduler_init init;

  float *v = new float[nx*ny];
  if (v == NULL) {
    cout << "Error: Cannot malloc mem"<<endl;
    exit(-1);
  }
  vp = v;
  // Init array so elements sum to 0
  for (int idx=0; idx<nx; idx++)
  for (int idy=0; idy<ny; idy++) {
    if (!(idx%2)) 
      *v++ = (float)idy + 1.0;
    else 
      *v++ = -(float)idy - 1.0;
  }

  ParallelUpdateSum();
  cout << "sum= "<<sum<<endl;

#ifdef SERIAL_SUM
  v = vp;
  int isize=nx*ny;
  double sum2 = 0.0;  // NB! don't use float
  for (int idx=0; idx<isize; idx++) {
    sum2 += *v++;
  }
  cout << "sum2= "<<sum2<<endl;
#endif
  
  return 0;
}
