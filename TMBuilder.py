#!/usr/bin/python3

import tm
import tmdb

framework = """
#! start 0a.boot1.A
# Based on the NQL register machine:
# <https://github.com/sorear/metamath-turing-machines>
#
# States that being with a digit are the states for the framework of the
# register machine implemented in a turing machine. States that don't begin
# with a digit are the decision tree states from the subroutines and main().
#
# 0a. boot1
#
# boot1 isn't quite BB(5) but leaves the tape in a good state for boot2.
#
0a.boot1.A 0 1 R 0a.boot1.B
0a.boot1.A 1 1 L 0a.boot1.C
0a.boot1.B 0 0 L 0a.boot1.A
0a.boot1.B 1 0 L 0a.boot1.D
0a.boot1.C 0 1 L 0a.boot1.A
#
# At the end of boot1 the tape looks like this:
# 10101010101010101010101010101010101[1]01111000000000000000000000000000000
# with 1909 singleton 1s.
#
# Fortunately the right side of the tape looks like it is part way through
# a register operation so by transitioning to the right register operation
# state we can complete the operation and clean up the tape to a good state
# to start boot2.
#
0a.boot1.C 1 1 R [3.register_0.inc]
0a.boot1.D 0 1 L 0a.boot1.B
0a.boot1.D 1 1 R 0a.boot1.E
0a.boot1.E 0 0 R 0a.boot1.D
0a.boot1.E 1 0 R 0a.boot1.B
#
# 0b. boot2
#
# In boot2 we are going through dispatch and can use much of the framework
# loop to help clean up the PC and initialize the registers.
# In particular, boot2 relies on a successful decnz adding one
# register to the register file as a side-effect.
#
# The boot2 decision "tree" works a bit differently from the regular machine.
# The end of the PC alternates between:
# ...110 - increment register 0
# ...111 - decrement register 0
# boot2 scans right on the PC until encountering one of these two patterns.
#
# At the end of the boot2 phase the PC contains "11",
# there are 3822 0s between the PC and the register file,
# and the register file contains 1909 registers plus the -1 marker register.
#
0b.boot2.0 1 1 R 0b.boot2.1
0b.boot2.1 0 0 R 0b.boot2.0
0b.boot2.1 1 1 R 0b.boot2.2
0b.boot2.2 0 0 R [3.register_0.inc]
0b.boot2.2 1 1 R [3.register_0.decnz]
#
# 1. 2. 3. Register manipulation
#
# The normal form of the tape is:
#
# 11010110010010000000000000001011101010101110101100
# [ PC        ][ 0s          ]^^[ unary registers ]^
#                             |                    |
#                             -1 register          Last register terminated with 00
#
# The boundry between the PC and the 0s before the register file is
# implicit in the decision tree. The PC starts with the leftmost 1 on the tape.
#
# During a register operation the tape is modified as follows:
#
# 1a. A marker is placed at the end of the PC (handled by half of state 3.):
#
# 11010110010011000000000000001011101010101110101100
# [ PC        ]^[ 0s         ]^^[ unary registers ]^
#              |              |                    |
#              marker         -1 register          Last register terminated with 00
#
# 1b. The -1 register is extended to the left almost to the marker:
#
# 11010110010011011111111111111011101010101110101100
# [ PC        ]^ [ -1 register ][ unary registers ]^
#              |                                   |
#              marker                              Last register terminated with 00
#
# 1c. We go through dispatch again.
#
# 2a. The marker is removed from the end of the PC (handled by the other half of state 3.):
#
# 11010110010010011111111111111011101010101110101100
# [ PC        ]^ [ -1 register ][ unary registers ]^
#              |                                   |
#              00 before the -1 register           Last register terminated with 00
#
# 2b. The sepecific register operation is performed:
#
# 110101100100100111111111111110111101010101110101100
# [ PC        ]^ [ -1 register ][ unary registers  ]^
#              |                                    |
#              00 before the -1 register            Last register terminated with 00
#
# 2c. The result of the register operation is returned to the PC.
# 00 before the -1 register marks where the PC ends.
#
# 2d. The PC is adusted:
#
# 110101100101000111111111111110111101010101110101100
# [ PC        ]^ [ -1 register ][ unary registers  ]^
#              |                                    |
#              00 before the -1 register            Last register terminated with 00
#
# 2e. The -1 register is reduced back to a single 1:
#
# 110101100101000000000000000010111101010101110101100
# [ PC        ][ zeros       ]^^[ unary registers  ]^
#                             |                     |
#                             -1 register           Last register terminated with 00
#
# 2f. We are back in normal form and go back through dispatch to start executing
# the next instruction. The length of the PC may be longer or shorter for the
# next operation than for the register operation.
#
1b.reg.prep_1 0 0 R 1b.reg.prep_2
1b.reg.prep_2 0 1 R 1b.reg.prep_2
1b.reg.prep_2 1 1 L 6.continue.0
2b.reg.-1.dec 0 0 R 2b.reg.-2.dec
2b.reg.-1.dec 1 1 R 2b.reg.-1.dec
2b.reg.-1.inc 0 0 R 2b.reg.-2.inc
2b.reg.-1.inc 1 1 R 2b.reg.-1.inc
# 2b.reg.-2.dec does double duty to restore a register and return if a
# decz fails.
2b.reg.-2.dec 0 1 L 2c.reg.return_1_1
2b.reg.-2.dec 1 0 R 2b.reg.dec.check
2b.reg.-2.inc 0 1 R 2b.reg.inc.shift_1
2b.reg.-2.inc 1 1 R 2b.reg.-2.inc
2b.reg.dec.check 0 0 L 2b.reg.-2.dec
2b.reg.dec.check 1 1 R 2b.reg.dec.scan_1
2b.reg.dec.scan_1 1 1 R 2b.reg.dec.scan_1
2b.reg.dec.scan_1 0 0 R 2b.reg.dec.scan_2
2b.reg.dec.scan_2 0 0 L 2b.reg.dec.shift_1
2b.reg.dec.scan_2 1 1 R 2b.reg.dec.scan_1
2b.reg.dec.shift_1 0 1 L 2b.reg.dec.shift_2
2b.reg.dec.shift_1 1 1 L 2b.reg.dec.shift_1
2b.reg.dec.shift_2 0 0 L 2c.reg.return_0_1
2b.reg.dec.shift_2 1 0 L 2b.reg.dec.shift_1
2b.reg.inc.shift_1 0 0 L 2c.reg.return_0_1
2b.reg.inc.shift_1 1 0 R 2b.reg.inc.shift_2
2b.reg.inc.shift_2 0 1 R 2b.reg.inc.shift_1
2b.reg.inc.shift_2 1 1 R 2b.reg.inc.shift_2
2c.reg.return_0_1 0 0 L 2c.reg.return_0_2
2c.reg.return_0_1 1 1 L 2c.reg.return_0_1
2c.reg.return_0_2 0 0 L 6.break.0
2c.reg.return_0_2 1 1 L 2c.reg.return_0_1
2c.reg.return_1_1 0 0 L 2c.reg.return_1_2
2c.reg.return_1_1 1 1 L 2c.reg.return_1_1
2c.reg.return_1_2 0 0 L 6.break.1
2c.reg.return_1_2 1 1 L 2c.reg.return_1_1
2e.reg.cleanup_1 0 0 R 2e.reg.cleanup_1
2e.reg.cleanup_1 1 0 R 2e.reg.cleanup_2
2e.reg.cleanup_2 0 0 L 2e.reg.cleanup_3
2e.reg.cleanup_2 1 0 R 2e.reg.cleanup_2
2e.reg.cleanup_3 0 1 L 6.continue.0
#
# 4. dispatch
#
# Find the start of the PC. We pass by a set number of 0 cells going
# left (how many depends on the decision tree), then scan right for the
# first 1 cell.
#
4.dispatch.0 0 0 L 4.dispatch.scan
4.dispatch.0 1 1 L 4.dispatch.0
4.dispatch.scan 0 0 R 4.dispatch.scan
4.dispatch.scan 1 1 R 5.root.1
#
# 5. The root of the PC decision tree:
# 10 - in boot2 phase
# 110 - in main subroutine
# 111 - main subroutine has completed. (Loop back to 110)
#
# In the boot2 phase we may be at a false root, but due to the
# way boot2 works this doesn't cause problems.
#
5.root.1 0 0 R 0b.boot2.0
5.root.1 1 1 R 5.root.1.1
5.root.1.1 0 0 R main().0
5.root.1.1 1 0 R main().0
#
#
# 6. PC jump instructions.
#
# We don't know if we got to break.0 from phase two of a register instruction
# or not. Tranisition to the reg -1 cleanup state unconditionally. If we're
# not transitioning from a register operation this cleanup won't do anything
# and we'll end up back in dispatch regardless.
#
6.break.0 0 1 R 2e.reg.cleanup_1
6.break.0 1 0 L 6.break.0
6.break.1 0 0 L 6.break.0
6.break.1 1 0 L 6.break.1
6.continue.0 0 0 L 6.continue.0
6.continue.0 1 1 L [largest_4.dispatch]
"""



