#!/usr/bin/python3

import tm

framework = """
#! start 0.boot1.A
# Based on the NQL register machine:
# <https://github.com/sorear/metamath-turing-machines>
#
# States that being with a digit are the states for the framework of the
# register machine implemented in a turing machine. States that don't begin
# with a digit are the decision tree states from the subroutines and main().
#
# 1. boot1 isn't quite BB(5) but leaves the tape in a good state for boot2.
#
0.boot1.A 0 1 R 0.boot1.B
0.boot1.A 1 1 L 0.boot1.C
0.boot1.B 0 0 L 0.boot1.A
0.boot1.B 1 0 L 0.boot1.D
0.boot1.C 0 1 L 0.boot1.A
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
0.boot1.C 1 1 R [4.register_0_inc]
0.boot1.D 0 1 L 0.boot1.B
0.boot1.D 1 1 R 0.boot1.E
0.boot1.E 0 0 R 0.boot1.D
0.boot1.E 1 0 R 0.boot1.B
#
# 1. In boot2 we are going through dispatch and can use much of the framework
# loop to help clean up the PC and initialize the registers.
# In particular, boot2 relies on a successful decnz adding one
# register to the register file as a side-effect.
#
# At the end of boot2 the PC contains "11", there are 3822 0s between the PC
# and the register file, and the register file contains 1909 registers plus
# the -1 marker register.
#
1.boot2.0 1 1 R 1.boot2.1
1.boot2.1 0 0 R 1.boot2.0
1.boot2.1 1 1 R 1.boot2.2
1.boot2.2 0 0 R [4.register_0.inc]
1.boot2.2 1 1 R [4.register_0.decnz]
#
# 2. The dispatch states handle finding the start of the PC. During the boot2
# phase the wrong cell is identified as the start of the PC until the last
# few iterations, but this does not cause any difficulties.
#
2.dispatch.0 0 0 L 2.dispatch.find.pc
2.dispatch.0 1 1 L 2.dispatch.0
2.dispatch.find.pc 0 0 R 2.dispatch.find.pc
2.dispatch.find.pc 1 1 R 2.root.1
#
# 2. The transition of the PC from "101" to "110" initiates the start
# of the main loop. The rest of the PC is then the decision tree for the main
# subroutine.
# Upon overflow to "111" the PC is set back to "110" to start the main loop over.
# The 2.root* states handle the transitions between these phases.
#
2.root.1 0 0 R 1.boot2.0
2.root.1 1 1 R 2.root.1.1
2.root.1.1 0 0 R main().0
2.root.1.1 1 0 R main().0
#
# 3. and 4. Register operations go through dispatch twice.
# In the first phase, the -1 marker register is extended to the left
# almost to the PC. In the second phase, the register operation is performed,
# the PC is adjusted, and the -1 marker register is collapsed back to one cell.
# (This allows the decision tree to take additional cells for the PC if it
#  wishes in the following dispatch.)
#
# The states beginning with 4. handle the transition between phase 1 and phase 2
# of the register operations. Unlike most dispatch states, these states
# manipulate the last bit of the PC directly.
#
3.reg.-1.dec 0 0 R 3.reg.-2.dec
3.reg.-1.dec 1 1 R 3.reg.-1.dec
3.reg.-1.inc 0 0 R 3.reg.-2.inc
3.reg.-1.inc 1 1 R 3.reg.-1.inc
3.reg.-2.dec 0 1 L 3.reg.return_2_1
3.reg.-2.dec 1 0 R 3.reg.dec.check
3.reg.-2.inc 0 1 R 3.reg.inc.shift_1
3.reg.-2.inc 1 1 R 3.reg.-2.inc
3.reg.cleanup_1 0 0 R 3.reg.cleanup_1
3.reg.cleanup_1 1 0 R 3.reg.cleanup_2
3.reg.cleanup_2 0 0 L 3.reg.cleanup_3
3.reg.cleanup_2 1 0 R 3.reg.cleanup_2
3.reg.cleanup_3 0 1 L 2.dispatch
3.reg.dec.check 0 0 L 3.reg.-2.dec
3.reg.dec.check 1 1 R 3.reg.dec.scan_1
3.reg.dec.scan_1 1 1 R 3.reg.dec.scan_1
3.reg.dec.scan_1 0 0 R 3.reg.dec.scan_2
3.reg.dec.scan_2 0 0 L 3.reg.dec.shift_1
3.reg.dec.scan_2 1 1 R 3.reg.dec.scan_1
3.reg.dec.shift_1 0 1 L 3.reg.dec.shift_2
3.reg.dec.shift_1 1 1 L 3.reg.dec.shift_1
3.reg.dec.shift_2 0 0 L 3.reg.return_1_1
3.reg.dec.shift_2 1 0 L 3.reg.dec.shift_1
3.reg.inc.shift_1 0 0 L 3.reg.return_1_1
3.reg.inc.shift_1 1 0 R 3.reg.inc.shift_2
3.reg.inc.shift_2 0 1 R 3.reg.inc.shift_1
3.reg.inc.shift_2 1 1 R 3.reg.inc.shift_2
3.reg.prep_1 0 0 R 3.reg.prep_2
3.reg.prep_2 0 1 R 3.reg.prep_2
# Phase 1 of the register operation is over. We've forgotten which register
# and operation we're performing so go through dispatch again:
3.reg.prep_2 1 1 L 5.continue.0
3.reg.return_1_1 0 0 L 3.reg.return_1_2
3.reg.return_1_1 1 1 L 3.reg.return_1_1
3.reg.return_1_2 0 0 L 5.break.0
3.reg.return_1_2 1 1 L 3.reg.return_1_1
3.reg.return_2_1 0 0 L 3.reg.return_2_2
3.reg.return_2_1 1 1 L 3.reg.return_2_1
3.reg.return_2_2 0 0 L 5.break.1
3.reg.return_2_2 1 1 L 3.reg.return_2_1
#
# 5. PC jump instructions.
#
# We don't know if we got to break.0 from phase two of a register instruction
# or not. Tranisition to the reg -1 cleanup state unconditionally. If we're
# not transitioning from a register operation this cleanup won't do anything
# and we'll end up back in dispatch regardless.
5.break.0 0 1 R 3.reg.cleanup_1
5.break.0 1 0 L 5.break.0
5.break.1 0 0 L break.0
5.break.1 1 0 L break.1
5.continue.0 0 0 L 5.continue.0
5.continue.0 1 1 L [largest_2.dispatch]
"""



