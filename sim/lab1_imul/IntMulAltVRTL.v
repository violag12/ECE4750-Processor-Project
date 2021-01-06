//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

`ifndef LAB1_IMUL_INT_MUL_ALT_V
`define LAB1_IMUL_INT_MUL_ALT_V

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
  input logic [2:0] a_mux_sel,
  input logic [2:0] b_mux_sel,
  input logic result_mux_sel,
  input logic add_mux_sel,
  //Reg enable
  input logic result_reg_en,
  
  // Status signals
  
  output [31:0] b_reg_output,
  output [31:0] a_reg_output
  );

  localparam c_nbits = 32;

  //Data signals
  logic [c_nbits-1:0] firstHalf = req_msg[63:32];
  logic [c_nbits-1:0] secondHalf = req_msg[31:0];
  logic [c_nbits-1:0] req_msg_b;
  logic [c_nbits-1:0] req_msg_a;

  //assign the smaller value to req_msg_b and the larger value
  //req_msg_a for improved efficiency 

  assign req_msg_b = (firstHalf>=secondHalf) ? secondHalf : firstHalf;  //req_msg[63:32];
  assign req_msg_a = (firstHalf>=secondHalf) ? firstHalf : secondHalf;  //req_msg[31:0];
  

  //A MUX
  logic [c_nbits-1:0] a_shifted_1;      //IN
  logic [c_nbits-1:0] a_shifted_2;      //IN
  logic [c_nbits-1:0] a_shifted_4;      //IN
  logic [c_nbits-1:0] a_shifted_8;      //IN
  logic [c_nbits-1:0] a_shifted_16;     //IN
  logic [c_nbits-1:0] a_mux_output;   //OUT

  vc_Mux6 #(c_nbits) A_mux(
  .in0(a_shifted_1),
  .in1(a_shifted_2),
  .in2(a_shifted_4),
  .in3(a_shifted_8),
  .in4(a_shifted_16),
  .in5(req_msg_a),
  .sel(a_mux_sel),
  .out(a_mux_output)); 


  //B MUX
  logic [c_nbits-1:0] b_shifted_1;      //IN
  logic [c_nbits-1:0] b_shifted_2;      //IN
  logic [c_nbits-1:0] b_shifted_4;      //IN
  logic [c_nbits-1:0] b_shifted_8;      //IN
  logic [c_nbits-1:0] b_shifted_16;     //IN
  logic [c_nbits-1:0] b_mux_output;   //OUT

  vc_Mux6 #(c_nbits) B_mux(
    .in0(b_shifted_1),
    .in1(b_shifted_2),
    .in2(b_shifted_4),
    .in3(b_shifted_8),
    .in4(b_shifted_16),
    .in5(req_msg_b),
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
  vc_LeftLogicalShifter #(c_nbits,1) l_shift_1(
    .in(a_reg_output),
    .shamt(1),
    .out(a_shifted_1));

  vc_LeftLogicalShifter #(c_nbits,2) l_shift_2(
    .in(a_reg_output),
    .shamt(2),
    .out(a_shifted_2));

  vc_LeftLogicalShifter #(c_nbits,3) l_shift_4(
    .in(a_reg_output),
    .shamt(4),
    .out(a_shifted_4));

  vc_LeftLogicalShifter #(c_nbits,4) l_shift_8(
    .in(a_reg_output),
    .shamt(8),
    .out(a_shifted_8));

  vc_LeftLogicalShifter #(c_nbits,5) l_shift_16(
    .in(a_reg_output),
    .shamt(16),
    .out(a_shifted_16));

  //RIGHT SHIFTER - USED by B
  vc_RightLogicalShifter #(c_nbits,1) r_shift_1(
    .in(b_reg_output),
    .shamt(1),
    .out(b_shifted_1));

  vc_RightLogicalShifter #(c_nbits,2) r_shift_2(
    .in(b_reg_output),
    .shamt(2),
    .out(b_shifted_2));

  vc_RightLogicalShifter #(c_nbits,3) r_shift_4(
    .in(b_reg_output),
    .shamt(4),
    .out(b_shifted_4));

  vc_RightLogicalShifter #(c_nbits,4) r_shift_8(
    .in(b_reg_output),
    .shamt(8),
    .out(b_shifted_8));

  vc_RightLogicalShifter #(c_nbits,5) r_shift_16(
    .in(b_reg_output),
    .shamt(16),
    .out(b_shifted_16));

  //ADDER
  vc_SimpleAdder #(c_nbits) adder(
    .in0(a_reg_output),
    .in1(result_reg_output),
    .out(adder_output));
    
  assign resp_msg = result_reg_output;
