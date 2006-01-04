#include <curses.h>
#define PLAYLIST_COLOR 1
#define SONG_INFO_COLOR 2

void clrscr(WINDOW *window);
int draw_windows();

int main(int argc, char *argv) {
	draw_windows();
//	char key;
	return 0;	
}

void clrscr(WINDOW *window) {
	int y, x, maxy, maxx;
	getmaxyx(window, maxy, maxx);
	for(y=0; y < maxy; y++)
		for(x=0; x < maxx; x++)
			mvaddch(y, x, ' ');
}

void wprintTitleCentered(WINDOW *window, const char *titleText) {
		int x, maxy, maxx;

		getmaxyx(window,maxy,maxx);
		x = (maxx - 4 - strlen(titleText))/2;
		mvwprintw(window,0,x,"| %s |",titleText);
		/*mvwaddch(window, 0, x, ACS_RTEE);
		waddch(window, ' ');
		waddstr(window, titleText);
		waddch(window, ' ');
		waddch(window, ACS_LTEE);*/
}

int draw_windows() {
	WINDOW *playlist;
	playlist = initscr();

/*	int y, x, maxy, maxx;
	getmaxyx(stdscr, maxy, maxx); 	//size of screen
*/
	start_color(); 			//colors initialization
	init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
	init_pair(SONG_INFO_COLOR, COLOR_WHITE, COLOR_BLACK);	
	attrset(COLOR_PAIR(PLAYLIST_COLOR));
	
	clrscr(playlist);
	box(playlist, ACS_VLINE, ACS_HLINE); 
	wprintTitleCentered(playlist, "Playlist");
	
	mvaddstr(10,10,"Test");
	refresh();

	sleep(3);
	delwin(playlist);
	endwin();
	refresh();

	return 0;
}
