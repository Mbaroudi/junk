zmp: main.o interface.o explorer.o playlist.o idtag.o
	gcc -g -Wall -lncurses -o zmp main.o interface.o explorer.o playlist.o

main.o: main.c interface.h explorer.h playlist.h idtag.h
	gcc -g -Wall -c main.c

interface.o: interface.c zmp.h
	gcc -g -Wall -c interface.c

explorer.o: explorer.c zmp.h
	gcc -g -Wall -c explorer.c

playlist.o: playlist.c zmp.h
	gcc -g -Wall -c playlist.c

idtag.o: idtag.c zmp.h
	gcc -g -Wall -c idtag.c
