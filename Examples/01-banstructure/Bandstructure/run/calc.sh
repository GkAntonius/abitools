#!/bin/bash


MPIRUN="mpirun -np 4 "
EXECUTABLE=abinit
INPUT=/Users/Antonius/Work/kTools/abitools/Examples/01-banstructure/Bandstructure/run/calc.files
LOG=/Users/Antonius/Work/kTools/abitools/Examples/01-banstructure/Bandstructure/run/calc.log
STDERR=stderr



$MPIRUN $EXECUTABLE < $INPUT > $LOG 2> $STDERR

