// g++ -O3 -DNDEBUG  -arch i386 -mmacosx-version-min=10.4 -msse3 -ftree-vectorize -I<path-to-tbb-headers> -L<path-to-tbb-libs>  psum2.cpp -ltbb -ltbbmalloc  -o psum2

#include <iostream>
#include "tbb/tick_count.h"
#include "tbb/blocked_range.h"
#include "tbb/task_scheduler_init.h"
#include "tbb/parallel_reduce.h"

using namespace std;

class SumUp {
  float* my_a;
public:
  double my_sum;
  void operator()( const tbb::blocked_range<int>& r ) {
    float *a = my_a;
    double sum = my_sum;
    int end = r.end();
    for( int i=r.begin(); i!=end; ++i ) {
//      sum += Foo(a[i]);   // Foo = identity
      sum += a[i];
    }
    my_sum = sum;
  }
  SumUp( SumUp& x, tbb::split ) : my_a(x.my_a), my_sum(0) {}
  void join( const SumUp& y ) {my_sum+=y.my_sum;}
  SumUp(float a[] ) :
    my_a(a), my_sum(0)
  {}
};

//double ParallelSum(const float a[], int n) {
double ParallelSum(float a[], int n) {
  SumUp sf(a);
  tbb::parallel_reduce( tbb::blocked_range<int>(0, n), sf, tbb::auto_partitioner() );
  return sf.my_sum;
}

int main()
{
  tbb::task_scheduler_init init;

  int nx=10000;
  int ny=10000;
  float *v = new float[nx*ny];
  if (v == NULL) {
    cout << "Error: Cannot malloc mem"<<endl;
    exit(-1);
  }
  float *vp = v;
  for (int idx=0; idx<nx; idx++)
  for (int idy=0; idy<ny; idy++) {
    if (!(idx%2)) 
      *v++ = (float)idy + 1.0;
    else 
      *v++ = -(float)idy - 1.0;
  }

#undef PARALLEL_SUM
#ifdef PARALLEL_SUM
//  double sum = ParallelSum(const vp,nx*ny);
  double sum = ParallelSum(vp,nx*ny);
  cout << "(parallel) sum= "<<sum<<endl;

#else
  v = vp;
  int isize=nx*ny;
  double sum2 = 0.0;  // NB! don't use float
//  for (int idx=0; idx<nx; idx++) {
//   for (int idy=0; idy<ny; idy++) {
   for (int idx=0; idx<isize; idx++) {
//    cout<< *v << ",";
    sum2 += *v++;
   }
//   cout << endl;
//  }
  cout << "(serial) sum2= "<<sum2<<endl;
#endif
  
  return 0;
}
