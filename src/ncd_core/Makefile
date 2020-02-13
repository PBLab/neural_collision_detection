
SOURCES=main.cpp model.cpp collision.cpp collision_manager.cpp program.cpp result_object.cpp trace.cpp bounding_box.cpp cube.cpp
OBJS = $(SOURCES:.cpp=.o)
CFLAGS += -O2 -std=c++11 -Iinclude -static
LDFLAGS += -static -Lexternal
#LDFLAGS += -static -L/home/yoav/cg/new_fcl/fcl/build/src/CMakeFiles/fcl.dir
#LDFLAGS =


all: $(OBJS)
	g++ $(OBJS) -lfcl -lstdc++ -o ncd -lpthread -lfcl -lstdc++ -lccd $(LDFLAGS)
	strip ncd
clean:
	rm -f ncd *.o
run:
	./base_run.sh

%.o : %.cpp
	@date
	g++ -c $(CFLAGS) $< -o $@