class Register(str):
    @property
    def inc(self):
        return "3." + self + ".inc"

    @property
    def dec(self):
        return "3." + self + ".dec"

    @property
    def decnz(self):
        return "3." + self + ".decnz"

class Sequence():
    def __init__(self, seq):
        self.seq = seq
        self.name = None
        self.unresolved_labels = set()

    def __repr__(self):
        if self.name:
            return f"{self.name}{self.seq}"
        else:
            return f"{self.seq}"

def subroutine(func):
    """Decorator which memoizes a method, and adds the return value to the sequences list"""

    def _wrapper(self, *args):
        new_args = tuple(self.add_sequence(v) for v in args)
        key = (func.__name__, *new_args)
        try:
            return self.memo[key]
        except KeyError:
            pass

        rv = tuple(v for v in (self.add_sequence(v2) for v2 in func(self, *new_args)) if v != ())
        self.memo[key] = rv
        subroutine_seq = self.add_sequence(rv)
        if self.sequences[subroutine_seq].name is None:
            self.sequences[subroutine_seq].name = "{}({}).0".format(func.__name__, ",".join(str(v) for v in new_args))
        else:
            self.sequences[subroutine_seq].name = "fn_{}().0".format(subroutine_seq)
        return rv

    return _wrapper



class TMBuilder:
    """Subclass this class to build a particular turing machine"""
    def __init__(self):
        self.tm = tm.TuringMachine()
        self.registers = {}
        self.nextreg = 0
        self.sequences = []
        self.sequence_lookup = {}
        self.memo = {}

    def reg(self, name):
        if name not in self.registers:
            reg = Register(name)
            self.tm.states[("2b.reg.{}.inc".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "2b.reg.{}.inc".format(self.nextreg - 1))
            self.tm.states[("2b.reg.{}.inc".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "2b.reg.{}.inc".format(self.nextreg))
            self.tm.states[("2b.reg.{}.dec".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "2b.reg.{}.dec".format(self.nextreg - 1))
            self.tm.states[("2b.reg.{}.dec".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "2b.reg.{}.dec".format(self.nextreg))
            self.tm.states[(reg.inc, "0")] = \
                tm.Transition("1", "R", "1b.reg.prep_1")
            self.tm.states[(reg.inc, "1")] = \
                tm.Transition("0", "R", "2b.reg.{}.inc".format(self.nextreg))
            self.tm.states[(reg.decnz, "0")] = \
                tm.Transition("1", "R", "1b.reg.prep_1")
            self.tm.states[(reg.decnz, "1")] = \
                tm.Transition("0", "R", "2b.reg.{}.dec".format(self.nextreg))
            self.tm.states[(reg.dec, "0")] = \
                tm.Transition("0", "R", reg.decnz)
            self.tm.states[(reg.dec, "1")] = \
                tm.Transition("0", "L", "6.break.0")
            self.nextreg = self.nextreg + 1
            self.registers[name] = reg
        return self.registers[name]

    def add_sequence(self, tree):
        while isinstance(tree, (list, tuple)) and len(tree) == 1:
            tree=tree[0]

        if not isinstance(tree, (list, tuple)) or len(tree) == 0:
            return tree

        key = tuple(v for v in (self.add_sequence(entry) for entry in tree) if v!= ())

        if len(key) == 0:
            return ()
        if len(key) == 1:
            return key[0]

        if key not in self.sequence_lookup:
            seq = Sequence(key)
            for v in key:
                if isinstance(v, int):
                    seq.unresolved_labels.update(self.sequences[v].unresolved_labels)
                elif v.startswith("break_") or v.startswith("continue_"):
                    seq.unresolved_labels.add(v.split("_", maxsplit=1)[1])

            self.sequence_lookup[key] = len(self.sequences)
            self.sequences.append(seq)

        return self.sequence_lookup[key]

    def label(self, name, seq, zeros=0, ones=0):
        control_flow = ("break_" + name, "continue_" + name)

        def contains_reference(name, seq):
            for entry in seq:
                if entry in control_flow:
                    return True
                if isinstance(entry, int) and name in self.sequences[entry].unresolved_labels:
                    return True
                if isinstance(entry, tuple) or isinstance(entry, list):
                    if contains_reference(name, entry):
                        return True
            return False

        def resolve_entry(zeros, ones, val):
            if val in control_flow:
                if val == "break_" + name:
                    return "_break.{}".format(zeros)
                else:
                    return "_continue.{}".format(ones)
            if isinstance(val, int) and name in self.sequences[val].unresolved_labels:
                rv=self.add_sequence(self.label(name, self.sequences[val].seq, zeros, ones))
                # transfer the sequence name over to the new sequence
                self.sequences[rv].name = self_sequences[val].name
                return rv
            if isinstance(val, tuple) or isinstance(val, list):
                return self.label(name, val, zeros, ones)
            return val

        if not contains_reference(name, seq):
            return seq

        if len(seq) == 2:
            return (resolve_entry(zeros + 1, ones, seq[0]),
                    resolve_entry(zeros, ones + 1, seq[1]))

        assert False, "unimplemented"

    def find_seq(self, name):
        for i in range(len(self.sequences)):
            if self.sequences[i].name == name:
                return i

    def reachable(self):
        grey = set()
        black = set()
        grey.add(self.find_seq("main().0"))

        while grey:
            i = grey.pop()
            if i not in black:
                yield i
                black.add(i)
                for v in self.sequences[i].seq:
                    if isinstance(v, int):
                        grey.add(v)

    def breakout_common_subsequences(self):

        search_len = max(len(s.seq) for s in self.sequences)

        while search_len > 1:
            subsequences = set()
            match = None
            reachable = [v for v in self.reachable()]
            for i in reachable:
                s = self.sequences[i]
                if len(s.seq) >= search_len:
                    for offset in range(len(s.seq) + 1 - search_len):
                        subseq=s.seq[offset:offset+search_len]
                        if subseq in subsequences:
                            match = subseq
                            break
                        subsequences.add(subseq)
                if match:
                    break

            if match:
                match_i = self.add_sequence(match)
                for i in reachable:
                    while True:
                        s = self.sequences[i].seq
                        if len(s) > search_len:
                            for offset in range(len(s) + 1 - search_len):
                                if s[offset:offset+search_len] == match:
                                    self.sequences[i].seq = s[0:offset] + (match_i,) + s[offset+search_len:]
                                    break
                            else:
                                break
                        else:
                            break
            else:
                search_len = search_len - 1

    def reduce_to_cons(self):
        """ break all sequences down into 2-tuples"""

        i = 0
        while i < len(self.sequences):
            s = self.sequences[i].seq
            if len(s) > 2:
                cdr = self.add_sequence(s[1:])
                self.sequences[i].seq = (s[0], cdr)
            i = i + 1

    def name_sequences(self):
        proposed = {i: self.sequences[i].name for i in range(len(self.sequences))
                    if self.sequences[i].name is not None}
        for _ in range(len(self.sequences)):
            for i in range(len(self.sequences)):
                try:
                    name = proposed[i]
                except KeyError:
                    continue
                car, cdr = self.sequences[i].seq
                car_name = name + ".0"
                if isinstance(car, int):
                    if car not in proposed or proposed[car] == car_name:
                        proposed[car] = car_name
                    elif self.sequences[car].name is None:
                        proposed[car] = "node_{}.0".format(car)

                if isinstance(cdr, int):
                    if "." in name and name.rsplit(".", maxsplit=1)[1].isnumeric():
                        cdr_name = name.rsplit(".", maxsplit=1)[0] + "." + \
                            str(int(name.rsplit(".", maxsplit=1)[1]) + 1)
                    else:
                        cdr_name = "node_{}.0".format(cdr)
                    if cdr not in proposed or proposed[cdr] == cdr_name:
                        proposed[cdr] = cdr_name
                    elif self.sequences[cdr].name is None:
                        proposed[cdr] = "node_{}.0".format(cdr)

        for i in proposed:
            self.sequences[i].name = proposed[i]

        #ensure all names are unique
        previous_names = set()
        dup_names = set()
        for i in self.reachable():
            if self.sequences[i].name in previous_names:
                dup_names.add(self.sequences[i].name)
            previous_names.add(self.sequences[i].name)

        for i in self.reachable():
            if self.sequences[i].name in dup_names:
                self.sequences[i].name += ".n{}".format(i)

    def generate(self):

        def max_zeros(v):
            if isinstance(v, int):
                s = self.sequences[v].seq
                return max(1 + max_zeros(s[0]), max_zeros(s[1]))
            else:
                return 0

        def generate_break(level):
            while level > 0:
                self.tm.states[(f"6.break.{level}", "0")] = \
                    tm.Transition("0", "L", f"6.break.{level - 1}")
                self.tm.states[(f"6.break.{level}", "1")] = \
                    tm.Transition("0", "L", f"6.break.{level}")
                level -= 1

        def generate_continue(level):
            while level > 0:
                self.tm.states[(f"6.continue.{level}", "0")] = \
                    tm.Transition("0", "L", f"6.continue.{level}")
                self.tm.states[(f"6.continue.{level}", "1")] = \
                    tm.Transition("0", "L", f"6.continue.{level - 1}")
                level -= 1

        max_zeros = max(1 + max_zeros(self.find_seq("main().0")), 2)

        for lineno, l in enumerate(framework.splitlines()):
            self.tm.loadline(l, "<framework>", lineno)

        for i in range(1, max_zeros + 1):
            self.tm.states[("4.dispatch.{}".format(i), "0")] = \
                tm.Transition("0", "L", f"4.dispatch.{i-1}")
            self.tm.states[("4.dispatch.{}".format(i), "1")] = \
                tm.Transition("1", "L", f"4.dispatch.{i}")

        self.tm.states[("6.continue.0", "1")] = \
            tm.Transition("1", "L", f"4.dispatch.{max_zeros}")

        for reg in self.registers.values():
            if self.tm.states[(reg.inc, "1")].nextstate == "2b.reg.0.inc":
                zero_reg = reg

        self.tm.states[("0a.boot1.C", "1")] = tm.Transition("1", "R", zero_reg.inc)
        self.tm.states[("0b.boot2.2", "0")] = tm.Transition("0", "R", zero_reg.inc)
        self.tm.states[("0b.boot2.2", "1")] = tm.Transition("1", "R", zero_reg.decnz)

        # the framework is now ready except for the break and continue states
        # Generate the decision tree states and the needed framework states.
        for seq_i in self.reachable():
            seq = self.sequences[seq_i]
            if isinstance(seq.seq[0], int):
                self.tm.states[(seq.name, "0")] = \
                    tm.Transition("0", "R", self.sequences[seq.seq[0]].name)
            elif seq.seq[0].startswith("_break."):
                if seq.seq[0] == "_break.0":
                    self.tm.states[(seq.name, "0")] = \
                        tm.Transition("1", "L", "6.continue.0")
                else:
                    break_i = int(seq.seq[0].split(".")[1]) - 1
                    self.tm.states[(seq.name, "0")] = \
                        tm.Transition("0", "L", f"6.break.{break_i}")
                    generate_break(break_i)
            elif seq.seq[0].startswith("_continue."):
                continue_i = int(seq.seq[0].split(".")[1])
                self.tm.states[(seq.name, "0")] = \
                    tm.Transition("0", "L", f"6.continue.{continue_i}")
                generate_continue(continue_i)
            else:
                self.tm.states[(seq.name, "0")] = \
                     tm.Transition("0", "R", seq.seq[0])

            if isinstance(seq.seq[1], int):
                self.tm.states[(seq.name, "1")] = \
                    tm.Transition("1", "R", self.sequences[seq.seq[1]].name)
            elif seq.seq[1].startswith("_break."):
                break_i = int(seq.seq[1].split(".")[1])
                self.tm.states[(seq.name, "1")] = \
                    tm.Transition("0", "L", f"6.break.{break_i}")
                generate_break(break_i)
            elif seq.seq[1].startswith("_continue."):
                continue_i = int(seq.seq[1].split(".")[1]) - 1
                assert continue_i >= 0 # otherwise we've somehow generated an infinite loop
                self.tm.states[(seq.name, "1")] = \
                    tm.Transition("0", "L", f"6.continue.{continue_i}")
                generate_continue(continue_i)
            else:
                self.tm.states[(seq.name, "1")] = \
                    tm.Transition("1", "R", seq.seq[1])

    def build_machine(self):
        self.main()
        self.breakout_common_subsequences()
        self.reduce_to_cons()
        self.name_sequences()
        self.generate()
        self.tm.gc()
        self.tm.statename = self.tm.start


    def process_cmdline(self):
        self.build_machine()
        debugger = tmdb.TMDB()
        debugger.tm = self.tm
        debugger.mainloop()

    @subroutine
    def while_decnz(self, var, body):
        if body == ():
            return [
                self.label(
                "loop",
                [
                    var.decnz,
                    "continue_loop"
                ])
                   ]
        else:
            return [
                self.label(
                "loop",
                [
                    var.decnz,
                    [
                        body,
                        "continue_loop"
                    ]
                ])
                    ]

    @subroutine
    def if_decnz(self, var, body):
        assert body != ()
        return [[
            var.decnz,
            body
            ]]

    @subroutine
    def if_not_decnz(self, var, body):
        assert body != ()
        return [
            self.label(
            "fn",
            [
                [
                    var.decnz,
                    "break_fn"
                ],
                body
            ])
                ]

    @subroutine
    # zeros in1, in2
    def pair(self, out, in1, in2):
        assert out not in (in1, in2)
        return [
            self.label(
            "loop",
            [
                self.while_decnz(in1, [in2.inc, out.inc]),
                [
                    in2.decnz,
                    [
                        [
                            out.inc,
                            self.while_decnz(in2, in1.inc),
                        ],
                        "continue_loop"
                    ]
                ]
            ])
                ]


    @subroutine
    # zeros in1
    def unpair(self, out1, out2, in1):
        assert in1 not in (out1, out2)

        return [
            self.label(
            "loop",
            [
                in1.decnz,
                [
                    out1.inc,
                    [
                        [
                            out2.decnz,
                            "continue_loop"
                        ],
                        [
                            self.while_decnz(out1, out2.inc),
                            "continue_loop"
                        ]
                    ]
                ]
            ])
               ]

    @subroutine
    # zeros in1, in2
    def if_eq(self, in1, in2, body):
        return [
            self.label(
            "fn",
            [
                [
                    self.label(
                    "loop",
                    [
                        #continue
                        in1.decnz,
                        [
                            [
                                in2.decnz,
                                "continue_loop"
                            ],
                            [
                                # in1 > in2
                                # zero in1 and return
                                self.while_decnz(in1, ()),
                                "break_fn"
                            ]
                        ]
                    ]),
                    # if in2 is 0 then the two match
                    [
                        in2.decnz,
                        [
                            # in2 > in1
                            # zero in2 and return
                            self.while_decnz(in2, ()),
                            "break_fn"
                        ]
                    ],
                ],
                body
            ])
                ]


