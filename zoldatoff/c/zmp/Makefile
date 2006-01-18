zmp: main.o interface.o explorer.o playlist.o idtag.o
	gcc -O2 -Wall -lncursesw -lid3tag -lSDL_mixer -o zmp main.o interface.o explorer.o playlist.o idtag.o

interface.o: interface.c zmp.h
	gcc -g -Wall -c interface.c

explorer.o: explorer.c zmp.h
	gcc -g -Wall -c explorer.c

playlist.o: playlist.c zmp.h
	gcc -g -Wall -c playlist.c

idtag.o: idtag.c zmp.h
	gcc -g -Wall -c idtag.c

main.o: main.c interface.o explorer.o playlist.o idtag.o zmp.h
	gcc -g -Wall -c main.c


