`timescale 1ns/1ps

// NOT gate: CMOS implementation
module not_gate(output Y, input A);
  supply1 vdd;
  supply0 gnd;

  pmos p1(Y, vdd, A);    // P-type: A=0 -> pull up
  nmos n1(Y, gnd, A);    // N-type: A=1 -> pull down
endmodule

// NAND gate: CMOS implementation (2-input)
module nand_gate(output Y, input A, B);
  supply1 vdd;
  supply0 gnd;

  wire n_mid;

  // Pull-up network (parallel pMOS)
  pmos p1(Y, vdd, A);ㅐ
  pmos p2(Y, vdd, B);

  // Pull-down network (series nMOS)
  nmos n1(n_mid, gnd, B);
  nmos n2(Y, n_mid, A);
endmodule

// AND gate = NAND followed by NOT
module and_gate(output Y, input A, B);
  wire nand_out;
  nand_gate nand1(nand_out, A, B);
  not_gate not1(Y, nand_out);
endmodule

// XOR gate: CMOS-based from basic gates
module xor_gate(output Y, input A, B);
  wire na, nb, a1, a2;

  not_gate n1(na, A);
  not_gate n2(nb, B);
  and_gate a_and1(a1, A, nb);
  and_gate a_and2(a2, na, B);
  or_gate  o1(Y, a1, a2);
endmodule

// OR gate: CMOS implementation using DeMorgan = ~(~A & ~B)
module or_gate(output Y, input A, B);
  wire na, nb, nand_out;
  not_gate n1(na, A);
  not_gate n2(nb, B);
  nand_gate nand1(nand_out, na, nb);
  not_gate not1(Y, nand_out);
endmodule

// 1-bit Full Adder
module full_adder(output Sum, output Cout, input A, B, Cin);
  wire s1, c1, c2;

  xor_gate x1(s1, A, B);
  xor_gate x2(Sum, s1, Cin);

  and_gate a1(c1, A, B);
  and_gate a2(c2, s1, Cin);
  or_gate  o1(Cout, c1, c2);
endmodule

// 32-bit Subtractor (a - b = a + (~b + 1))
module substractor(output [31:0] s1, input [31:0] a, b);
  wire [31:0] b_inv;
  wire [31:0] sum;
  wire [31:0] c;

  genvar i;
  generate
    for (i = 0; i < 32; i = i + 1) begin
      not_gate inv(b_inv[i], b[i]);
    end
  endgenerate

  full_adder fa0(sum[0], c[0], a[0], b_inv[0], 1'b1);
  generate
    for (i = 1; i < 32; i = i + 1) begin : adder_loop
      full_adder fa(sum[i], c[i], a[i], b_inv[i], c[i-1]);
    end
  endgenerate

  assign s1 = sum;
endmodule
