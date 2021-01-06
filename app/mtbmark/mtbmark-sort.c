//========================================================================
// mtbmark-sort-v1
//========================================================================
// This version (v1) is brought over directly from Fall 15. It uses
// quicksort to sort each fourth of the elements, and then run 3 times of
// two-way merge. The first two merge runs are parallelized.

#include "common.h"
#include "mtbmark-sort.dat"

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Implement multicore sorting
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

typedef struct {
  int* dest;
  int* src;
  int size;
}arg_q;

typedef struct {
  int* dest;
  int* sorted1;
  int* sorted2;
  int size1;
  int size2;
}arg_m;


void swap(int* element1, int* element2){
  int temp = *element1;
  *element1 = *element2;
  *element2 = temp;
}

int partition(int* sorted, int start, int end){
  int pivot= sorted[end];
  int index= start-1;
  for(int array_it = start; array_it <= end-1; array_it++){
    if(sorted[array_it] < pivot){
      index++;
      swap(&sorted[index], &sorted[array_it]);
    }
  }
  swap(&sorted[index+1], &sorted[end]);
  return (index+1);
}

void quicksort(int* sorted, int start, int end) {

    if(start < end){
        int p_index = partition(sorted, start, end);
        quicksort(sorted, start, p_index-1);
        quicksort(sorted, p_index+1, end);
    }

}

void quicksort_scalar( void* arg_qptr)
{

        arg_q* arg_ptr = (arg_q*) arg_qptr;

        int* dest = arg_ptr->dest;
        int* src  = arg_ptr->src;
        int size  = arg_ptr->size;

        quicksort(src, 0, size-1);
    //implement quicksort algorithm here

        int i;
    // dummy copy src into dest
    for ( i = 0; i < size; i++ )
      dest[i] = src[i];

}

void mergesort( void* arg_mptr)
{

        arg_m* arg_ptr = (arg_m*) arg_mptr;

        int* dest    = arg_ptr->dest;
        int* sorted1 = arg_ptr->sorted1;
        int* sorted2 = arg_ptr->sorted2;
        int size1    = arg_ptr->size1;
        int size2    = arg_ptr->size2;

        int in1 = 0;
        int in2 = 0;        
        for(int i = 0; i < size1+size2; i++){
          if(in1 >= size1){
            dest[i] = sorted2[in2];
            in2++;
          }else if(in2 >= size2){
            dest[i] = sorted1[in1];
            in1++;
          }else if(sorted1[in1] < sorted2[in2]){
            dest[i] = sorted1[in1];
            in1++;
          }else{
            dest[i] = sorted2[in2];
            in2++;
          }
        }


}

void slice(int* src, int* dest, int start, int end)
{
	for(int i=start; i<=end; i++){
		dest[i-start] = src[i];
	}
}


//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( i, dest[i], ref[i] );
    }
  }
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{

  // Initialize the bthread (bare thread)

  bthread_init();

  // Initialize dest array, which stores the final result.

  int dest[size];

  //--------------------------------------------------------------------
  // Start counting stats
  //--------------------------------------------------------------------

  test_stats_on();

  //int i = 0;

  // Because we need in-place sorting, we need to create a mutable temp
  // array.
  //int temp0[size];

  //for ( i = 0; i < size; i++ ) {
  //  temp0[i] = src[i];
  //}

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: distribute work and call sort_scalar()
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  int part = size/4;
  int array0[part];
  int array1[part];
  int array2[part];
  int array3[size-3*part];

  slice(src, array0, 0, 	part-1);
  slice(src, array1, part, 	2*part-1);
  slice(src, array2, 2*part,3*part-1);
  slice(src, array3, 3*part,size-1);

  arg_q arg0 = {array0, array0, part};
  arg_q arg1 = {array1, array1, part};
  arg_q arg2 = {array2, array2, part};
  arg_q arg3 = {array3, array3, (size - 3*part)};

  bthread_spawn(1, &quicksort_scalar, &arg1);
  bthread_spawn(2, &quicksort_scalar, &arg2);
  bthread_spawn(3, &quicksort_scalar, &arg3);

  quicksort_scalar(&arg0);

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: do bthread_join(), do the final reduction step here
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  bthread_join(1); 
  bthread_join(2); 
  bthread_join(3); 

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: distribute work and call sort_scalar()
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  int dest0[2*part];
  int dest1[size-2*part];


  arg_m argm0 = {dest0, array0, array1, part, part};
  arg_m argm1 = {dest1, array2, array3, part, (size-3*part)};

  bthread_spawn(1, &mergesort, &argm1);

  mergesort(&argm0);

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: do bthread_join(), do the final reduction step here
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  bthread_join(1); 

  arg_m argm2 = {dest, dest0, dest1, 2*part, (size-2*part)};
  mergesort(&argm2);

  //--------------------------------------------------------------------
  // Stop counting stats
  //--------------------------------------------------------------------

  test_stats_off();

  // verifies solution

  verify_results( dest, ref, size );

  return 0;
}
