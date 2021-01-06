//========================================================================
// ubmark-quicksort
//========================================================================
// This version (v1) is brought over directly from Fall 15.

#include "../common/common.h"
//#include "common.h"
#include "ubmark-quicksort.dat"

//------------------------------------------------------------------------
// quicksort-scalar
//------------------------------------------------------------------------

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Add functions you may need
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

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


void quicksort_scalar( int* dest, int* src, int size )
{

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Implement main function of serial quicksort
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
	quicksort(src, 0, size-1);
    //implement quicksort algorithm here
    
	int i;
    // dummy copy src into dest
    for ( i = 0; i < size; i++ )
      dest[i] = src[i];

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
  int dest[size];

  int i;
  for ( i = 0; i < size; i++ )
    dest[i] = 0;

  test_stats_on();
  quicksort_scalar( dest, src, size );
  test_stats_off();

  verify_results( dest, ref, size );

  return 0;
}
