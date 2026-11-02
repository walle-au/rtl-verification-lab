// Combinational ALU
// op | operation
// ---+---------------------------
//  0 | ADD  a + b      (carry out)
//  1 | SUB  a - b      (carry = borrow)
//  2 | AND
//  3 | OR
//  4 | XOR
//  5 | SLL  a << b[2:0]
//  6 | SRL  a >> b[2:0]
//  7 | SLT  signed a < b ? 1 : 0
module alu #(
    parameter int WIDTH = 8
) (
    input  logic [WIDTH-1:0] a,
    input  logic [WIDTH-1:0] b,
    input  logic [2:0]       op,
    output logic [WIDTH-1:0] result,
    output logic             carry,
    output logic             zero
);
    localparam int SHW = $clog2(WIDTH);

    always_comb begin
        carry = 1'b0;
        case (op)
            3'd0: {carry, result} = {1'b0, a} + {1'b0, b};
            3'd1: {carry, result} = {1'b0, a} - {1'b0, b};
            3'd2: result = a & b;
            3'd3: result = a | b;
            3'd4: result = a ^ b;
            3'd5: result = a << b[SHW-1:0];
            3'd6: result = a >> b[SHW-1:0];
            3'd7: result = {{(WIDTH-1){1'b0}}, ($signed(a) < $signed(b))};
            default: result = '0;
        endcase
    end

    assign zero = (result == '0);

endmodule
