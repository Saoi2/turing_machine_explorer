#!/usr/bin/python3

import sys
import argparse
import traceback

class TuringMachine:
    def __init__(self):
        self.entry = "HLT"
        self.states = {}
        self.statename = "HLT"
        self.source = {}
        self.stdin_state_lineno = 1
        self.left = []
        self.right = []
        self.tape = "0"
        self.stepcount = 0
        self.statetrace = [("HLT", '0', 0)]
        self.looping = False

    def tape_at(self, index):
        if index == 0:
            return self.state
        elif index < 0 and len(self.left) <= -index:
            return self.left[len(self.left) + index]
        elif index > 0 and len(self.right) <= index:
            return self.right[len(self.right) - index]
        else:
            return '0'

    def load(self, filename):
        linenumber = 1
        with open(filename,"r") as f:
            for l in f:
                l = l.rstrip()
                self.source[(filename, linenumber)] = l.rstrip()
                l = l.strip()
                if "=" in l:
                    self.loadstate(l, filename, linenumber)
                linenumber = linenumber + 1

    def loadstate(self, line, filename="<STDIN>", linenumber=None):

        (name, rhs) = line.split("=", 1)
        name = name.strip()
        rhs = rhs.strip().split()
        if not rhs:
            del self.states[name]
            return True
        state = {'0': None, '1': None, 'name': name, 'filename': filename, 'lineno': linenumber or self.stdin_state_lineno}
        if rhs[0] != "*":
            if len(rhs) not in (4, 6) or rhs[0] not in ('0', '1') or rhs[1] not in ('l', 'r'):
                return False
            state['0'] = (rhs[0], rhs[1], rhs[2])
        if rhs[-1] != "*":
            if len(rhs) not in (4, 6) or rhs[-3] not in ('0','1') or rhs[-2] not in ('l', 'r'):
                return False
            state['1'] = (rhs[-3], rhs[-2], rhs[-1])

        if not linenumber:
            self.source[("<STDIN>", self.stdin_state_lineno)] = line
            self.stdin_state_lineno = self.stdin_state_lineno + 1

        if self.entry not in self.states:
            self.entry = name # First state in file

        self.states[name] = state

        return True

    def printstate(self, state):
        rv = "{} = ".format(state['name'])
        if state['0']:
            rv += "{} {} {} ".format(*state['0'])
        else:
            rv += "* "
        if state['1']:
            rv += "{} {} {}".format(*state['1'])
        else:
            rv += "*"

        return rv

    def save(self, filename):
        with open(filename, "w") as f:
            if self.entry in self.states:
                f.write("{}\n".format(self.printstate(self.states[self.entry])))
            for statename in sorted(x for x in self.states if x != self.entry):
                f.write("{}\n".format(self.printstate(self.states[statename])))



    def step(self):
        self.looping = False
        try:
            state = self.states[self.statename]
        except KeyError:
            return False
        half=state[self.tape]
        if not half:
            return False
        tape = half[0]
        if half[1] == 'l':
            self.right.append(tape)
            if self.left:
                self.tape = self.left.pop()
            else:
                self.tape = '0'
                looping = state['0'] and state['0'][2] == self.statename
        else:
            self.left.append(tape)
            if self.right:
                self.tape = self.right.pop()
            else:
                self.tape = '0'
                looping = state['0'] and state['0'][2] == self.statename

        self.statename = half[2]
        if (self.statename, self.tape) == self.statetrace[0][:2]:
            self.statetrace[0] = (self.statename, self.tape, self.statetrace[0][2] + 1)
        else:
            self.statetrace = [(self.statename, self.tape, 1)] + self.statetrace[:10]

        return True

class TMDB:

    def __init__(self):
        self.tm = TuringMachine()
        self.breakpoints = set()
        self.quit = False
        self.repeatcommand = False
        self.listsize = 10

    def repeatcount(self, cmd):
        if len(cmd) == 2 and isnumeric(cmd[1]):
            return int(cmd[1])
        else:
            return 1

    def processcommand(self, cmd):

        self.repeatcommand = False

        if "=" in cmd:
            if not self.tm.loadstate(cmd):
                print("Could not parse state")
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
            self.tm.tape = '0'
            self.tm.statename = self.tm.entry
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

        if cmd[0] in ("entry"):
            if len(cmd) != 2:
                print("entry [state]")
                return False
            self.tm.entry = cmd[1]
            return False

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

        if cmd[0] in ("bt", "backtrace"):
            for trace in reversed(self.tm.statetrace):
                state = self.tm.states[trace[0]]
                if state:
                    print("{} [{}] x {}: {}".format(state['lineno'], trace[1], trace[2],
                        self.tm.source[(state['filename'], state['lineno'])]))
                else:
                    print("   [{}] x {}: {} = **undefined**".format(trace[1], trace[2], trace[0]))
            return False

        if cmd[0] in ("set"):
            if len(cmd) > 2 and cmd[1] in ("listsize") and cmd[2].isnumeric():
                self.listsize = int(cmd[2])
                return False

        if cmd[0] in ("l", "list"):
            listing = []
            filename = None
            lineno = 1
            if self.tm.statename in self.tm.states:
                filename = self.tm.states[self.tm.statename]['filename']
                lineno = self.tm.states[self.tm.statename]['lineno']
            if len(cmd) > 1:
                if ":" not in cmd[1]:
                    statename = cmd[1].split(",")[0] # range is unsupported we just use the start
                    if statename in self.tm.states:
                        filename = self.tm.states[statename]['filename']
                        lineno = self.tm.states[statename]['lineno']
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
                print("{}[{}]{}".format(left,self.tm.tape,right))
                if self.tm.statename in self.tm.states:
                    state = self.tm.states[self.tm.statename]
                    print("{} {}".format(state['lineno'], self.tm.source[(state['filename'], state['lineno'])]))
                    if self.tm.statename in self.breakpoints:
                        print("Breakpoint")
                    elif not state[self.tm.tape]:
                        print("Undefined Transition")
                    elif self.tm.looping:
                        print("looping detected")

                else:
                    if self.tm.statename == "HLT":
                        print("HALTED")
                    else:
                        print("Undefined state: {}".format(self.tm.statename))


import argparse

parser = argparse.ArgumentParser(description="Debugger for Turing machines")
parser.add_argument("TM_Files", metavar="TM_File", help="Turing Machine file", nargs="*")

args = parser.parse_args()

if __name__ == '__main__':
    tmdb = TMDB()
    for fname in args.TM_Files:
        tmdb.tm.load(fname)
    tmdb.mainloop()
