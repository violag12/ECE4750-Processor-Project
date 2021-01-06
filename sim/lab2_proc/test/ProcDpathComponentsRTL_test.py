#=========================================================================
# ProcDpathComponentsRTL_test.py
#=========================================================================

import pytest
import random

from pymtl      import *
from harness    import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import run_test_vector_sim

from lab2_proc.ProcDpathComponentsRTL import ImmGenRTL
from lab2_proc.ProcDpathComponentsRTL import AluRTL

#-------------------------------------------------------------------------
# ImmGenRTL
#-------------------------------------------------------------------------

def test_immgen( test_verilog, dump_vcd ):

  header_str = \
  ( "imm_type", "inst",
    "imm*" )
  
  run_test_vector_sim( ImmGenRTL(), [ header_str,
    # imm_type inst                                imm
    [ 0,       0b11111111111100000000000000000000, 0b11111111111111111111111111111111], # I-imm
    [ 0,       0b00000000000011111111111111111111, 0b00000000000000000000000000000000], # I-imm
    [ 0,       0b01111111111100000000000000000000, 0b00000000000000000000011111111111], # I-imm
    [ 0,       0b11111111111000000000000000000000, 0b11111111111111111111111111111110], # I-imm
    [ 1,       0b11111110000000000000111110000000, 0b11111111111111111111111111111111], # S-imm
    [ 1,       0b00000001111111111111000001111111, 0b00000000000000000000000000000000], # S-imm
    [ 1,       0b01111110000000000000111110000000, 0b00000000000000000000011111111111], # S-imm
    [ 1,       0b11111110000000000000111100000000, 0b11111111111111111111111111111110], # S-imm
    [ 2,       0b11111110000000000000111110000000, 0b11111111111111111111111111111110], # B-imm
    [ 2,       0b00000001111111111111000001111111, 0b00000000000000000000000000000000], # B-imm
    [ 2,       0b11000000000000000000111100000000, 0b11111111111111111111010000011110], # B-imm
    [ 3,       0b11111111111111111111000000000000, 0b11111111111111111111000000000000], # U-imm
    [ 3,       0b00000000000000000000111111111111, 0b00000000000000000000000000000000], # U-imm
    [ 4,       0b11111111111111111111000000000000, 0b11111111111111111111111111111110], # J-imm
    [ 4,       0b00000000000000000001111111111111, 0b00000000000000000001000000000000], # J-imm
    [ 4,       0b01000000000010011001000000000000, 0b00000000000010011001010000000000], # J-imm
  ], dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# AluRTL
#-------------------------------------------------------------------------

def test_alu_add( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   0,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   0,  0x0ffbc964,   '?',      '?',       '?'      ],
    #pos-neg
    [ 0x00132050,   0xd6620040,   0,  0xd6752090,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   0,  0xfff0e890,   '?',      '?',       '?'      ],
    # neg-neg
    [ 0xfeeeeaa3,   0xf4650000,   0,  0xf353eaa3,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

#''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Add more ALU function tests
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def test_alu_sub( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*                  ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   1,  0x00000000,           '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   1,  0x0ff9835c,           '?',      '?',       '?'      ],
    #pos-neg
    [ 0x00000001,   0xffffffff,   1,  0x00000002,           '?',      '?',       '?'      ],
    #neg-pos
    [ 0xffff8000,   0x7fffffff,   1,  0x7fff8001,           '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   1,  0xfff05ff0,           '?',      '?',       '?'      ],
    # neg-neg
    [ 0xfeeeeaa3,   0xf4650000,   1,  0x0a89eaa3,           '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_and( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   2,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   2,  0x00002200,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,   2,  0x00020040,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   2,  0x00000440,   '?',      '?',       '?'      ],
    [ 0xffffffff,   0xffffffff,   2,  0xffffffff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )  

def test_alu_or( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   3,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   3,  0x0ffba764,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,   3,  0xd6732050,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   3,  0xfff0e450,   '?',      '?',       '?'      ],
    [ 0xffffffff,   0xffffffff,   3,  0xffffffff,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_xor( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   4,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   4,  0x0ffb8564,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,   4,  0xd6712010,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   4,  0xfff0e010,   '?',      '?',       '?'      ],
    [ 0xffffffff,   0xffffffff,   4,  0x00000000,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_sra( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x00000001,   0x00000001,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0xfffffffd,   0x00000007,   5,  0xffffffff,   '?',      '?',       '?'      ],
    
    [ 0x00000000,   0x0000000e,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00000000,   5,  0x80000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x0000000e,   5,  0xfffe0000,   '?',      '?',       '?'      ],
    
    [ 0x00007fff,   0x00000000,   5,  0x00007fff,   '?',      '?',       '?'      ],
    [ 0x0fffffff,   0x00000000,   5,  0x0fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x0000000e,   5,  0x0001ffff,   '?',      '?',       '?'      ],
    
    [ 0x80000000,   0x0000000c,   5,  0xfff80000,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x0000000c,   5,  0x0007ffff,   '?',      '?',       '?'      ],
    
    [ 0x00000000,   0x00000001,   5,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x000003e8,   0x00000001,   5,  0x000001f4,   '?',      '?',       '?'      ],
    [ 0xffffff9c,   0x00000001,   5,  0xffffffce,   '?',      '?',       '?'      ],

  ], dump_vcd, test_verilog )
  
def test_alu_srl( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x00000001,   0x00000001,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0xfffffffd,   0x00000007,   6,  0x01ffffff,   '?',      '?',       '?'      ],
    
    [ 0x00000000,   0x0000000e,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00000000,   6,  0x80000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x0000000e,   6,  0x00020000,   '?',      '?',       '?'      ],
    
    [ 0x00007fff,   0x00000000,   6,  0x00007fff,   '?',      '?',       '?'      ],
    [ 0x0fffffff,   0x00000000,   6,  0x0fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x0000000e,   6,  0x0001ffff,   '?',      '?',       '?'      ],
    
    [ 0x00008001,   0x0000000b,   6,  0x00000010,   '?',      '?',       '?'      ],
    [ 0xffff7fff,   0x0000000c,   6,  0x000ffff7,   '?',      '?',       '?'      ],

    [ 0x00000000,   0x00000001,   6,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x000003e8,   0x00000001,   6,  0x000001f4,   '?',      '?',       '?'      ],
    [ 0xffffff9c,   0x00000001,   6,  0x7fffffce,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_sll( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   7,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x00000001,   0x00000001,   7,  0x00000002,   '?',      '?',       '?'      ],
    [ 0xfffffffd,   0x00000007,   7,  0xfffffe80,   '?',      '?',       '?'      ],
                                  
    [ 0x00000000,   0x0000000e,   7,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x00000000,   7,  0x80000000,   '?',      '?',       '?'      ],
    [ 0x80000000,   0x0000000e,   7,  0x00000000,   '?',      '?',       '?'      ],
                                  
    [ 0x00007fff,   0x00000000,   7,  0x00007fff,   '?',      '?',       '?'      ],
    [ 0x0fffffff,   0x00000000,   7,  0x0fffffff,   '?',      '?',       '?'      ],
    [ 0x7fffffff,   0x0000000e,   7,  0xffffc000,   '?',      '?',       '?'      ],
                                  
    [ 0x00008001,   0x0000000b,   7,  0x04000800,   '?',      '?',       '?'      ],
    [ 0xffff7fff,   0x0000000c,   7,  0xf7fff000,   '?',      '?',       '?'      ],
                                  
    [ 0x00000000,   0x00000001,   7,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x000003e8,   0x00000001,   7,  0x000007d0,   '?',      '?',       '?'      ],
    [ 0xffffff9c,   0x00000001,   7,  0xffffff38,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_slt( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   8,  0x00000000,   '?',       '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   8,  0x00000000,   '?',       '?',       '?'      ],
    [ 0x00132050,   0xd6620040,   8,  0x00000000,   '?',       '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   8,  0x00000001,   '?',       '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,   8,  0x00000000,   '?',       '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_sltu( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   9,  0x00000000,   '?',        '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,   9,  0x00000000,   '?',        '?',       '?'      ],
    [ 0x00132050,   0xd6620040,   9,  0x00000001,   '?',        '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,   9,  0x00000000,   '?',        '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,   9,  0x00000000,   '?',        '?',       '?'      ],
  ], dump_vcd, test_verilog )
  
def test_alu_jalr( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,   10,  0x00000000,   '?',        '?',       '?'      ],
    [ 0x0ffaa660,   0x00000304,   10,  0x0ffaa964,   '?',        '?',       '?'      ],
    [ 0x00132050,   0x00000045,   10,  0x00132094,   '?',        '?',       '?'      ],
    [ 0xfff0a440,   0x00000fff,   10,  0xfff0b43e,   '?',        '?',       '?'      ],
    [ 0xfeeeeaa3,   0x000004de,   10,  0xfeeeef80,   '?',        '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_cp_op0( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  11,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,  11,  0x0ffaa660,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,  11,  0x00132050,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,  11,  0xfff0a440,   '?',      '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  11,  0xfeeeeaa3,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_cp_op1( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  12,  0x00000000,   '?',      '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,  12,  0x00012304,   '?',      '?',       '?'      ],
    [ 0x00132050,   0xd6620040,  12,  0xd6620040,   '?',      '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,  12,  0x00004450,   '?',      '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  12,  0xf4650000,   '?',      '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_equality( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  14,  0x00000000,   1,        '?',       '?'      ],
    [ 0x0ffaa660,   0x00012304,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0x00132050,   0xd6620040,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0xfff0a440,   0x00004450,  14,  0x00000000,   0,        '?',       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  14,  0x00000000,   0,        '?',       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_lt( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  14,  0x00000000,   '?',        0,       '?'      ],
    [ 0x0ffaa660,   0x00012304,  14,  0x00000000,   '?',        0,       '?'      ],
    [ 0x00132050,   0xd6620040,  14,  0x00000000,   '?',        0,       '?'      ],
    [ 0xfff0a440,   0x00004450,  14,  0x00000000,   '?',        1,       '?'      ],
    [ 0xfeeeeaa3,   0xf4650000,  14,  0x00000000,   '?',        0,       '?'      ],
  ], dump_vcd, test_verilog )

def test_alu_fn_ltu( dump_vcd, test_verilog ):
  run_test_vector_sim( AluRTL(), [
    ('in0           in1           fn  out*          ops_eq*   ops_lt*  ops_ltu*'),
    [ 0x00000000,   0x00000000,  14,  0x00000000,   '?',        '?',        0      ],
    [ 0x0ffaa660,   0x00012304,  14,  0x00000000,   '?',        '?',        0      ],
    [ 0x00132050,   0xd6620040,  14,  0x00000000,   '?',        '?',        1      ],
    [ 0xfff0a440,   0x00004450,  14,  0x00000000,   '?',        '?',        0      ],
    [ 0xfeeeeaa3,   0xf4650000,  14,  0x00000000,   '?',        '?',        0      ],
  ], dump_vcd, test_verilog )
