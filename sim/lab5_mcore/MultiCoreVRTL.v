//========================================================================
// 1-Core Processor-Cache-Network
//========================================================================

`ifndef LAB5_MCORE_MULTI_CORE_V
`define LAB5_MCORE_MULTI_CORE_V

`include "vc/mem-msgs.v"
`include "vc/trace.v"
`include "lab5_mcore/McoreDataCacheVRTL.v"
`include "lab5_mcore/MemNetVRTL.v"

`include "lab2_proc/ProcAltVRTL.v"
`include "lab3_mem/BlockingCacheAltVRTL.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include components
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab5_mcore_MultiCoreVRTL
(
  input  logic                       clk,
  input  logic                       reset,

  input  logic [c_num_cores-1:0][31:0] mngr2proc_msg,
  input  logic [c_num_cores-1:0]       mngr2proc_val,
  output logic [c_num_cores-1:0]       mngr2proc_rdy,

  output logic [c_num_cores-1:0][31:0] proc2mngr_msg,
  output logic [c_num_cores-1:0]       proc2mngr_val,
  input  logic [c_num_cores-1:0]       proc2mngr_rdy,

  output mem_req_16B_t                 imemreq_msg,
  output logic                         imemreq_val,
  input  logic                         imemreq_rdy,

  input  mem_resp_16B_t                imemresp_msg,
  input  logic                         imemresp_val,
  output logic                         imemresp_rdy,

  output mem_req_16B_t                 dmemreq_msg,
  output logic                         dmemreq_val,
  input  logic                         dmemreq_rdy,

  input  mem_resp_16B_t                dmemresp_msg,
  input  logic                         dmemresp_val,
  output logic                         dmemresp_rdy,

  //  Only takes Core 0's stats_en to the interface
  output logic                         stats_en,
  output logic [c_num_cores-1:0]       commit_inst,
  output logic [c_num_cores-1:0]       icache_miss,
  output logic [c_num_cores-1:0]       icache_access,
  output logic [c_num_cores-1:0]       dcache_miss,
  output logic [c_num_cores-1:0]       dcache_access
);

  localparam c_num_cores = 4;

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Instantiate modules and wires
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

///Proc Wires
mem_req_4B_t [c_num_cores-1:0]	imem_req_msg;
logic [c_num_cores-1:0]		 	imem_req_val;
logic [c_num_cores-1:0]		 	imem_req_rdy;

mem_resp_4B_t [c_num_cores-1:0]	imem_resp_msg;
logic [c_num_cores-1:0]		 	imem_resp_val;
logic [c_num_cores-1:0]		 	imem_resp_rdy;

mem_req_4B_t [c_num_cores-1:0]	dmem_req_msg;
logic [c_num_cores-1:0]		 	dmem_req_val;
logic [c_num_cores-1:0]		 	dmem_req_rdy;

mem_resp_4B_t [c_num_cores-1:0]	dmem_resp_msg;
logic [c_num_cores-1:0]		 	dmem_resp_val;
logic [c_num_cores-1:0]		 	dmem_resp_rdy;

logic [c_num_cores-1:0]			ext_stats_en;
assign stats_en = ext_stats_en[0];

//-------------------------
// Cache Wires to Proc
mem_req_4B_t [c_num_cores-1:0]	cache_req_msg;
logic [c_num_cores-1:0]		 	cache_req_val;
logic [c_num_cores-1:0]		 	cache_req_rdy;

mem_resp_4B_t [c_num_cores-1:0]	cache_resp_msg;
logic [c_num_cores-1:0]		 	cache_resp_val;
logic [c_num_cores-1:0]		 	cache_resp_rdy;

//Cache <-> Proc assign statement
assign cache_req_msg = imem_req_msg;
assign cache_req_val = imem_req_val;
assign imem_req_rdy  = cache_req_rdy;

assign imem_resp_msg  = cache_resp_msg;
assign imem_resp_val  = cache_resp_val;
assign cache_resp_rdy = imem_resp_rdy;

