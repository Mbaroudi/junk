#include <curses.h>

int main() {
	draw_windows();
//	char key;
	return 0;	
}

int draw_windows () {
	WINDOW *playlist;
	playlist = initscr();
	mvaddstr(10,10,"Test");
	refresh();

	sleep(3);
	delwin(playlist);
	endwin();
	refresh();

	return 0;
}
