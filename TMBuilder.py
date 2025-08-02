#!/usr/bin/python3

import tm

framework = """
boot1.A 0 1 R boot1.B
boot1.A 1 1 L boot1.C
boot1.B 0 0 L boot1.A
boot1.B 1 0 L boot1.D
boot1.C 0 1 L boot1.A
boot1.C 1 1 R [register_0_inc]
boot1.D 0 1 L boot1.B
boot1.D 1 1 R boot1.E
boot1.E 0 0 R boot1.D
boot1.E 1 0 R boot1.B
boot2.0 1 1 R boot2.1
boot2.1 0 0 R boot2.0
boot2.1 1 1 R boot2.2
boot2.2 0 0 R [register_0_inc]
boot2.2 1 1 R [register_0_dec
dispatch 0 0 L dispatch
dispatch 1 1 L [largest_dispatch]
dispatch.0 0 0 L root.find_pc
dispatch.0 1 1 L dispatch.0
pc.inc 0 1 R reg.cleanup_1
pc.inc 1 0 L pc.inc
reg.-1.dec 0 0 R reg.-2.dec
reg.-1.dec 1 1 R reg.-1.dec
reg.-1.inc 0 0 R reg.-2.inc
reg.-1.inc 1 1 R reg.-1.inc
reg.-2.dec 0 1 L reg.return_2_1
reg.-2.dec 1 0 R reg.dec.check
reg.-2.inc 0 1 R reg.inc.shift_1
reg.-2.inc 1 1 R reg.-2.inc
reg.cleanup_1 0 0 R reg.cleanup_1
reg.cleanup_1 1 0 R reg.cleanup_2
reg.cleanup_2 0 0 L reg.cleanup_3
reg.cleanup_2 1 0 R reg.cleanup_2
reg.cleanup_3 0 1 L dispatch
reg.dec.check 0 0 L reg.-2.dec
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
root[] 1 1 R root[1]
root[1] 0 0 R main
root[1] 1 0 L dispatch
"""



class Register(str):
    def __getattribute__(self, name):
        if name == "inc":
            return self + ".inc"
        elif name == "dec":
            return self + ".dec"
        else:
            return super().__getattribute__(name)

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
        if subroutine_seq not in self.sequence_names:
            self.sequence_names[subroutine_seq] = "{}({})".format(func.__name__, ",".join(str(v) for v in new_args))
        else:
            self.sequence_names[subroutine_seq] = "node.{}".format(subroutine_seq)
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
        self.sequence_names = {}
        self.memo = {}

    def reg(self, name):
        if name not in self.registers:
            reg = Register(name)
            self.tm.states[("reg.{}.inc".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "reg.{}.inc".format(self.nextreg - 1))
            self.tm.states[("reg.{}.inc".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "reg.{}.inc".format(self.nextreg))
            self.tm.states[("reg.{}.dec".format(self.nextreg), "0")] = \
                tm.Transition("0", "R", "reg.{}.dec".format(self.nextreg - 1))
            self.tm.states[("reg.{}.dec".format(self.nextreg), "1")] = \
                tm.Transition("1", "R", "reg.{}.dec".format(self.nextreg))
            self.tm.states[(reg.inc, "0")] = \
                tm.Transition("1", "R", "reg.prep_1")
            self.tm.states[(reg.inc, "1")] = \
                tm.Transition("0", "R", "reg.{}.inc".format(self.nextreg))
            self.tm.states[(reg.dec, "0")] = \
                tm.Transition("1", "R", "reg.prep_1")
            self.tm.states[(reg.dec, "1")] = \
                tm.Transition("0", "R", "reg.{}.dec".format(self.nextreg))
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
            self.sequence_lookup[key] = len(self.sequences)
            self.sequences.append(key)
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

    @subroutine
    def while_dec(self, var, body):
        if body == ():
            return [[
                var.dec,
                self.jump_dispatch(0, 1, 1)
                ]]
        else:
            return [[
                var.dec,
                [
                    body,
                    self.jump_dispatch(0, 3, 2)
                ]
                ]]

    @subroutine
    def if_dec(self, var, body):
        assert body != ()
        return [[
            var.dec,
            body
            ]]

    @subroutine
    def if_not_dec(self, var, body):
        assert body != ()
        return [[
            [
                var.dec,
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
                self.while_dec(in1, [in2.inc, out.inc]),
                [
                    in2.dec,
                    [
                        [
                            out.inc,
                            self.while_dec(in2, in1.inc),
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
                in1.dec,
                [
                    out1.inc,
                    [
                        [
                            out2.dec,
                            self.jump_dispatch(0, 0b1101, 4)
                        ],
                        [
                            self.while_dec(out1, out2.inc),
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
                        in1.dec,
                        [
                            [
                                in2.dec,
                                self.jump_dispatch(0,0b101, 3) #goto continue
                            ],
                            [
                                # in1 > in2
                                # zero in1 and return
                                self.while_dec(in1, ()),
                                self.next_dispatch(0b00111, 5) # skip_inc
                            ]
                        ]
                    ],
                    # if in2 is 0 then the two match
                    [
                        in2.dec,
                        [
                            # in2 > in1
                            # zero in2 and return
                            self.while_dec(in2, ()),
                            self.next_dispatch(0b0111, 4) # skip_inc
                        ]
                    ],
                ],
                body
            ]
                #skip_inc
                ]

    def load_framework(self):
        for lineno, l in enumerate(framework.splitlines()):
            self.tm.loadline(l, "<framework>", lineno)