logic [c_num_cores-1:0][31:0] Num_Cores;
assign Num_Cores[0] = 32'd0;
assign Num_Cores[1] = 32'd1;
assign Num_Cores[2] = 32'd2;
assign Num_Cores[3] = 32'd3;

genvar i;
generate
	for(i=0; i<4; i++) begin: CORES_CACHES


	lab2_proc_ProcAltVRTL
	#(
		.p_num_cores (4)	
	) proc
	  (
		.clk           (clk),
		.reset         (reset),

		.core_id       (Num_Cores[i]),

		.imemreq_msg   (imem_req_msg[i]),	//output
		.imemreq_val   (imem_req_val[i]),	//output
		.imemreq_rdy   (imem_req_rdy[i]),	//input

		.imemresp_msg  (imem_resp_msg[i]),	//input
		.imemresp_val  (imem_resp_val[i]),	//input
		.imemresp_rdy  (imem_resp_rdy[i]),	//output

		.dmemreq_msg   (dmem_req_msg[i]),	//output
		.dmemreq_val   (dmem_req_val[i]),	//ouput
		.dmemreq_rdy   (dmem_req_rdy[i]),	//input

		.dmemresp_msg  (dmem_resp_msg[i]),	//input
		.dmemresp_val  (dmem_resp_val[i]),	//input
		.dmemresp_rdy  (dmem_resp_rdy[i]),	//ouput

		.mngr2proc_msg (mngr2proc_msg[i]),	//input
		.mngr2proc_val (mngr2proc_val[i]),	//input
		.mngr2proc_rdy (mngr2proc_rdy[i]),	//output

		.proc2mngr_msg (proc2mngr_msg[i]),	//output
		.proc2mngr_val (proc2mngr_val[i]),	//output
		.proc2mngr_rdy (proc2mngr_rdy[i]),	//input

		.stats_en      (ext_stats_en[i]),
		.commit_inst   (commit_inst[i])
	  );

	//Cache
	lab3_mem_BlockingCacheAltVRTL
	  #(
		.p_num_banks   (1)
	  )
	  icache
	  (
		.clk           (clk),
		.reset         (reset),

		.cachereq_msg  (cache_req_msg[i]),	//input
		.cachereq_val  (cache_req_val[i]),	//input
		.cachereq_rdy  (cache_req_rdy[i]),	//output

		.cacheresp_msg (cache_resp_msg[i]),	//output
		.cacheresp_val (cache_resp_val[i]),	//output
		.cacheresp_rdy (cache_resp_rdy[i]),	//input

		.memreq_msg    (memreq_msg[i]),		//output
		.memreq_val    (memreq_val[i]),		//output
		.memreq_rdy    (memreq_rdy[i]),		//input

		.memresp_msg   (memresp_msg[i]),	//input
		.memresp_val   (memresp_val[i]),	//input
		.memresp_rdy   (memresp_rdy[i])		//output

	  );
	end
endgenerate

//MemNet
//MemNet wires to Cache
mem_req_16B_t 	[c_num_cores-1:0] memreq_msg;
logic 			[c_num_cores-1:0] memreq_val;
logic 			[c_num_cores-1:0] memreq_rdy;

mem_resp_16B_t 	[c_num_cores-1:0] memresp_msg;
logic 			[c_num_cores-1:0] memresp_val;
logic 			[c_num_cores-1:0] memresp_rdy;

mem_req_16B_t	[c_num_cores-1:0]	ext_imemreq_msg;
logic			[c_num_cores-1:0]	ext_imemreq_val;
logic			[c_num_cores-1:0]	ext_imemreq_rdy;

mem_resp_16B_t	[c_num_cores-1:0]	ext_imemresp_msg;
logic			[c_num_cores-1:0]	ext_imemresp_val;
logic			[c_num_cores-1:0]	ext_imemresp_rdy;


assign imemreq_msg = ext_imemreq_msg[0];			//out
assign imemreq_val = ext_imemreq_val[0];			//out
assign ext_imemreq_rdy[0] = imemreq_rdy;			//in

assign ext_imemresp_msg[0] = imemresp_msg;			//in
assign ext_imemresp_val[0] = imemresp_val;			//in
assign imemresp_rdy        = ext_imemresp_rdy[0];	//out



lab5_mcore_MemNetVRTL MemNet
(
  .clk(clk),
  .reset(reset),

  .memreq_msg(memreq_msg),
  .memreq_val(memreq_val),
  .memreq_rdy(memreq_rdy),

  .memresp_msg(memresp_msg),
  .memresp_val(memresp_val),
  .memresp_rdy(memresp_rdy),

  .mainmemreq_msg(ext_imemreq_msg),
  .mainmemreq_val(ext_imemreq_val),
  .mainmemreq_rdy(ext_imemreq_rdy),

  .mainmemresp_msg(ext_imemresp_msg),
  .mainmemresp_val(ext_imemresp_val),
  .mainmemresp_rdy(ext_imemresp_rdy)
);

//DataCache

mem_req_4B_t [c_num_cores-1:0]	procreq_msg;
logic [c_num_cores-1:0]		 	procreq_val;
logic [c_num_cores-1:0]		 	procreq_rdy;

mem_resp_4B_t [c_num_cores-1:0]	procresp_msg;
logic [c_num_cores-1:0]		 	procresp_val;
logic [c_num_cores-1:0]		 	procresp_rdy;

assign procreq_msg  = dmem_req_msg;
assign procreq_val  = dmem_req_val;
assign dmem_req_rdy = procreq_rdy;

assign dmem_resp_msg = procresp_msg;
assign dmem_resp_val = procresp_val;
assign procresp_rdy  = dmem_resp_rdy;

lab5_mcore_McoreDataCacheVRTL dcache
(
  .clk(clk),
  .reset(reset),

  .procreq_msg(procreq_msg),	//input
  .procreq_val(procreq_val),	//input
  .procreq_rdy(procreq_rdy),	//output

  .procresp_msg(procresp_msg),	//output
  .procresp_val(procresp_val),	//output
  .procresp_rdy(procresp_rdy),	//input

  .mainmemreq_msg(dmemreq_msg),
  .mainmemreq_val(dmemreq_val),
  .mainmemreq_rdy(dmemreq_rdy),

  .mainmemresp_msg(dmemresp_msg),
  .mainmemresp_val(dmemresp_val),
  .mainmemresp_rdy(dmemresp_rdy),

  // Ports used for statistics gathering
  .dcache_miss(dcache_miss),			
  .dcache_access(dcache_access)
);

  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: Instantiate caches and connect them to cores
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''



  // Only takes proc0's stats_en
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // LAB TASK: hook up stats and add icache stats
  //''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  //assign commit_inst   = proc_commit_inst;
  assign icache_miss   = cache_resp_val & cache_resp_rdy & ~{cache_resp_msg[0].test[0], cache_resp_msg[1].test[0], cache_resp_msg[2].test[0], cache_resp_msg[3].test[0]};
  assign icache_access = cache_req_val  & cache_req_rdy;
  assign dcache_miss   = procresp_val & procresp_rdy & ~{procresp_msg[0].test[0], procresp_msg[1].test[0], procresp_msg[2].test[0], procresp_msg[3].test[0]};
  assign dcache_access = procreq_val  & procreq_rdy;


//
  `VC_TRACE_BEGIN
  begin

    // This is staffs' line trace, which assume the processors and icaches
    // are instantiated in using generate statement, and the data cache
    // system is instantiated with the name dcache. You can add net to the
    // line trace.
    // Feel free to revamp it or redo it based on your need.

    CORES_CACHES[0].icache.line_trace( trace_str );
    CORES_CACHES[0].proc.line_trace( trace_str );
    CORES_CACHES[1].icache.line_trace( trace_str );
    CORES_CACHES[1].proc.line_trace( trace_str );
    CORES_CACHES[2].icache.line_trace( trace_str );
    CORES_CACHES[2].proc.line_trace( trace_str );
    CORES_CACHES[3].icache.line_trace( trace_str );
    CORES_CACHES[3].proc.line_trace( trace_str );

    dcache.line_trace( trace_str );
  end
  `VC_TRACE_END

endmodule

`endif /* LAB5_MCORE_MULTI_CORE_V */
