#=========================================================================
# addi
#=========================================================================

import random

from pymtl      import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    csrr x1, mngr2proc, < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    addi x3, x1, 0x0004
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 9
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
    gen_rimm_dest_dep_test( 5, "addi", 500, -500, 0 ),
    gen_rimm_dest_dep_test( 4, "addi", 0, 0, 0 ),
    gen_rimm_dest_dep_test( 3, "addi", -1021241324, 10, -1021241314 ),
    gen_rimm_dest_dep_test( 2, "addi", 10, -128, -118 ),
    gen_rimm_dest_dep_test( 1, "addi", 100002, 2047, 102049 ),
    gen_rimm_dest_dep_test( 0, "addi", 0, 1202, 1202 ),
    gen_rimm_dest_dep_test( 0, "addi", -14234, -124, -14358 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "addi", 500, -500, 0 ),
    gen_rimm_src_dep_test( 4, "addi", 0, 0, 0 ),
    gen_rimm_src_dep_test( 3, "addi", -1021241324, 10, -1021241314 ),
    gen_rimm_src_dep_test( 2, "addi", 10, -128, -118 ),
    gen_rimm_src_dep_test( 1, "addi", 100002, 2047, 102049 ),
    gen_rimm_src_dep_test( 0, "addi", 0, 1202, 1202 ),
    gen_rimm_src_dep_test( 0, "addi", -14234, -124, -14358 ),
  ]                                   

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "addi", 123,   23, 146 ),
    gen_rimm_src_eq_dest_test( "addi", 123,    0, 123 ),
    gen_rimm_src_eq_dest_test( "addi", 123, -123,   0 ),
    gen_rimm_src_eq_dest_test( "addi", -22,  -32, -54 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "addi", 0, 0, 0 ),
    gen_rimm_value_test( "addi", 10, -10, 0 ),
    gen_rimm_value_test( "addi", 123323254, -10, 123323244 ),
    gen_rimm_value_test( "addi", 59000, -111, 58889 ),
    gen_rimm_value_test( "addi", -340, -5, -345 ),
    gen_rimm_value_test( "addi", 10, 0, 10 ),
    gen_rimm_value_test( "addi", -10, 0, -10 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src  = Bits( 32, random.randint(0,0xffffffff) )
    imm  = Bits( 12, random.randint(0,0xfff) )
    dest = src + sext(imm,32)
    asm_code.append( gen_rimm_value_test( "addi", src.uint(), imm.uint(), dest.uint() ) )
  return asm_code