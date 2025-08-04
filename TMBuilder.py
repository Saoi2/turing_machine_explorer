#!/usr/bin/python3

import tm

framework = """
0.boot1.A 0 1 R 0.boot1.B
0.boot1.A 1 1 L 0.boot1.C
0.boot1.B 0 0 L 0.boot1.A
0.boot1.B 1 0 L 0.boot1.D
0.boot1.C 0 1 L 0.boot1.A
0.boot1.C 1 1 R [4.register_0_inc]
0.boot1.D 0 1 L 0.boot1.B
0.boot1.D 1 1 R 0.boot1.E
0.boot1.E 0 0 R 0.boot1.D
0.boot1.E 1 0 R 0.boot1.B
1.boot2.0 1 1 R 1.boot2.1
1.boot2.1 0 0 R 1.boot2.0
1.boot2.1 1 1 R 1.boot2.2
1.boot2.2 0 0 R [4.register_0_inc]
1.boot2.2 1 1 R [4.register_0_dec
2.dispatch.0 0 0 L 2.root.find_2.pc
2.dispatch.0 1 1 L 2.dispatch.0
2.root.find_2.pc 0 0 R 2.root.find_2.pc
2.root.find_2.pc 1 1 R 2.root.1
2.root.1 0 0 R 1.boot2.0
2.root.1 1 1 R 2.root.1.1
2.root.1.1 0 0 R main().0
2.root.1.1 1 0 R main().0
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
3.reg.prep_2 1 1 L 5.continue.0
3.reg.return_1_1 0 0 L 3.reg.return_1_2
3.reg.return_1_1 1 1 L 3.reg.return_1_1
3.reg.return_1_2 0 0 L 5.break.0
3.reg.return_1_2 1 1 L 3.reg.return_1_1
3.reg.return_2_1 0 0 L 3.reg.return_2_2
3.reg.return_2_1 1 1 L 3.reg.return_2_1
3.reg.return_2_2 0 0 L 5.break.1
3.reg.return_2_2 1 1 L 3.reg.return_2_1
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


    def jump_dispatch(self, pc, old_pc, bits):
        state_name = "jump_dispatch({},{},{})".format(pc, old_pc, bits)
        next_state = self.jump(pc, old_pc, bits)
        self.tm.states[(state_name, "0")] = tm.Transition("0", "L", next_state)
        self.tm.states[(state_name, "1")] = tm.Transition("1", "L", next_state)
        return state_name

    def jump(self, pc, old_pc, bits):
        if bits == 0:
            return "dispatch"

        state_name = "jump({},{},{})".format(pc, old_pc & ~1, bits)
        next_state = self.jump(pc >> 1, old_pc >> 1, bits - 1)
        self.tm.states[(state_name, "01"[old_pc & 1])] = tm.Transition("01"[pc & 1], "L", next_state)

        return state_name

    def next_dispatch(self, old_pc, bits):
        state_name = "next_dispatch({},{})".format(old_pc, bits)
        next_state = self.next_pc(old_pc, bits)
        self.tm.states[(state_name, "0")] = tm.Transition("0", "L", next_state)
        self.tm.states[(state_name, "1")] = tm.Transition("1", "L", next_state)
        return state_name

    def next_pc(self, old_pc, bits):
        if bits == 0:
            return "pc.next"

        state_name = "next({},{})".format(old_pc & ~1, bits)
        next_state = self.next_pc(old_pc >> 1, bits - 1)
        self.tm.states[(state_name, "01"[old_pc & 1])] = tm.Transition("0", "L", next_state)

        return state_name

    def load_framework(self):
        for lineno, l in enumerate(framework.splitlines()):
            self.tm.loadline(l, "<framework>", lineno)

    def breakout_common_subsequences(self):

        search_len = max(len(s.seq) for s in self.sequences)

        while search_len > 1:
            subsequences = set()
            match = None
            for s in self.sequences:
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
                i = 0
                while i < len(self.sequences):
                    s = self.sequences[i].seq
                    if len(s) > search_len:
                        for offset in range(len(s) + 1 - search_len):
                            if s[offset:offset+search_len] == match:
                                self.sequences[i].seq = s[0:offset] + (match_i,) + s[offset+search_len:]
                                break
                        else:
                            i = i + 1
                    else:
                        i = i + 1
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



    @subroutine
    def while_decnz(self, var, body):
        if body == ():
            return [[
                var.decnz,
                self.jump_dispatch(0, 1, 1)
                ]]
        else:
            return [[
                var.decnz,
                [
                    body,
                    self.jump_dispatch(0, 3, 2)
                ]
                ]]

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
        return [[
            [
                var.decnz,
                self.next_dispatch(1, 2)
            ],
            body
            ]]

    @subroutine
    # zeros in1, in2
    def pair(self, out, in1, in2):
        assert out not in (in1, in2)
        return [
            [
                self.while_decnz(in1, [in2.inc, out.inc]),
                [
                    in2.decnz,
                    [
                        [
                            out.inc,
                            self.while_decnz(in2, in1.inc),
                        ],
                        self.jump_dispatch(0,0b111, 3)
                    ]
                ]
            ]
                ]


    @subroutine
    # zeros in1
    def unpair(self, out1, out2, in1):
        assert in1 not in (out1, out2)

        return [
            [
                in1.decnz,
                [
                    out1.inc,
                    [
                        [
                            out2.decnz,
                            self.jump_dispatch(0, 0b1101, 4)
                        ],
                        [
                            self.while_decnz(out1, out2.inc),
                            self.jump_dispatch(0, 0b1111, 4)
                        ]
                    ]
                ]
            ]
               ]

    @subroutine
    # zeros in1, in2
    def if_eq(self, in1, in2, body):
        return [
            [
                [
                    [
                        #continue
                        in1.decnz,
                        [
                            [
                                in2.decnz,
                                self.jump_dispatch(0,0b101, 3) #goto continue
                            ],
                            [
                                # in1 > in2
                                # zero in1 and return
                                self.while_decnz(in1, ()),
                                self.next_dispatch(0b00111, 5) # skip_inc
                            ]
                        ]
                    ],
                    # if in2 is 0 then the two match
                    [
                        in2.decnz,
                        [
                            # in2 > in1
                            # zero in2 and return
                            self.while_decnz(in2, ()),
                            self.next_dispatch(0b0111, 4) # skip_inc
                        ]
                    ],
                ],
                body
            ]
                #skip_inc
                ]


