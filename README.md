# Tiny Tail Flash SSDSim
Modified by Shane Alvarez & Charles Good

## Getting Started
To run the experiment for any trace file, execute run.sh:

```
./run.sh
```

**NOTE**: You will need to modify this trace file for every additional trace you plan to use.
This file tracks the names of traces along with their start times.
The script will build TTFlash and run it on each declared trace file several times for each TTFlash configuration.
After each trace is used, it will output a CDF plot in the form of EPS file in cdf/gen/eps

For additional traces, you can download them from [http://iotta.snia.org/tracetypes/3]
For Microsoft's Production Server Traces, you can convert individual trace CSV files with the provided python file:

```
	cd traces
	python3 parse.py [path to trace.csv] [name]
```

If no arguments are provided, then it will run a set script for whatever file/name pairs are provided.  (Currently references untracked files).

Once the traces are generated, they must be added to run.sh to execute them.  Additionally, the start time fo the trace file should be recorded in run.sh as well.

