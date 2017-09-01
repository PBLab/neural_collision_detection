
SOURCES=main.cpp model.cpp collision.cpp collision_manager.cpp program.cpp result_object.cpp trace.cpp
OBJS = $(SOURCES:.cpp=.o)
CFLAGS += -O2 -std=c++11 -I/usr/include/eigen3/ -static
LDFLAGS += -static -L/home/yoav/cg/fcl/build/src/CMakeFiles/fcl.dir
#LDFLAGS =


all: $(OBJS)
	g++ $(OBJS) -lfcl -lstdc++ -o ncd -L/home/yoav/cg/fcl/build/lib -lpthread -lfcl -lstdc++ -lccd $(LDFLAGS)
clean:
	rm -f ncd *.o
run:
	./base_run.sh

%.o : %.cpp
	@date
	g++ -c $(CFLAGS) $< -o $@
