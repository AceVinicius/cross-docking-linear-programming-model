PLATFORM = linux64
INC      = /opt/gurobi810/linux64/include/
CPP      = g++
CARGS    = -m64 -g
#CLIB     = -L /opt/gurobi800/linux64/lib/ -lgurobi80
CPPLIB   = -L/opt/gurobi810/linux64/lib/ -lgurobi_c++ -lgurobi81
#JFLAG    = -d . $(CLASSDIR)

main: main.cc
	   $(CPP) $(CARGS) -o main main.cc -I$(INC) $(CPPLIB) -lm
clean:
	rm -rf *.o main
	
# /home/eduardo/teste/mip1_c++.cpp
#	       $(CPP) $(CARGS) -o $@ $< -I$(INC) $(CPPLIB) -lm

