#!/usr/bin/python3

import TMBuilder
from TMBuilder import subroutine

class ZF2(TMBuilder.TMBuilder):
    """
This program halts if it finds an inconsistency in ZF.
It is a port of <https://github.com/sorear/metamath-turing-machines/blob/master/zf2.nql> with
some ideas from <https://github.com/CatsAreFluffy/metamath-turing-machines/blob/master/zf2.nql>
    """

    def __init__(self):
        super().__init__()
        self.prooflist = self.reg("prooflist")
        self.nextproof = self.reg("nextproof")
        self.topwff = self.reg("topwff")
        self.wffstack = self.reg("wffstack")
        self.axiomcode = self.reg("axiomcode")
        self.param1 = self.reg("param1")
        self.param2 = self.reg("param2")
        self.param3 = self.reg("param3")
        self.scratch1 = self.reg("scratch1")
        self.scratch2 = self.reg("scratch2")
        self.scratch3 = self.reg("scratch3")


    @subroutine
    def pushwff(self):
        return [
            self.pair(self.scratch1, self.topwff, self.wffstack),
            self.while_decnz(self.scratch1, self.wffstack.inc)
               ]

    # v_0 is just pushwff
    def v_0(self):
        return self.pushwff()

    @subroutine
    def v_1(self):
        return [
            *self.v_0(),
            self.topwff.inc
               ]

    @subroutine
    def v_2(self):
        return [
            *self.v_1(),
            self.topwff.inc
               ]

    @subroutine
    def v_3(self):
        return [
            *self.v_2(),
            self.topwff.inc
               ]

    @subroutine
    def v_4(self):
        return [
            *self.v_3(),
            self.topwff.inc
               ]

    @subroutine
    def cons(self):
        return [
            self.unpair(self.scratch1, self.scratch2, self.wffstack),
            self.while_decnz(self.scratch2, self.wffstack.inc),
            self.pair(self.scratch2, self.scratch1, self.topwff),
            self.while_decnz(self.scratch2, self.topwff.inc)
               ]

    @subroutine
    def weq(self):
        return [self.cons(), self.v_0(), self.cons()]

    @subroutine
    def wel(self):
        return [self.cons(), self.v_1(), self.cons()]

    @subroutine
    def wim(self):
        return [self.cons(), self.v_2(), self.cons()]

    @subroutine
    def wn(self):
        return [self.v_3(), self.cons() ]

    @subroutine
    def wal(self):
        return [self.cons(), self.v_4(), self.cons()]

    @subroutine
    def wex(self):
        return [self.wn(), *self.wal(), self.wn()]

    @subroutine
    def wa(self):
        return [self.wn(), *self.wim(), self.wn()]

    @subroutine
    def par1(self):
        return [
            self.pushwff(),
            self.while_decnz(self.param1, [self.topwff.inc, self.scratch1.inc]),
            self.while_decnz(self.scratch1, self.param1.inc)
               ]

    @subroutine
    def par2(self):
        return [
            self.pushwff(),
            self.while_decnz(self.param2, [self.topwff.inc, self.scratch1.inc]),
            self.while_decnz(self.scratch1, self.param2.inc)
               ]

    @subroutine
    def par3(self):
        return [
            self.pushwff(),
            self.while_decnz(self.param3, [self.topwff.inc, self.scratch1.inc]),
            self.while_decnz(self.scratch1, self.param3.inc)
               ]

    # This select function is a little different than in zf2.nql
    # The difference is that the unpair function here doesn't zero out1, out2
    # first. So we use scratch variables that are always kept zero.
    # But this means we need to make sure the scratch variables are reset
    # to zero at the end.
    @subroutine
    def select(self):
        return [
            self.while_decnz(self.topwff, self.scratch1.inc),
            self.unpair(self.topwff, self.scratch2, self.wffstack),
            self.while_decnz(self.scratch2, self.wffstack.inc),
            self.if_decnz(
                self.axiomcode,
                [
                    self.while_decnz(self.topwff, ()),
                    self.while_decnz(self.scratch1,self.topwff.inc),
                ]
            ),
            self.while_decnz(self.scratch1, ())
                ]

    @subroutine
    def cparam(self, p):
        return [
            self.label(
            "fn",
            [
                self.label(
                "test",
                [
                    self.label(
                    "innertest",
                    [
                        self.axiomcode.decnz,
                        [
                            [
                                self.axiomcode.decnz,
                                [
                                    # restore axiomcode
                                    [self.axiomcode.inc, self.axiomcode.inc],
                                    "break_innertest" # chained return
                                ]
                            ],
                            #axiomcode was 1
                            [
                                [
                                    self.axiomcode.inc, # restore axiomcode
                                    self.unpair(self.scratch1, self.scratch2, self.wffstack),
                                    self.while_decnz(self.scratch2, self.wffstack.inc),
                                ],
                                # by putting in a jump here, we can move the
                                # parameter-dependent part of this subroutine closer to the
                                # root.
                                "break_test" # jump to p = scratch1
                            ]
                        ]
                    ]),
                    "break_fn" #return
                ]),
                # p = scratch1
                [
                    self.while_decnz(p, ()),
                    self.while_decnz(self.scratch1, p.inc)
                ]
            ])
               ]


    @subroutine
    def main(self):
        weq = self.weq()
        wel = self.wel()
        wim = self.wim()
        wn = self.wn()
        wal = self.wal()
        wex = self.wex()
        wa = self.wa()
        v_0 = self.v_0()
        v_1 = self.v_1()
        v_2 = self.v_2()
        v_3 = self.v_3()
        par1 = self.par1()
        par2 = self.par2()
        par3 = self.par3()
        select = self.select()

        return [
            self.if_not_decnz(self.prooflist, [
                self.while_decnz(self.nextproof, [self.scratch1.inc, self.prooflist.inc]),
                self.while_decnz(self.scratch1, self.nextproof.inc),
                self.nextproof.inc,
                ]),

            self.debug_assert_eq_val(self.scratch1, 0),
            self.debug_assert_eq_val(self.scratch2, 0),
            self.while_decnz(self.axiomcode, ()),
            self.while_decnz(self.param1, ()),
            self.while_decnz(self.param2, ()),
            self.while_decnz(self.param3, ()),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.axiomcode.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param3.inc),

            v_0, # default theorem if nothing is selected.

            # DET
            self.cparam(self.param3), # minor premise ph
            self.cparam(self.param2), # major premise ( ph -> ps), par1 = ps
            par3, par1, wim,
            # we've build ph->ps in topwff, move it to scratch2,
            # leaving topwff as the |v_0 = v_0| wff.
            self.while_decnz(self.topwff, self.scratch2.inc),
            # copy param2 in scratch3
            self.while_decnz(self.param2, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.if_eq(self.scratch2, self.scratch3, [
                # if the wff popped into param2 is ph->ps, copy param1 (ps) to topwff.
                self.while_decnz(self.param1, [self.scratch1.inc, self.topwff.inc]),
                self.while_decnz(self.scratch1, self.param1.inc)
                ]),
            select,

            # GEN
            self.cparam(self.param3), # ph
            par1, par3, wal, select,

            # B1
            par1, par2, wim, par2, par3, wim, par1, par3, wim, wim, wim, select,

            # B2
            par1, wn, par1, wim, par1, wim, select,

            # B3
            par1, par1, wn, par2, wim, wim, select,

            # B4
            par1, par2, par3, wim, wal, par1, par2, wal, par1, par3, wal, wim, wim, select,

            # B6b
            par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select,

            # B8b
            par1, par2, weq, par1, par3, wel, par2, par3, wel, wim, wim, select,

            # B6a
            par1, par2, weq, par3, par1, par2, weq, wal, wim,
            par1, par2, wel, par3, par1, par2, wel, wal, wim, wa,
            # copy param1 into scratch2 and param3 into scratch3
            self.while_decnz(self.param1, [self.scratch1.inc, self.scratch2.inc]),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.while_decnz(self.param3, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.if_eq(self.scratch2, self.scratch3, [
                self.while_decnz(self.topwff, ())
                ]),
            # copy param2 into scratch2 and param3 into scratch3
            self.while_decnz(self.param2, [self.scratch1.inc, self.scratch2.inc]),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.while_decnz(self.param3, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.if_eq(self.scratch2, self.scratch3, [
                self.while_decnz(self.topwff, ())
                ]),
            select,

            # B6b
            par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select,

            # B6c
            par1, par1, par2, wal, wex, par2, wim, select,

            # B7
            par1, par1, par2, weq, wex, select,

            # B8a
            par1, par2, weq, par1, par3, weq, par2, par3, weq, wim, wim, select,

            # B8b
            par1, par2, weq, par1, par3, wel, par2, par3, wel, wim, wim, select,

            # B8c
            par1, par2, weq, par3, par1, wel, par3, par2, wel, wim, wim, select,

            # EXT
            v_2,
            v_2, v_0, wel, v_2, v_1, wel, wim,
            v_2, v_1, wel, v_2, v_0, wel, wim, wa,
            wal, v_0, v_1, weq, wim, select,

            # REP
            v_3, v_1, v_2, v_1, par1, wal, v_2, v_1, weq, wim, wal, wex, wal,
            v_1, v_2,
            v_2, v_1, wel, v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, wim,
            v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, v_2, v_1, wel, wim, wa,
            wal, wex,
            wim, select,

            # POW
            v_1, v_2, v_3, v_3, v_2, wel, v_3, v_0, wel, wim, wal, v_2, v_1, wel, wim, wal, wex, select,

            # UNI
            v_1, v_2, v_3, v_2, v_3, wel, v_3, v_0, wel, wa, wex, v_2, v_1, wel, wim, wal, wex, select,

            # INF
            v_1, v_0, v_1, wel, v_0, v_0, v_1, wel, v_2, v_2, v_1, wel,
            v_1, v_1, v_2, wel, v_1, v_0, weq, wim,
            v_1, v_0, weq, v_1, v_2, wel, wim, wa, wal,
            wa, wex, wim, wal, wa, wex, select,

            # check if we've proved the false v_0 e. v_0 wff.
            [
                self.topwff.decnz,
                self.label(
                "if",
                [
                    [
                        self.topwff.decnz,
                        [
                            # restore topwff
                            [self.topwff.inc, self.topwff.inc],
                            "break_if"
                        ]
                    ],
                    # topwff was 1
                    # this corresponds to the false wff (v_0 e. v_0) being proved.
                    "halt"
                ])
            ]
               ]

if __name__ == "__main__":
    ZF2().process_cmdline()