class Register(str):
    @property
    def inc(self):
        return "4." + self + ".inc"

    @property
    def dec(self):
        return "4." + self + ".dec"

    @property
    def decnz(self):
        return "4." + self + ".decnz"

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
            self.tm.states[("3..reg.{}.inc".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "3.reg.{}.inc".format(self.nextreg - 1))
            self.tm.states[("reg.{}.inc".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "3.reg.{}.inc".format(self.nextreg))
            self.tm.states[("reg.{}.dec".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "3.reg.{}.dec".format(self.nextreg - 1))
            self.tm.states[("reg.{}.dec".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "3.reg.{}.dec".format(self.nextreg))
            self.tm.states[(reg.inc, "0")] = \
                tm.Transition("1", "R", "reg.prep_1")
            self.tm.states[(reg.inc, "1")] = \
                tm.Transition("0", "R", "reg.{}.inc".format(self.nextreg))
            self.tm.states[(reg.decnz, "0")] = \
                tm.Transition("1", "R", "reg.prep_1")
            self.tm.states[(reg.decnz, "1")] = \
                tm.Transition("0", "R", "reg.{}.dec".format(self.nextreg))
            self.tm.states[(reg.dec, "0")] = \
                tm.Transition("0", "R", reg.decnz)
            self.tm.states[(reg.dec, "1")] = \
                tm.Transition("0", "L", "5.break.0")
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

        def resolve_entry(zeros, ones, val):
            if val in control_flow:
                if val == "break_" + name:
                    return "5.break.{}".format(zeros)
                else:
                    return "5.continue.{}".format(ones)
            if isinstance(val, int) and name in self.sequences[val].unresolved_labels:
                return self.label(name, self.sequences[val].seq, zeros, ones)
            return val

        if len(seq) == 2:
            return self.add_sequence((resolve_entry(zeros + 1, ones, seq[0]),
                                      resolve_entry(zeros, ones + 1, seq[1])))

        assert False, "unimplemented"

    def find_seq(self, name):
        for i in range(len.self.sequences):
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

        max_zeros = 1 + maz_zeros(self.find_seq("main.0"))

        for lineno, l in enumerate(framework.splitlines()):
            self.tm.loadline(l, "<framework>", lineno)

        for i in range(1, max_zeros + 1):
            self.tm.states[("2.dispatch.{}".format(i), "0")] = \
                tm.Transition("0", "L", "2.dispatch.{}".format(i-1))
            self.tm.states[("2.dispatch.{}".format(i), "1")] = \
                tm.Transition("1", "L", "2.dispatch.{}".format(i))

        self.tm.states[("5.continue.0", "1")] = \
            tm.Transition("1", "L", "2.dispatch.{}".format(max_zeros))

        for reg in self.registers.values():
            if self.tm.states[(reg.inc, "1")].nextstate == "3.reg.0.inc":
                zero_reg = reg

        self.tm.states[("0.boot1.C", "1")] = tm.Transition("1", "R", reg.inc)
        self.tm.states[("1.boot2.2", "0")] = tm.Transition("0", "R", reg.inc)
        self.tm.states[("1.boot2.2", "1")] = tm.Transition("1", "R", reg.decnz)

        # the framework is now ready except for the break and continue states
        # Generate the decision tree states
        for seq_i in self.reachable():
            seq = self.sequences[seq_i]
            if isinstance(seq.seq[0], int):
                self.tm.states[(seq.name, "0")] = \
                    tm.Transition("0", "R", self.sequences[seq.seq[0]].name)
            elif seq.seq[0].startswith("break."):
                assert False, "TODO"

        assert False, "TODO"

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


