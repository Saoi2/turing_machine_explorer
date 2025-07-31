#! start boot1.A
# Based on the NQL register machine:
# <https://github.com/sorear/metamath-turing-machines>
#
# boot1 isn't quite BB(5) but leaves the PC root in a good state for the
# transition from boot2 into the main loop.
#
# dispatch won't actually find the actual PC root to start with, but that's
# okay because the cell it identifies as the root will result in the decision
# tree reaching boot2.
# boot2 will slowly reduce the length of PC while alternating between
# reg.0.inc and reg.0.dec.
# A successful register decrement adds a register to the register file
# as a side-effect. (This actually saves half a state over not having the side-effect)
# The boot2 process ends once the PC overflows into 11 at the start of the
# decision tree, leaving the rest of PC as 0's, and creating ~ 1900 registers.

boot1.A 0 1 R boot1.B
boot1.A 1 1 L boot1.C
boot1.B 0 0 L boot1.A
boot1.B 1 0 L boot1.D
boot1.C 0 1 L boot1.A
boot1.C 1 1 R reg.0.inc
boot1.D 0 1 L boot1.B
boot1.D 1 1 R boot1.E
boot1.E 0 0 R boot1.D
boot1.E 1 0 R boot1.B
boot2.0 1 1 R boot2.1
boot2.1 0 0 R boot2.0
boot2.1 1 1 R boot2.2
boot2.2 0 0 R reg.0.inc
boot2.2 1 1 R reg.0.dec
dispatch 0 0 L dispatch
dispatch 1 1 L dispatch.9
dispatch.0 0 0 L root.find_pc
dispatch.0 1 1 L dispatch.0
dispatch.1 0 0 L dispatch.0
dispatch.1 1 1 L dispatch.1
dispatch.2 0 0 L dispatch.1
dispatch.2 1 1 L dispatch.2
dispatch.3 0 0 L dispatch.2
dispatch.3 1 1 L dispatch.3
dispatch.4 0 0 L dispatch.3
dispatch.4 1 1 L dispatch.4
dispatch.5 0 0 L dispatch.4
dispatch.5 1 1 L dispatch.5
dispatch.6 0 0 L dispatch.5
dispatch.6 1 1 L dispatch.6
dispatch.7 0 0 L dispatch.6
dispatch.7 1 1 L dispatch.7
dispatch.8 0 0 L dispatch.7
dispatch.8 1 1 L dispatch.8
dispatch.9 0 0 L dispatch.8
dispatch.9 1 1 L dispatch.9
jump_0_1 1 0 L dispatch
main[0] 0 0 R reg.0.dec
main[0] 1 1 R halt
main[] 0 0 R main[0]
main[] 1 1 R reg.0.inc
pc.inc 0 1 R reg.cleanup_1
pc.inc 1 0 L pc.inc
reg.-1.dec_2 0 0 R reg.-2.dec_2
reg.-1.dec_2 1 1 R reg.-1.dec_2
reg.-1.inc_2 0 0 R reg.-2.inc_2
reg.-1.inc_2 1 1 R reg.-1.inc_2
reg.-2.dec_2 0 1 L reg.return_2_1
reg.-2.dec_2 1 0 R reg.dec.check
reg.-2.inc_2 0 1 R reg.inc.shift_1
reg.-2.inc_2 1 1 R reg.-2.inc_2
reg.0.dec 0 1 R reg.prep_1
reg.0.dec 1 0 R reg.0.dec_2
reg.0.dec_2 0 0 R reg.-1.dec_2
reg.0.dec_2 1 1 R reg.0.dec_2
reg.0.inc 0 1 R reg.prep_1
reg.0.inc 1 0 R reg.0.inc_2
reg.0.inc_2 0 0 R reg.-1.inc_2
reg.0.inc_2 1 1 R reg.0.inc_2
reg.1.inc 0 1 R reg.prep_1
reg.1.inc 1 0 R reg.1.inc_2
reg.1.inc_2 0 0 R reg.0.inc_2
reg.1.inc_2 1 1 R reg.1.inc_2
reg.2.inc 0 1 R reg.prep_1
reg.2.inc 1 0 R reg.2.inc_2
reg.2.inc_2 0 0 R reg.1.inc_2
reg.2.inc_2 1 1 R reg.2.inc_2
reg.cleanup_1 0 0 R reg.cleanup_1
reg.cleanup_1 1 0 R reg.cleanup_2
reg.cleanup_2 0 0 L reg.cleanup_3
reg.cleanup_2 1 0 R reg.cleanup_2
reg.cleanup_3 0 1 L dispatch
reg.dec.check 0 0 L reg.-2.dec_2
reg.dec.check 1 1 R reg.dec.scan_1
reg.dec.scan_1 1 1 R reg.dec.scan_1
reg.dec.scan_1 0 0 R reg.dec.scan_2
reg.dec.scan_2 0 0 L reg.dec.shift_1
reg.dec.scan_2 1 1 R reg.dec.scan_1
reg.dec.shift_1 0 1 L reg.dec.shift_2
reg.dec.shift_1 1 1 L reg.dec.shift_1
reg.dec.shift_2 0 0 L reg.return_1_1
reg.dec.shift_2 1 0 L reg.dec.shift_1
reg.inc.shift_1 0 0 L reg.return_1_1
reg.inc.shift_1 1 0 R reg.inc.shift_2
reg.inc.shift_2 0 1 R reg.inc.shift_1
reg.inc.shift_2 1 1 R reg.inc.shift_2
reg.prep_1 0 0 R reg.prep_2
reg.prep_2 0 1 R reg.prep_2
reg.prep_2 1 1 L dispatch
reg.return_1_1 0 0 L reg.return_1_2
reg.return_1_1 1 1 L reg.return_1_1
reg.return_1_2 0 0 L pc.inc
reg.return_1_2 1 1 L reg.return_1_1
reg.return_2_1 0 0 L reg.return_2_2
reg.return_2_1 1 1 L reg.return_2_1
reg.return_2_2 0 0 L reg.return_2_3
reg.return_2_2 1 1 L reg.return_2_1
reg.return_2_3 0 0 L pc.inc
reg.return_2_3 1 0 L pc.inc
root.find_pc 0 0 R root.find_pc
root.find_pc 1 1 R root[]
root[] 0 0 R boot2.0
