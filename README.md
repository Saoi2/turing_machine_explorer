# turing_machine_explorer

Utilities for creating, optimizing and debugging turing machines.

## tmdb.py

Turing machine debugger, loosly based on gdb and pydb.

## framework.pm

Exploring ideas based on the register machine in <https://github.com/sorear/metamath-turing-machines> but with a variable-depth decision tree. This requires extra states to handle the transition from the decision tree to the register file and back, (2 extra states per register plus some extra overhead), but my hope is that without alignment concerns the program running on the register machine can be encoded more compactly with greater sharing of subtrees.
