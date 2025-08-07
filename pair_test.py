#!/usr/bin/python3

import TMBuilder
from TMBuilder import subroutine

class Test(TMBuilder.TMBuilder):

    @subroutine
    def main(self):
        v_1 = self.reg("v_1")
        v_2 = self.reg("v_2")
        v_3 = self.reg("v_3")
        car = self.reg("car")
        cdr = self.reg("cdr")
        cons = self.reg("cons")
        cons_copy = self.reg("cons_copy")
        scratch = self.reg("scratch")
        return [
            car.inc, car.inc, car.inc, car.inc,
            self.pair(cons, car, cdr),
            self.while_decnz(cons, cdr.inc),
            car.inc,
            self.pair(cons, car, cdr),
            self.while_decnz(cons, cdr.inc),
            car.inc, car.inc, car.inc,
            self.pair(cons, car, cdr),
            self.while_decnz(cons, scratch.inc),
            self.while_decnz(scratch, [cons.inc, cons_copy.inc]),

            # now unpair
            self.unpair(v_1, cdr, cons),
            self.while_decnz(cdr, cons.inc),
            self.unpair(v_2, cdr, cons),
            self.while_decnz(cdr, cons.inc),
            self.unpair(v_3, cdr, cons),

            "halt" # first 3 variables should have 3, 1, 4
                ]

if __name__ == "__main__":
    Test().process_cmdline()