endmodule
////////////////////////////////////////////////

////////////////////////////////////////////////
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
  output logic [2:0] a_mux_sel,
  output logic [2:0] b_mux_sel,
  output logic result_mux_sel,
  output logic add_mux_sel,
  //Reg enable
  output logic result_reg_en,
  
  // Data signals
  
  input logic [31:0] b_reg_output,
  input logic [31:0] a_reg_output
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
  //assign is_calc_done = Counter == 5'b11111;
  assign is_calc_done = b_reg_output == 32'b0 || a_reg_output == 32'b0;

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
  
  localparam shift_x          = 3'dx;
  localparam shift_1          = 3'd0;
  localparam shift_2          = 3'd1;
  localparam shift_4          = 3'd2;
  localparam shift_8          = 3'd3;
  localparam shift_16         = 3'd4;  
  localparam load_no_shift    = 3'd5;
  
  localparam result_x             = 1'dx;
  localparam result_add_mux_out   = 1'd0;
  localparam result_zero          = 1'd1;

  localparam add_x                = 1'dx;
  localparam add_adder_out        = 1'd0;
  localparam add_result_reg_out   = 1'd1;
  
  task CS(
    input logic cs_req_rdy,
    input logic cs_resp_val,
    input logic [2:0] cs_a_mux_sel,
    input logic [2:0] cs_b_mux_sel,
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
  logic b_lsb;

  logic shift_16_bool;
  logic shift_8_bool;
  logic shift_4_bool;
  logic shift_2_bool;

  assign b_lsb = b_reg_output[0];
  assign do_add_shift = b_lsb;

  assign shift_16_bool= b_reg_output[15:0]== 16'b0;
  assign shift_8_bool = b_reg_output[7:0] ==  8'b0;
  assign shift_4_bool = b_reg_output[3:0] ==  4'b0;
  assign shift_2_bool = b_reg_output[1:0] ==  2'b0;


  always_comb begin

    CS( 0, 0, shift_x, shift_x, result_x, add_x, 0);
    case (CurrentState)
      //                                req resp   a mux          b mux          result             add mux           result reg
      //                                rdy val    sel            sel            mux sel            sel               enable
      IDLE:                          CS( 1, 0, load_no_shift, load_no_shift,        result_zero,              add_x,     1);
      CALC: begin 
            if (do_add_shift )       CS( 0, 0, shift_1,       shift_1,       result_add_mux_out,      add_adder_out,     1);
            else if(shift_16_bool)   CS( 0, 0, shift_16,      shift_16,      result_add_mux_out, add_result_reg_out,     0);
            else if(shift_8_bool)    CS( 0, 0, shift_8,       shift_8,       result_add_mux_out, add_result_reg_out,     0);
            else if(shift_4_bool)    CS( 0, 0, shift_4,       shift_4,       result_add_mux_out, add_result_reg_out,     0);
            else if(shift_2_bool)    CS( 0, 0, shift_2,       shift_2,       result_add_mux_out, add_result_reg_out,     0);
            else                     CS( 0, 0, shift_1,       shift_1,       result_add_mux_out, add_result_reg_out,     0);
      
      end
      DONE:                          CS( 0, 1, shift_x,       shift_x,                 result_x,           add_x,        0);
      default:                       CS('x,'x, shift_x,       shift_x,                 result_x,           add_x,       'x);

    endcase

  end
  
endmodule


//=========================================================================
// Integer Multiplier Variable-Latency Implementation
//=========================================================================

module lab1_imul_IntMulAltVRTL
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
logic [2:0] a_mux_sel;
logic [2:0] b_mux_sel;
logic result_mux_sel;
logic add_mux_sel;
//REG enable wire
logic result_reg_en;
//extra signal
logic [31:0] a_reg_output;
logic [31:0] b_reg_output;

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

    $sformat( str, "%x", req_msg );
    vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

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

    $sformat(str, "%d", control_unit.b_mux_sel);
    vc_trace.append_str(trace_str, str);
    vc_trace.append_str(trace_str, " ");

    case(control_unit.CurrentState)
      control_unit.IDLE: vc_trace.append_str( trace_str, "I");

      control_unit.CALC: begin
        if(control_unit.do_add_shift)  vc_trace.append_str(trace_str, "C+ ");
        else                           vc_trace.append_str(trace_str, "C  ");
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

`endif /* LAB1_IMUL_INT_MUL_ALT_V */
