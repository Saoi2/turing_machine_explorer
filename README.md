# turing_machine_explorer

Utilities for creating, optimizing and debugging turing machines.

## tmdb.py

Turing machine debugger, loosly based on gdb and pydb.

## zf2.py

Produces a Turning machine with 385 states that halts if it finds an
inconsistency in ZF2. This is a port of zf2.nql in
<https://github.com/CatsAreFluffy/metamath-turing-machines> to a python list based
intermediate representation. This is in turn compiled to a slightly different
register machine than used by NQL.

### usage:

```
$./zf2.py
states count:
framework:    96
decision DAG: 289
total:        385
(tmdb) save zf2.tm
(tmdb) q
```

Other useful tmdb commands are "`break main().0`",
"`c 1000`" (continue past 1000 breakpoints), and "`info tape`".

## TMBuilder.py

A framework for building Turing machines consisting of a register machine
emulator and a decision DAG for the program being compiled. This register
machine is similar to the one in NQL, but there are a few differences:

* The PC is not fixed size and the decision DAG is not constant height.

* The sense of decnz is reversed from decz in NQL: if the decnz is in a car
  the corresponding cdr of the cons will be executed if the register being
  decremented was non-zero.

* A glitch where a register is added to the register file for every successful
  decnz. We take advantage of this to initialize the register file cheaply.

