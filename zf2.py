#!/usr/bin/python

import TMBuilder
from TMBuilder import subroutine

class Main(TMBuilder.TMBuilder):

    def __init__(self):
        super.__init__(*argc, *argv)
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
            self.while_dec(self.scratch1, self.wffstack)
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
            *self.v3(),
            self.topwff.inc
               ]

    @subroutine
    def cons(self):
        return [
            self.unpair(self.scratch1, self.scratch2, self.wffstack),
            self.while_dec(self.scratch2, self.wffstack.inc),
            self.pair(self.scratch2, self.topwff, self.scratch1),
            self.while_dec(self.scratch2, self.topwff.inc)
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
        return [self.wn(), self.cons(), self.v_4(), self.cons(), self.wn()]

    @subroutine
    def wa(self):
        return [self.wn(), self.cons(), self.v_2(),  self.cons(), self.wn()]

    @subroutine
    def par1(self):
        return [
            self.pushwff(),
            self.while_dec(self.param1, [self.topwff.inc, self.scratch1.inc]),
            self.while_dec(self.scratch1, self.param1.inc)
               ]

    @subroutine
    def par2(self):
        return [
            self.pushwff(),
            self.while_dec(self.param2, [self.topwff.inc, self.scratch1.inc]),
            self.while_dec(self.scratch1, self.param2.inc)
               ]

    @subroutine
    def par3(self):
        return [
            self.pushwff(),
            self.while_dec(self.param3, [self.topwff.inc, self.scratch1.inc]),
            self.while_dec(self.scratch1, self.param3.inc)
               ]

    # This select function is a little different than in zf2.sql
    # The difference is that the unpair function here doesn't zero out1, out2
    # first. So we use a scratch variable that is always kept zero.
    # But this means we need to make sure the scratch variables are reset
    # to zero at the end.
    @subroutine
    def select(self):
        return [
            self.unpair(self.scratch1, self.scratch2, self.wffstack),
            self.while_dec(self.scratch2, self.wffstack.inc),
            self.if_not_dec(
                self.axiomcode,
                [
                    self.while_dec(self.wfftop, ()),
                    self.while_dec(self.scratch1,self.wfftop.inc),
                ]
            ),
            self.while_dec(self.scratch1, ())
                ]

    @subroutine
    def cparam(self, p):
        return [
            [
                [
                    [
                        self.axiomcode.dec,
                        [
                            [
                                self.axiomcode.dec,
                                [
                                    # restore axiomcode
                                    [self.axiomcode.inc, self.axiomcode.inc],
                                    self.next_dispatch(0b1011, 4) # chained return
                                ]
                            ],
                            #axiomcode was 1
                            [
                                [
                                    self.axiomcode.inc, # restore axiomcode
                                    self.unpair(self.scratch1, self.scratch2, self.wffstack),
                                    self.while_dec(self.scratch2, self.wffstack.inc),
                                ],
                                # by putting in a jump here, we can move the
                                # parameter-dependent part of this subroutine closer to the
                                # root.
                                self.next_dispatch(0b0111, 4) # jump to p = scratch1
                            ]
                        ]
                    ],
                    self.next_dispatch(0b01,2) #return
                ],
                # p = scratch1
                [
                    self.while_dec(p, ()),
                    self.while_dec(self.scratch1, p.inc)
                ]
            ]
               ]

    @subroutine
    def safety(self, p1, p2):
        return [
            # make copies of the parameters
            self.while_dec(p1, [self.scratch1.inc, self.scratch2.inc]),
            self.while_dec(self.scratch1, p1.inc),
            self.while_dec(p2, [self.scratch1.inc, self.scratch3.inc]),
            self.while_dec(self.scratch1, p2.inc),
            self.if_eq(scratch2, scratch3, self.p1.inc)
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
            self.if_not_dec(self.prooflist, [
                self.while_dec(self.nextproof, [self.scratch1.inc, self.prooflist.inc]),
                self.while_dec(self.scratch1, self.nextproof.inc),
                self.nextproof.inc,
                ]),

            self.while_dec(self.axiomcode, ()),
            self.while_dec(self.param1, ()),
            self.while_dec(self.param2, ()),
            self.while_dec(self.param3, ()),
            self.unpair(scratch1, scratch2, prooflist),
            self.while_dec(scratch2, prooflist.inc),
            self.while_dec(scratch1, axiomcode.inc),
            self.unpair(scratch1, scratch2, prooflist),
            self.while_dec(scratch2, prooflist.inc),
            self.while_dec(scratch1, param1.inc),
            self.unpair(scratch1, scratch2, prooflist),
            self.while_dec(scratch2, prooflist.inc),
            self.while_dec(scratch1, param2.inc),
            self.unpair(scratch1, scratch2, prooflist),
            self.while_dec(scratch2, prooflist.inc),
            self.while_dec(scratch1, param3.inc),

            # B1
            # no select since if axiomcode = 0 all selects reject the new entry
            par1, par2, wim, par2, par3, wim, par1, par3, wim, wim, wim,

            # B3
            par1, par1, wn, par2, wim, wim, select,

            # B2
            par1, wn, par1, wim, par1, wim, select,

            # B4
            par1, par2, par3, wim, wal, par1, par2, wal, par1, par3, wal, wim, wim, select,

            # B6b
            par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select,

            # B6c
            par1, par1, par2, wal, wex, par1, par2, wal, wim, select,

            # B8a
            # ( P = Q -> ( P = R -> Q = R) )
            # derivable using EXT
            par1, par2, weq, par1, par3, weq, par2, par3, weq, wim, wim, select,

            # B8c
            par1, par2, weq, par3, par1, wel, par3, par2, wel, wim, wim, select,

            # B7
            par1, par1, par2, weq, wex, select,

            # POW
            # E. y A. z ( A. y ( y e. z -> y e. x ) -> z e. y )
            v_1, v_2, v_1, v_1, v_2, wel, v_1, v_0, wel, wim, wal, v_2, v_1, wel, wim, wal, wex, select,

            # UNI
            # E. y A. z ( E. y ( z e. y /\ y e. x ) -> z e. y )
            v_1, v_2, v_1, v_2, v_1, wel, v_1, v_0, wel, wa, wex, v_2, v_1, wel, wim, wal, wex, select,

            # INF+COl+SEP
            # E. y ( A. z (( z e. x -> ( E. x A. y P -> z e. y ) ) /\ ( z e. y -> E. x P ) ) /\ A. x ( x e. y -> A. z  ( A. y P -> E. z ( z e. y /\ P ) ) ) )
            v_1, v_2, v_2, v_0, wel, v_0, v_1, par1, wal, wex, v_2, v_1, wel, wim, wim,
            v_2, v_1, wel, v_0, align_8, par1, wex, wim, wa,
            wal, v_0, v_0, v_1, wel, v_2, v_1, par1, wal,
            v_2, v_2, v_1, wel, par1, wa, wex, wim, wal, wim, wal, wa, wex,
            select,

            # BG6a
            self.safety(self.param1, self.param3),
            self.safety(self.param2, self.param3),
            par1, par2, weq, par3, par1, par2, weq, wal, wim,
            select,
            par1, par2, wel, par3, par1, par2, wel, wal, wim,
            select,

            # GEN
            # ph
            self.cparam(self.param2),
            par1, par2, wal, select,

            # ...

            # DET
            # ph
            self.cparam(self.param2),
            # ph -> ps
            self.cparam(self.param3),
            # param1 = ps
            par2, par1, wim,
            self.while_dec(self.topwff, self.scratch2.inc),
            self.while_dec(self.param3, [self.scratch1.inc, self.scratch3.inc]),
            self.while_dec(self.scratch1, self.param3.inc),
            self.if_eq(self.scratch2, self.scratch3, [
                self.while_dec(self.param1, [self.scratch1.inc, self.topwff.inc]),
                self.while_dec(self.scratch1, self.param1.inc)
                ]),
            select,

            # check if we've proved the false v_0 e. v_0 wff.
            [
                self.topwff.dec,
                [
                    [
                        self.topwff.dec,
                        [
                            # restore topwff
                            [self.topwff.inc, self.topwff.inc],
                            self.next_dispatch(0b011, 3)
                        ]
                    ],
                    # topwff was 1
                    # this corresponds to the false wff (v_0 e. v_0) being proved.
                    "halt"
                ]
            ]
               ]
