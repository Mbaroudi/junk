DEBUG=-ggdb #-fprofile-arcs -ftest-coverage
CC=gcc #$(DEBUG)
CFLAGS=-O2 -c -Wall
LDFLAGS=-lncursesw -lid3tag -lSDL_mixer

SOURCES=interface.c explorer.c playlist.c idtag.c main.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=zmp

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) $(CFLAGS) $< -o $@

clean: 
	rm -f *.bb *.bbg *.da *.out *.gcov *.gcno *.gcda *~ $(EXECUTABLE) $(OBJECTS)
