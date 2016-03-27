#!/bin/bash


MPIRUN="mpirun -np 4 "
EXECUTABLE=/Users/Antonius/Work/Software/Abinit/8.0.0-private/build1/src/98_main/abinit
INPUT=/Users/Antonius/Work/kTools/abitools/Examples/02-convergence/Kptconv-4/run/calc.files
LOG=/Users/Antonius/Work/kTools/abitools/Examples/02-convergence/Kptconv-4/run/calc.log
STDERR=stderr



$MPIRUN $EXECUTABLE < $INPUT > $LOG 2> $STDERR

