#=========================================================================
# slli
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x80008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

# ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define additional directed and random test cases.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rimm_dest_dep_test( 5, "slli", 1, 1, 2 ),
    gen_rimm_dest_dep_test( 4, "slli", 2, 1, 4 ),
    gen_rimm_dest_dep_test( 3, "slli", 3, 1, 6 ),
    gen_rimm_dest_dep_test( 2, "slli", 4, 1, 8 ),
    gen_rimm_dest_dep_test( 1, "slli", 5, 1, 10 ),
    gen_rimm_dest_dep_test( 0, "slli", 6, 1, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slli", 7,  1, 14 ),
    gen_rimm_src_dep_test( 4, "slli", 8,  1, 16 ),
    gen_rimm_src_dep_test( 3, "slli", 9,  1, 18 ),
    gen_rimm_src_dep_test( 2, "slli", 10, 1, 20 ),
    gen_rimm_src_dep_test( 1, "slli", 11, 1, 22 ),
    gen_rimm_src_dep_test( 0, "slli", 12, 1, 24 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slli",  25, 1,  50 ),
    gen_rimm_src_eq_dest_test( "slli", -26, 1, -52 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "slli", 0, 0, 0 ),
    gen_rimm_value_test( "slli", 1, 1, 2 ),
    gen_rimm_value_test( "slli", -3, 7, -384),

    gen_rimm_value_test( "slli", 0, 14, 0 ),
    gen_rimm_value_test( "slli", -2147483648, 0, -2147483648 ),
    gen_rimm_value_test( "slli", -2147483648, 14, 0 ),

    gen_rimm_value_test( "slli", 32767, 0, 32767 ),
    gen_rimm_value_test( "slli", 2147483647, 0, 2147483647 ),
    gen_rimm_value_test( "slli", 2147483647, 14, -16384),

    gen_rimm_value_test( "slli", 32769, 11, 67110912 ),
    gen_rimm_value_test( "slli", -32769, 12, -134221824 ),

    gen_rimm_value_test( "slli", 0, 1, 0 ),
    gen_rimm_value_test( "slli", 1000, 1, 2000 ),
    gen_rimm_value_test( "slli", -100, 1, -200 ),
    
    gen_rimm_value_test( "slli", 1, 31, 2147483648 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src  = Bits( 32, random.randint(0,0xffffffff) )
    imm  = Bits( 12, random.randint(0,31) )
    dest = src << sext(imm,32)
    asm_code.append( gen_rimm_value_test( "slli", src.uint(), imm.uint(), dest.uint() ) )
  return asm_code
