
SOURCES=main.cpp model.cpp collision.cpp collision_manager.cpp program.cpp result_object.cpp trace.cpp bounding_box.cpp cube.cpp
OBJS = $(SOURCES:.cpp=.o)
CFLAGS += -O2 -std=c++11 -Iinclude -static
LDFLAGS += -Lexternal -static
LDFLAGS += -L/usr/lib/x86_64-redhat-linux6E/lib64/


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
