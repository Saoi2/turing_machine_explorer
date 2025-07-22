#!/usr/bin/python3

import sys
import argparse
import traceback
from tm import TuringMachine

class TMDB:

    def __init__(self):
        self.tm = TuringMachine()
        self.breakpoints = set()
        self.quit = False
        self.repeatcommand = False
        self.listsize = 10
        self.stdin_lineno = 1

    def repeatcount(self, cmd):
        if len(cmd) == 2 and isnumeric(cmd[1]):
            return int(cmd[1])
        else:
            return 1

    def processcommand(self, cmd):

        self.repeatcommand = False

        if cmd.startswith("tm") and len(cmd.split()) > 1:
            if not self.tm.loadline(cmd.split(maxsplit=1)[1], "<STDIN>", self.stdin_lineno):
                print("Could not parse state")
            self.stdin_lineno = self.stdin_lineno + 1
            return False
        cmd = cmd.split()

        if cmd[0] in ("s", "step", "si"):
            for _ in range(self.repeatcount(cmd)):
                if not self.tm.step():
                    break
                if self.tm.statename in self.breakpoints or self.tm.looping:
                    break
            self.repeatcommand = True
            return True

        if cmd[0] in ("n", "next", "ni"):
            for _ in range(self.repeatcount(cmd)):
                currentname = self.tm.statename
                while self.tm.statename == currentname:
                    if not self.tm.step():
                        break
                    if self.tm.looping:
                        break
                if self.tm.statename in self.breakpoints:
                    break
            self.repeatcommand = True
            return True

        if cmd[0] in ("c", "continue"):
            for _ in range(self.repeatcount(cmd)):
                while True:
                    currentname = self.tm.statename
                    while self.tm.statename == currentname:
                        if not self.tm.step():
                            return True
                        if self.tm.looping:
                            return True
                    if self.tm.statename in self.breakpoints:
                        break
            self.repeatcommand = True
            return True

        if cmd[0] in ("start"):
            self.tm.left = []
            self.tm.right = []
            self.tm.symbol = self.tm.fill
            self.tm.statename = self.tm.start
            return True

        if cmd[0] in ("run"):
            self.processcommand("start")
            return self.processcommand("continue")

        if cmd[0] in ("jump"):
            if len(cmd) != 2:
                print("jump [state]")
                return False
            self.tm.statename = cmd[1]
            return True

        if cmd[0] in ("q", "quit"):
            self.quit = True
            return False

        if cmd[0] in ("load"):
            if len(cmd) != 2:
                print("load [filename]")
                return False
            self.tm.load(cmd[1])

        if cmd[0] in ("save"):
            if len(cmd) != 2:
                print("save [filename]")
                return False
            self.tm.save(cmd[1])
            return False

        if cmd[0] in ("bt", "backtrace"):
            for trace in reversed(self.tm.statetrace):
                if (trace[0], trace[1]) in self.tm.states:
                    state = self.tm.states[(trace[0], trace[1])]
                    print("{} {} x {}: {}".format(state.filename, state.lineno, trace[2],
                        self.tm.source[(state.filename, state.lineno)]))
                else:
                    print("{} {} x {}".format(trace[0], trace[1], trace[2]))
            return False

        if cmd[0] in ("set"):
            if len(cmd) > 2 and cmd[1] in ("listsize") and cmd[2].isnumeric():
                self.listsize = int(cmd[2])
                return False

        if cmd[0] in ("l", "list"):
            listing = []
            filename = None
            lineno = 1
            if (self.tm.statename, self.tm.symbol) in self.tm.states:
                filename = self.tm.states[(self.tm.statename, self.tm.symbol)].filename
                lineno = self.tm.states[(self.tm.statename, self.tm.symbol)].lineno
            if len(cmd) > 1:
                if ":" not in cmd[1]:
                    statename = cmd[1].split(",")[0] # range is unsupported we just use the start
                    for symbol in reversed(sorted(self.tm.symbols)):
                        if (statename, symbol) in self.tm.states:
                            filename = self.tm.states[(statename, symbol)].filename
                            lineno = self.tm.states[(statename, symbol)].lineno
                elif cmd[1].split(":")[1].isnumeric():
                    filename = cmd[1].split(":")[0]
                    lineno = cmd[1].split(":")[1]

            lines_displayed = 0
            lines = []
            for offset in range(self.listsize):
                if (filename, lineno + offset) in self.tm.source:
                    if lines_displayed == 0:
                        lines.append(">{} {}: {}".format(filename, lineno + offset, self.tm.source[(filename, lineno + offset)]))
                    else:
                        lines.append(" {} {}: {}".format(filename, lineno + offset, self.tm.source[(filename, lineno + offset)]))
                if offset > 0 and (filename, lineno - offset) in self.tm.source:
                    lines.insert(0," {} {}: {}".format(filename, lineno - offset, self.tm.source[(filename, lineno - offset)]))
                if lines_displayed >= self.listsize:
                    break

            if lines:
                for line in lines:
                    print(line)
            else:
                print("unable to find source")
            return False

        if cmd[0] in ("b", "break"):
            if len(cmd) == 2:
                self.breakpoints.add(cmd[1])
            else:
                self.breakpoints.add(self.tm.statename)
            return False

        if cmd[0] in ("clear"):
            self.breakpoints = set()
            return False

        if cmd[0] in ("info"):
            if cmd[1] in ("b", "break", "breakpoints"):
                for bp in self.breakpoints:
                    if bp in self.tm.states:
                        filename = self.tm.states[bp]['filename']
                        lineno = self.tm.states[bp]['lineno']
                        print("{} {}: {}".format(filename, lineno, self.tm.source[(filename, lineno)]))
                    else:
                        print(bp)
            if cmd[1] in ("registers"):
                i = -len(self.tm.left)
                while self.tm.tape_at(i) == self.tm.fill and i < len(self.tm.right):
                    i = i + 1
                while i < len(self.tm.right):
                    count = 0
                    symbol = self.tm.tape_at(i)
                    while self.tm.tape_at(i) == symbol and i < len(self.tm.right):
                        count = count + 1
                        i = i + 1
                    if symbol != self.tm.fill or i < len(self.tm.right):
                        print("{} x {}".format(symbol, count))
            return False

        return True # by default print information


    def mainloop(self):
        lastcommand = ""

        while not self.quit:
            cmd = input("(tmdb) ")
            if cmd == "" and self.repeatcommand:
                cmd = lastcommand
            lastcommand = cmd
            try:
                printstatus = self.processcommand(cmd)
            except Exception:
                traceback.print_exc()
                printstatus = True

            if printstatus:
                if len(self.tm.left) >= 35:
                    left = "".join(self.tm.left[-35:])
                else:
                    left = (("0" * 35) + "".join(self.tm.left))[-35:]
                if len(self.tm.right) >= 35:
                    right = "".join(reversed(self.tm.right[-35:]))
                else:
                    right = ("".join(reversed(self.tm.right)) + ("0" * 35))[:35]
                print("{}[{}]{}".format(left,self.tm.symbol,right))
                if (self.tm.statename, self.tm.symbol) in self.tm.states:
                    state = self.tm.states[(self.tm.statename, self.tm.symbol)]
                    print("{} {}".format(state.lineno, self.tm.source[(state.filename, state.lineno)]))
                    if self.tm.statename in self.breakpoints:
                        print("Breakpoint")
                    elif self.tm.looping:
                        print("looping detected")

                else:
                    if self.tm.statename == "HLT":
                        print("HALTED")
                    else:
                        print("Undefined transition: {} {}".format(self.tm.statename, self.tm.symbol))


import argparse

parser = argparse.ArgumentParser(description="Debugger for Turing machines")
parser.add_argument("TM_Files", metavar="TM_File", help="Turing Machine file", nargs="*")

args = parser.parse_args()

if __name__ == '__main__':
    tmdb = TMDB()
    for fname in args.TM_Files:
        tmdb.tm.load(fname)
    tmdb.mainloop()
