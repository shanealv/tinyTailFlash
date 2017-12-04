declare -a configs=("nogc" "def" "pbl" "gtr" "rgc")
declare -a traces=("DTRS")
declare -a stimes=("43200000378000")
declare basePlt=cdf/gen/base.plt
declare dat=cdf/gen/dat
declare eps=cdf/gen/eps
declare plt=cdf/gen/plt

make clean 
make

# remove previously generated folders/files
rm -r -f $dat
rm -r -f $eps
rm -r -f $plt

# create necessary folders
mkdir -p $dat
mkdir -p $eps
mkdir -p $plt

# for all traces
for index in ${!traces[*]};
do
	trace=${traces[$index]}
	stime=${stimes[$index]}
	export stats_time=$stime
	# generate the data output folder for the trace
	mkdir $dat/$trace 

	# generate a plot file for the trace
	cp $basePlt $plt/$trace.plt
	sed -i -e "s/TRACE/$trace/g" $plt/$trace.plt 

	for c in "${configs[@]}"
	do
		# configure and execute on the trace
		cp configs/$c.config page.parameters
		./ssd traces/$trace.trace

		# generate data from the output
		python bin/cdf data/raw-data/read_time $dat/$trace/$c.dat
	done
done

# make plots for all outputs and display them
gnuplot cdf/gen/plt/*.plt
evince $eps/*.eps
