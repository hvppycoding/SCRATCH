`timescale 1ns/1ps

// NOT gate using tranif1
module not_gate(output Y, input A);
  supply1 vdd;
  supply0 gnd;
  wire w;
  tranif1 t1(w, gnd, A);
  tranif1 t2(Y, vdd, w);
endmodule

// AND gate using tranif1
module and_gate(output Y, input A, B);
  supply1 vdd;
  wire w;
  tranif1 t1(w, vdd, A);
  tranif1 t2(Y, w, B);
endmodule

// OR gate using tranif1
module or_gate(output Y, input A, B);
  supply1 vdd;
  wire w1, w2;
  tranif1 t1(w1, vdd, A);
  tranif1 t2(w2, vdd, B);
  tranif1 t3(Y, w1, A);
  tranif1 t4(Y, w2, B);
endmodule

// XOR gate using basic logic gates
module xor_gate(output Y, input A, B);
  wire na, nb, w1, w2;
  not_gate n1(na, A);
  not_gate n2(nb, B);
  and_gate a1(w1, A, nb);
  and_gate a2(w2, na, B);
  or_gate  o1(Y, w1, w2);
endmodule

// 1-bit Full Adder
module full_adder(output Sum, output Cout, input A, B, Cin);
  wire w1, w2, w3;
  xor_gate x1(w1, A, B);
  xor_gate x2(Sum, w1, Cin);
  and_gate a1(w2, A, B);
  and_gate a2(w3, w1, Cin);
  or_gate  o1(Cout, w2, w3);
endmodule

// 32-bit Full Adder
module full_adder_32(output [31:0] S, input [31:0] A, B, input Cin);
  wire [31:0] C;
  genvar i;
  generate
    for (i = 0; i < 32; i = i + 1) begin : fa_loop
      if (i == 0)
        full_adder fa(S[i], C[i], A[i], B[i], Cin);
      else
        full_adder fa(S[i], C[i], A[i], B[i], C[i-1]);
    end
  endgenerate
endmodule

// 32-bit Subtractor using 2's complement
module substractor(output [31:0] S, input [31:0] A, B);
  wire [31:0] B_inv;
  genvar i;
  generate
    for (i = 0; i < 32; i = i + 1)
      not_gate inv(B_inv[i], B[i]);
  endgenerate
  full_adder_32 adder(S, A, B_inv, 1'b1);  // A + (~B + 1)
endmodule
