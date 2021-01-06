#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest
import random

random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from lab1_imul.IntMulFL   import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, imul, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( Bits(64), src_msgs,  src_delay  )
    s.imul = imul
    s.sink = TestSink   ( Bits(32), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.imul.vcd_file = dump_vcd

    # Translation

    if test_verilog:
      s.imul = TranslationTool( s.imul )

    # Connect

    s.connect( s.src.out,  s.imul.req  )
    s.connect( s.imul.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.imul.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  msg = Bits( 64 )
  msg[32:64] = Bits( 32, a, trunc=True )
  msg[ 0:32] = Bits( 32, b, trunc=True )
  return msg

def resp( a ):
  return Bits( 32, a, trunc=True )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  req(  2,  3 ), resp(   6 ),
  req(  4,  5 ), resp(  20 ),
  req(  3,  4 ), resp(  12 ),
  req( 10, 13 ), resp( 130 ),
  req(  8,  7 ), resp(  56 ),
]

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional lists of request/response messages to create
# additional directed and random test cases.
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#----------------------------------------------------------------------
# Test Case: small negative * negative
#----------------------------------------------------------------------

small_neg_neg_msgs = [
  req(  -2,  -3 ), resp(   6 ),
  req(  -4,  -5 ), resp(  20 ),
  req(  -3,  -4 ), resp(  12 ),
  req( -10, -13 ), resp( 130 ),
  req(  -8,  -7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: small positive * negative
#----------------------------------------------------------------------

small_pos_neg_msgs = [
  req(  2,  -3 ), resp(   -6 ),
  req(  4,  -5 ), resp(  -20 ),
  req(  3,  -4 ), resp(  -12 ),
  req( 10, -13 ), resp( -130 ),
  req(  8,  -7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * positive
#----------------------------------------------------------------------

small_neg_pos_msgs = [
  req(  -2,  3 ), resp(   -6 ),
  req(  -4,  5 ), resp(  -20 ),
  req(  -3,  4 ), resp(  -12 ),
  req( -10, 13 ), resp( -130 ),
  req(  -8,  7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: 0 * integer OR integer * 0
#----------------------------------------------------------------------

zero_msgs = [
  req(  0,  1 ), resp(   0 ),
  req(  0,  -1 ), resp(   0 ),
  req(  0,  3 ), resp(   0 ),
  req(  1,  0 ), resp(   0 ),
  req(  -1,  0 ), resp(   0 ),
  req(  3,  0 ), resp(   0 ),
  req(  0,  0 ), resp(   0 ),
]

#----------------------------------------------------------------------
# Test Case: 1 * integer OR integer * 1
#----------------------------------------------------------------------

pos_one_msgs = [
  req(  3,  1 ), resp(   3 ),
  req(  -3,  1 ), resp(   -3 ),
  req(  1,  3 ), resp(   3 ),
  req(  1,  -3 ), resp(   -3 ),
  req(  2147483647,  1 ), resp(   2147483647 ),
  req( -2147483648, 1 ), resp( -2147483648  ),
  req(  1,  2147483647 ), resp(   2147483647 ),
  req(  1,  -2147483648 ), resp(   -2147483648 ),
]

#----------------------------------------------------------------------
# Test Case: -1 * integer OR integer * -1
#----------------------------------------------------------------------

neg_one_msgs = [
  req(  3,  -1 ), resp(   -3 ),
  req(  -3,  -1 ), resp(   3 ),
  req(  -1,  3 ), resp(   -3 ),
  req(  -1,  -3 ), resp(   3 ),
  req(  2147483647,  -1 ), resp(   -2147483647 ),
  req(  -2147483648,  -1 ), resp(   2147483648 ),
  req(  -1,  2147483647 ), resp(   -2147483647 ),
  req(  -1,  -2147483648 ), resp(   2147483648 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * positive
#----------------------------------------------------------------------

large_pos_pos_msgs = [
  req(  44000,  31700 ), resp( 1394800000 ),
  # Actual result should be 2200000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -2094967296
  req(  44000,  50000 ), resp(  -2094967296 ),
  req(  48800,  44000 ), resp(  2147200000 ),
  # Actual result should be 10000000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get 1410065408
  req( 500000, 20000 ), resp( 1410065408 ),
  req(  3386,  20998 ), resp(  71099228 ),
]

#----------------------------------------------------------------------
# Test Case: large negative * negative
#----------------------------------------------------------------------

large_neg_neg_msgs = [
  req(  -44000,  -31700 ), resp( 1394800000 ),
  # Actual result should be 2200000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -2094967296
  req(  -44000,  -50000 ), resp(  -2094967296 ),
  req(  -48800,  -44000 ), resp(  2147200000 ),
  # Actual result should be 10000000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get 1410065408
  req( -500000, -20000 ), resp( 1410065408 ),
  req(  -3386,  -20998 ), resp(  71099228 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * negative
#----------------------------------------------------------------------

large_pos_neg_msgs = [
  req(  44000,  -31700 ), resp( -1394800000 ),
  # Actual result should be -2200000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get 2094967296
  req(  44000,  -50000 ), resp(  2094967296 ),
  req(  48800,  -44000 ), resp(  -2147200000 ),
  # Actual result should be -10000000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -1410065408
  req( 500000, -20000 ), resp( -1410065408 ),
  req(  3386,  -20998 ), resp(  -71099228 ),
]

#----------------------------------------------------------------------
# Test Case: large negative * positive
#----------------------------------------------------------------------

large_neg_pos_msgs = [
  req(  -44000,  31700 ), resp( -1394800000 ),
  # Actual result should be -2200000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get 2094967296
  req(  -44000,  50000 ), resp(  2094967296 ),
  req(  -48800,  44000 ), resp(  -2147200000 ),
  # Actual result should be -10000000000 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -1410065408
  req( -500000, 20000 ), resp( -1410065408 ),
  req(  -3386,  20998 ), resp(  -71099228 ),
]

#----------------------------------------------------------------------
# Test Case: lower bits masked off
#----------------------------------------------------------------------

lower_mask_msgs = [
  # 0b11100000 *  0b11111111111111111100000000000000
  req( -32,  -16384 ), resp( 524288 ),
  # 0b11100000 *  0b11111111111111111111111110000000 
  req( -32, -128 ), resp(  4096 ),
  # 0b11111111111111111111110000000000 * 0b11111111111111111111111000000000
  req( -1024,  -512 ), resp(  524288 ),
  # 0b11110000 * 0b1111111000000000
  req( -16,  -512), resp( 8192 ),
  # 0b11111000 * 0b11111000
  req( -8,  -8), resp(  64 ),
]

#----------------------------------------------------------------------
# Test Case: middle bits masked off
#----------------------------------------------------------------------

middle_mask_msgs = [
  # 0b1110000000111111 *  0b11111111111100000000000000111111
  # Actual result should be 8523362177 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -66572415
  req( -8129,  -1048513 ), resp( -66572415 ),
  # 0b1110000011111111 *  0b11111111111111111110000000011111 
  req( -7937, -8161 ), resp(  64773857 ),
  # 0b11100000000001111111111111111111 * 0b11000111
  # Actual result should be 30571757625 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get 506986553
  req( -536346625,  -57 ), resp(  506986553 ),
  # 0b11000011 * 0b1111110000000001
  req( -61,  -1023), resp( 62403 ),
  # 0b11100111 * 0b10001111
  req( -25,  -8), resp(  200 ),
]

#----------------------------------------------------------------------
# Test Case: multiplying sparse numbers with many zeros but few ones
#----------------------------------------------------------------------

sparse_msgs = [
  # 0b0001000000001000 * 1000100001100011
  req( 4104,  -30621 ), resp( -125668584 ),
  # 0b00010000 *  0b00010001
  req( 16, 17 ), resp(  272 ),
  # 0b00111000000100000000100001010000 * 0b00000010
  req( 940574800,  2 ), resp(  1881149600 ),
  # 0b10000001 * 0b10001001
  req( -127,  -119), resp(  15113 ),
]

#----------------------------------------------------------------------
# Test Case: multiplying dense numbers with many ones but few zeros
#----------------------------------------------------------------------

dense_msgs = [
  # 0b1110111111110111 * 0b0111011110011100
  req( -4105,  30620 ), resp( -125695100 ),
  # 0b11101111 *  0b11101110
  req( -17, -18 ), resp(  306 ),
  # 0b11000111111011111111011110101111 * 0b11111101
  # Actual result should be 2821724403 but this number can't be
  # expressed in 32 bits, so the result is truncated and we get -1473242893
  req( -940574801,  -3 ), resp(  -1473242893 ),
  # 0b01111110 * 0b01110110
  req( 126,  118), resp(  14868 ),
]

#----------------------------------------------------------------------
# Test Case: Cases where the alt design will take the same amount of
#            cycles as the base design due to lack of consecutive zeros
#----------------------------------------------------------------------

alt_design_corner_cases_msgs = [
  # 0b11111111111111111111111111111111 * 0b01010101010101010101010101010101
  req( -1,  1431655765 ), resp( -1431655765 ),
  # 0b10101010101010101010101010101010 *  0b11111111111111111111111111111111
  req( -1431655766, -1 ), resp( 1431655766 ),
]

#----------------------------------------------------------------------
# Random Test Case: small positive * positive
#----------------------------------------------------------------------

random_small_pos_pos_msgs = []
for i in xrange(5):
  a = random.randint(0,5001)
  b = random.randint(0,5001)
  c = a * b
  random_small_pos_pos_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: small negative * negative
#----------------------------------------------------------------------

random_small_neg_neg_msgs = []
for i in xrange(5):
  a = random.randint(-5000,0)
  b = random.randint(-5000,0)
  c = a * b
  random_small_neg_neg_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: small positive * negative
#----------------------------------------------------------------------

random_small_pos_neg_msgs = []
for i in xrange(5):
  a = random.randint(0,5001)
  b = random.randint(-5000,0)
  c = a * b
  random_small_pos_neg_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: small negative * positive
#----------------------------------------------------------------------

random_small_neg_pos_msgs = []
for i in xrange(5):
  a = random.randint(-5000,0)
  b = random.randint(0,5001)
  c = a * b
  random_small_neg_pos_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: 0 * integer OR integer * 0
#----------------------------------------------------------------------

random_zero_msgs = [
  req(  0,  random.randint(0,2147483648) ), resp(   0 ),
  req(  0,  random.randint(-2147483648,0) ), resp(   0 ),
  req(  random.randint(0,2147483648),  0 ), resp(   0 ),
  req(  random.randint(-2147483648,0),  0 ), resp(   0 ),
]

#----------------------------------------------------------------------
# Random Test Case: 1 * integer OR integer * 1
#----------------------------------------------------------------------

random_pos_one_msgs = []
for i in xrange(2):
  a = random.randint(0,2147483648)
  c = a * 1
  random_pos_one_msgs.extend([ req( a, 1 ), resp(c) ])
  
for i in xrange(2):
  a = random.randint(-2147483648,0)
  c = a * 1
  random_pos_one_msgs.extend([ req( a, 1 ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: -1 * integer OR integer * -1
#----------------------------------------------------------------------

random_neg_one_msgs = []
for i in xrange(2):
  a = random.randint(0,2147483648)
  c = a * -1
  random_neg_one_msgs.extend([ req( a, -1 ), resp(c) ])
  
for i in xrange(2):
  a = random.randint(-2147483648,0)
  c = a * -1
  random_neg_one_msgs.extend([ req( a, -1 ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: large positive * positive
#----------------------------------------------------------------------

random_large_pos_pos_msgs = []
for i in xrange(10):
  a = random.randint(5001,3000000000)
  b = random.randint(5001,3000000000)
  c = a * b
  random_large_pos_pos_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: large negative * negative
#----------------------------------------------------------------------

random_large_neg_neg_msgs = []
for i in xrange(10):
  a = random.randint(-3000000000,-5000)
  b = random.randint(-3000000000,-5000)
  c = a * b
  random_large_neg_neg_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: large positive * negative
#----------------------------------------------------------------------

random_large_pos_neg_msgs = []
for i in xrange(10):
  a = random.randint(5001,3000000000)
  b = random.randint(-3000000000,-5000)
  c = a * b
  random_large_pos_neg_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: large negative * positive
#----------------------------------------------------------------------

random_large_neg_pos_msgs = []
for i in xrange(10):
  a = random.randint(-3000000000,-5000)
  b = random.randint(5000,3000000000)
  c = a * b
  random_large_neg_pos_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: lower bits masked off
#----------------------------------------------------------------------

random_lower_mask_msgs = []
for i in xrange(5):
  a_mask = random.randint(0,16)
  b_mask = random.randint(0,16)
  # Left shifts the 32-bit 2' complement representation of -1
  a = Bits( 32, -(2**a_mask), trunc=True )
  b = Bits( 32, -(2**b_mask), trunc=True )
  c = a * b
  random_lower_mask_msgs.extend([ req( a, b ), resp(c) ])

#----------------------------------------------------------------------
# Random Test Case: middle bits masked off
#----------------------------------------------------------------------

random_middle_mask_msgs = []
for i in xrange(5):
  a1_mask = random.randint(1,16)
  a2_mask = random.randint(1,16)
  a1 = -1 << a1_mask
  a2 = 4294967295 >> a2_mask
  # XOR left-shifted a1 and right-shifted a2 to mask random number of
  # bits in the middle
  a = a1 ^ a2
  
  b1_mask = random.randint(1,16)
  b2_mask = random.randint(1,16)
  b1 = -1 << b1_mask
  b2 = 4294967295 >> b2_mask
  # XOR left-shifted b1 and right-shifted b2 to mask random number of
  # bits in the middle
  b = b1 ^ b2
  
  c = a * b
  random_middle_mask_msgs.extend([ req( a, b ), resp(c) ])

#--------------------------------------------------------------------------
# Random Test Case: multiplying sparse numbers with many zeros but few ones
#--------------------------------------------------------------------------

random_sparse_msgs = []
for i in xrange(5):
  # Generate random number of ones to insert into bit array a and b
  num_of_ones_in_a = random.randint(1,10)
  num_of_ones_in_b = random.randint(1,10)
  a = []
  b =[]
  # Insert '1' into array for a and b
  while(num_of_ones_in_a > 0):
    a.append('1')
    num_of_ones_in_a -= 1
  while(num_of_ones_in_b > 0):
    b.append('1')
    num_of_ones_in_b -= 1
  # Fill up rest of 32 bit array with zeros
  while(len(a) <= 32):
    a.append('0')
  while(len(b) <= 32):
    b.append('0')
  
  # Shuffle the arrays
  random.shuffle(a)
  random.shuffle(b)
  # Convert the arrays to ints
  a = int(''.join(a), 2)
  b = int(''.join(b), 2)
    
  c = a * b
  random_sparse_msgs.extend([ req( a, b ), resp(c) ])

#-------------------------------------------------------------------------
# Random Test Case: multiplying dense numbers with many ones but few zeros
#-------------------------------------------------------------------------

random_dense_msgs = []
for i in xrange(5):
  # Generate random number of zeros to insert into bit array a and b
  num_of_zeros_in_a = random.randint(1,10)
  num_of_zeros_in_b = random.randint(1,10)
  a = []
  b =[]
  # Insert '0' into array for a and b
  while(num_of_zeros_in_a > 0):
    a.append('0')
    num_of_zeros_in_a -= 1
  while(num_of_zeros_in_b > 0):
    b.append('0')
    num_of_zeros_in_b -= 1
  # Fill up rest of 32 bit array with ones
  while(len(a) <= 32):
    a.append('1')
  while(len(b) <= 32):
    b.append('1')
   
  # Shuffle the arrays  
  random.shuffle(a)
  random.shuffle(b)
  # Convert the arrays to ints
  a = int(''.join(a), 2)
  b = int(''.join(b), 2)
    
  c = a * b
  random_dense_msgs.extend([ req( a, b ), resp(c) ])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                 src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,   0,        0          ],
  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to leverage the additional lists
  # of request/response messages defined above, but also to test
  # different source/sink random delays.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  [ "small_neg_neg",     small_neg_neg_msgs,   0,        0          ],
  [ "small_neg_pos",     small_neg_pos_msgs,   0,        0          ],
  [ "small_pos_neg",     small_pos_neg_msgs,   0,        0          ],
  [ "zero",              zero_msgs,            0,        0          ],
  [ "pos_one",           pos_one_msgs,         0,        0          ],
  [ "neg_one",           neg_one_msgs,         0,        0          ],
  [ "large_pos_pos",     large_pos_pos_msgs,   0,        0          ],
  [ "large_neg_neg",     large_neg_neg_msgs,   0,        0          ],
  [ "large_neg_pos",     large_neg_pos_msgs,   0,        0          ],
  [ "large_pos_neg",     large_pos_neg_msgs,   0,        0          ],
  [ "lower_mask",        lower_mask_msgs,      0,        0          ],
  [ "middle_mask",       middle_mask_msgs,     0,        0          ],
  [ "sparse_mask",       sparse_msgs,          0,        0          ],
  [ "dense_mask",        dense_msgs,           0,        0          ],
  [ "alt_corner_cases",  alt_design_corner_cases_msgs, 0,    0      ],
  # Same tests as above but with source/sink delay
  [ "delay_small_pos_pos",     small_pos_pos_msgs,   1,        5          ],
  [ "delay_small_neg_neg",     small_neg_neg_msgs,   3,        6          ],
  [ "delay_small_neg_pos",     small_neg_pos_msgs,   5,        1          ],
  [ "delay_small_pos_neg",     small_pos_neg_msgs,   2,        4          ],
  [ "delay_zero",              zero_msgs,            10,        0         ],
  [ "delay_pos_one",           pos_one_msgs,         3,        5          ],
  [ "delay_neg_one",           neg_one_msgs,         7,        7          ],
  [ "delay_large_pos_pos",     large_pos_pos_msgs,   1,        8          ],
  [ "delay_large_neg_neg",     large_neg_neg_msgs,   2,        9          ],
  [ "delay_large_neg_pos",     large_neg_pos_msgs,   8,        4          ],
  [ "delay_large_pos_neg",     large_pos_neg_msgs,   9,        11         ],
  [ "delay_lower_mask",        lower_mask_msgs,      8,        3          ],
  [ "delay_middle_mask",       middle_mask_msgs,     0,        5          ],
  [ "delay_sparse_mask",       sparse_msgs,          1,        43         ],
  [ "delay_dense_mask",        dense_msgs,           3,        2          ],
  [ "delay_alt_corner_cases",  alt_design_corner_cases_msgs, 10,    1     ],
  # Random test cases
  # Random source and sink delay is anywhere between 0 and 19 (inclusive)
  [ "random_small_pos_pos",     random_small_pos_pos_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_small_neg_neg",     random_small_neg_neg_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_small_neg_pos",     random_small_neg_pos_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_small_pos_neg",     random_small_pos_neg_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_zero",              random_zero_msgs,            random.randint(1,20),        random.randint(1,20)          ],
  [ "random_pos_one",           random_pos_one_msgs,         random.randint(1,20),        random.randint(1,20)          ],
  [ "random_neg_one",           random_neg_one_msgs,         random.randint(1,20),        random.randint(1,20)          ],
  [ "random_large_pos_pos",     random_large_pos_pos_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_large_neg_neg",     random_large_neg_neg_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_large_neg_pos",     random_large_neg_pos_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_large_pos_neg",     random_large_pos_neg_msgs,   random.randint(1,20),        random.randint(1,20)          ],
  [ "random_lower_mask",        random_lower_mask_msgs,      random.randint(1,20),        random.randint(1,20)          ],
  [ "random_middle_mask",       random_middle_mask_msgs,     random.randint(1,20),        random.randint(1,20)          ],
  [ "random_sparse_mask",       random_sparse_msgs,          random.randint(1,20),        random.randint(1,20)          ],
  [ "random_dense_mask",        random_dense_msgs,           random.randint(1,20),        random.randint(1,20)          ],

])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( IntMulFL(),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

