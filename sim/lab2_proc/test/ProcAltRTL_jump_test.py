#=========================================================================
# ProcAltRTL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcAltRTL import ProcAltRTL

#-------------------------------------------------------------------------
# jal
#-------------------------------------------------------------------------

import inst_jal

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jal.gen_basic_test        ) ,
  asm_test( inst_jal.gen_multijump_test		),
  asm_test( inst_jal.gen_dest_dep_test		),
  asm_test( inst_jal.gen_value_dep_test		),

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])

def test_jal( name, test, dump_vcd ):
  run_test( ProcAltRTL, test, dump_vcd )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def test_jal_rand_delays( dump_vcd ):
  run_test( ProcAltRTL, inst_jal.gen_value_dep_test, dump_vcd,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )
#-------------------------------------------------------------------------
# jalr
#-------------------------------------------------------------------------

import inst_jalr

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jalr.gen_basic_test    ) ,
  asm_test( inst_jalr.gen_src_dep_test	),
  asm_test( inst_jalr.gen_dest_dep_test	),
  asm_test( inst_jalr.gen_value_dep_test),

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
])

def test_jalr( name, test, dump_vcd ):
  run_test( ProcAltRTL, test, dump_vcd )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def test_jalr_rand_delays( dump_vcd ):
  run_test( ProcAltRTL, inst_jalr.gen_value_dep_test, dump_vcd,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )