//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
//FILES WE INCLUDED
`include "vc/arithmetic.v"
`include "vc/muxes.v"
`include "vc/regs.v"

// ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Define datapath and control unit here.
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module DataPath
(
  input logic clk,
  input logic reset,
  
  // Data signals
  input logic [63:0] req_msg,
  output logic [31:0] resp_msg,
  
  // Control signals
  input logic a_mux_sel,
  input logic b_mux_sel,
  input logic result_mux_sel,
  input logic add_mux_sel,
  //Reg enable
  input logic result_reg_en,
  
  // Status signals
  output logic b_lsb
  );

  localparam c_nbits = 32;

  //Data signals
  logic [c_nbits-1:0] req_msg_b = req_msg[63:32];
  logic [c_nbits-1:0] req_msg_a = req_msg[31:0];

  //A MUX
  logic [c_nbits-1:0] a_shifted;      //IN
  logic [c_nbits-1:0] a_mux_output;   //OUT

  vc_Mux2 #(c_nbits) A_mux(
  .in0(a_shifted),
  .in1(req_msg_a),
  .sel(a_mux_sel),
  .out(a_mux_output)); 


  //B MUX
  logic [c_nbits-1:0] b_shifted;      //IN
  logic [c_nbits-1:0] b_mux_output;   //OUT

  vc_Mux2 #(c_nbits) B_mux(
    .in0(b_shifted),
    .in1(req_msg_b),
    .sel(b_mux_sel),
    .out(b_mux_output));

  //RESULT Mux
  logic [c_nbits-1:0] add_mux_output;     //IN
  logic [c_nbits-1:0] result_mux_output;  //OUT
  
  vc_Mux2 #(c_nbits) Result_mux(
    .in0(add_mux_output),
    .in1(32'b0),                          //c_nbits'b0??
    .sel(result_mux_sel),
    .out(result_mux_output)); 

  //ADD MUX
  logic [c_nbits-1:0] adder_output;       //IN
  logic [c_nbits-1:0] result_reg_output;  //IN
  //output of mux is initialized with RESULT MUX

  vc_Mux2 #(c_nbits) Add_mux(
    .in0(adder_output),
    .in1(result_reg_output),
    .sel(add_mux_sel),
    .out(add_mux_output)); 


  //A REG
  logic [c_nbits-1:0] a_reg_output;               //OUT
  //INPUT defined by A MUX output
  vc_Reg #(c_nbits) regA(
    .clk(clk),// on pos edge of clock q<=d 
    .q(a_reg_output), //q is data output
    .d(a_mux_output));//d is data input

  //B REG
  logic [c_nbits-1:0] b_reg_output;               //OUT
  //INPUT defined by B MUX output
  vc_Reg #(c_nbits) regB(
    .clk(clk),// on pos edge of clock q<=d 
    .q(b_reg_output), //q is data output
    .d(b_mux_output));//d is data input

  //RESULT REG
  //INPUT defined by result mux output
  //OUTPUT defined by add mux input "result_reg_output"
  vc_EnReg #(c_nbits) result_reg(
    .clk(clk),
    .reset(reset),
    .q(result_reg_output),
    .d(result_mux_output),
    .en(result_reg_en));

  //LEFT SHIFTER - USED by A
  vc_LeftLogicalShifter #(c_nbits,1) l_shift(
    .in(a_reg_output),
    .shamt(1),
    .out(a_shifted));

  //RIGHT SHIFTER - USED by B
  vc_RightLogicalShifter #(c_nbits,1) r_shift(
    .in(b_reg_output),
    .shamt(1),
    .out(b_shifted));


  vc_SimpleAdder #(c_nbits) adder(
    .in0(a_reg_output),
    .in1(result_reg_output),
    .out(adder_output));
    
  // Connect to output port
  assign b_lsb = b_reg_output[0];
  assign resp_msg = result_reg_output;
endmodule
/////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////


module ControlUnit
(
  input logic clk,
  input logic reset,

  // Dataflow signals
  input  logic req_val,	//input asking fsm if ready to accept input
  output logic req_rdy, 
  input  logic resp_rdy, //input confirming ready to accept ouput msg
  output logic resp_val,
  
  // Control signals
  output logic a_mux_sel,
  output logic b_mux_sel,
  output logic result_mux_sel,
  output logic add_mux_sel,
  //Reg enable
  output logic result_reg_en,
  
  // Data signals
  input logic b_lsb
  );
  
  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------
  localparam IDLE = 2'b0;
  localparam CALC = 2'b01;
  localparam DONE = 2'b10;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------
  logic [1:0] CurrentState;
  logic [1:0] NextState;
  
  // Counter
  logic [5:0] Counter;

  always_ff @(posedge clk) begin
    if(reset) CurrentState <= IDLE;
    else CurrentState <= NextState;
  end

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  logic req_go;
  logic resp_go;
  logic is_calc_done;

  assign req_go       = req_val  && req_rdy;
  assign resp_go      = resp_val && resp_rdy;
  // Switch out of CALC to DONE if Counter is 32
  assign is_calc_done = Counter == 6'b100000;

  always_comb begin
    // Case statement will only set  NextState to something other than CurrentState
    // Gets rid of the need for else statements
    NextState = CurrentState;
    case(CurrentState)
      IDLE: if(req_go)        NextState = CALC;
      CALC: if(is_calc_done)  NextState = DONE;
      DONE: if(resp_go)       NextState = IDLE;
      default: begin
        NextState = 'x;
      end
    endcase
  end
  
  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------
  
  localparam a_x       = 1'dx;
  localparam a_shift   = 1'd0;
  localparam a_load    = 1'd1;

  localparam b_x      = 1'dx;
  localparam b_shift  = 1'd0;
  localparam b_load   = 1'd1;
  
  localparam result_x             = 1'dx;
  localparam result_add_mux_out   = 1'd0;
  localparam result_zero          = 1'd1;

  localparam add_x                = 1'dx;
  localparam add_adder_out        = 1'd0;
  localparam add_result_reg_out   = 1'd1;
  
  task CS(
    input logic cs_req_rdy,
    input logic cs_resp_val,
    input logic cs_a_mux_sel,
    input logic cs_b_mux_sel,
    input logic cs_result_mux_sel,
    input logic cs_add_mux_sel,
    input logic cs_result_reg_en);
  begin
    req_rdy         = cs_req_rdy;
    resp_val        = cs_resp_val;
    a_mux_sel       = cs_a_mux_sel;
    b_mux_sel       = cs_b_mux_sel;
    result_mux_sel  = cs_result_mux_sel;
    add_mux_sel     = cs_add_mux_sel;
    result_reg_en   = cs_result_reg_en;
  end
  endtask
  
  // Labels for Mealy transitions
  logic do_add_shift;

  assign do_add_shift = b_lsb;

  always_comb begin
    // starting case
    CS( 0, 0, a_x, b_x, result_x, add_x, 0);
    case (CurrentState)
      // depending on state, do_add_shift, the control values select for the muxes and enable for the register, plus the
      // outputs that need to be sent to the test source/sink blocks
      //                                  req resp     a mux    b mux    result              add mux             result reg
      //                                  rdy val      sel      sel      mux sel             sel                     enable
      IDLE: begin                          
                                CS(        1,   0,   a_load,   b_load,          result_zero,              add_x,         1);
	    Counter = 6'b0;
      end
      CALC: begin 
            if (do_add_shift )  CS(        0,   0,  a_shift,  b_shift,   result_add_mux_out,      add_adder_out,         1);
            else                CS(        0,   0,  a_shift,  b_shift,   result_add_mux_out, add_result_reg_out,         0);
	    Counter = Counter + 6'b00001;
      end
      DONE:                     CS(        0,   1,     a_x,       b_x,             result_x,              add_x,         0);
      default:                  CS(       'x,  'x,     a_x,       b_x,             result_x,              add_x,        'x);

    endcase

  end
  
endmodule
//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module lab1_imul_IntMulBaseVRTL
(
  input  logic        clk,
  input  logic        reset,

  input  logic        req_val,
  output logic        req_rdy,
  input  logic [63:0] req_msg,

  output logic        resp_val,
  input  logic        resp_rdy,
  output logic [31:0] resp_msg
);

  // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Instantiate datapath and control models here and then connect them
  // together.
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//SEL bit wires
logic a_mux_sel;
logic b_mux_sel;
logic result_mux_sel;
logic add_mux_sel;
//REG enable wire
logic result_reg_en;
//extra signal
logic b_lsb;

DataPath data_path
(
    .*  
);


ControlUnit control_unit 
( 
    .*  //2 always blocks -> set nextstate and change current state
);

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%b", req_msg );
    vc_trace.append_str(trace_str, str);
    //vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Add additional line tracing using the helper tasks for
    // internal state including the current FSM state.
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    $sformat( str, "%b", data_path.a_reg_output);
    vc_trace.append_str( trace_str, str);
    vc_trace.append_str(trace_str, " ");

    $sformat( str, "%b", data_path.b_reg_output);
    vc_trace.append_str( trace_str, str);
    vc_trace.append_str(trace_str, " ");

    $sformat( str, "%b", data_path.result_reg_output);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    $sformat(str, "%d", control_unit.Counter);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    case(control_unit.CurrentState)
      control_unit.IDLE: vc_trace.append_str( trace_str, "I");

      control_unit.CALC: begin
        if(control_unit.do_add_shift)  vc_trace.append_str(trace_str, "C+ ");
        else                                vc_trace.append_str(trace_str, "C  ");
      end

      control_unit.DONE:  vc_trace.append_str(trace_str, "D");

      default:            vc_trace.append_str(trace_str, "?");

    endcase // control_unit.CurrentState

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_BASE_V */

