#include <curses.h>
#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define SONG_INFO_COLOR 3

void draw_window(WINDOW *window,int size_y,int size_x,int y,int x,int color_pair,int attrib,char *titleText);

int main(int argc, char *argv) {
	initscr();
	touchwin(stdscr);
	wrefresh(stdscr); 	//I don't know why this is necessary, but it is!
	start_color(); 		//colors initialization
	init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
	init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
	init_pair(SONG_INFO_COLOR, COLOR_WHITE, COLOR_BLACK);	

	int x, maxy, maxx;
	getmaxyx(stdscr,maxy,maxx);
	
	WINDOW *base_win, *playlist_win, *song_info_win;
	draw_window(base_win, maxy, maxx, 0, 0, BASEWIN_COLOR, WA_BOLD, "Zoldatoff media player");
	draw_window(playlist_win, maxy-2, (3*maxx)/4 - 1, 1, maxx/4, PLAYLIST_COLOR, WA_BOLD, "Playlist");
	draw_window(song_info_win, maxy-2, maxx/4 - 1, 1, 1, SONG_INFO_COLOR, WA_BOLD, "Song info");
	
	getch();
	delwin(playlist_win); 	//kill all windows
	delwin(song_info_win); 	//kill all windows
	endwin(); 		//end curses environment
	return 0;	
}

void wclrscr(WINDOW *window) {
	int y, x, maxy, maxx;
	getmaxyx(window, maxy, maxx);
	for(y=0; y < maxy; y++)
	for(x=0; x < maxx; x++)
		mvwaddch(window, y, x, ' ');
}

void wprintTitleCentered(WINDOW *window, const char *titleText) {
	int x, maxy, maxx;
	getmaxyx(window,maxy,maxx);
	x = (maxx - 4 - strlen(titleText))/2;
	mvwprintw(window,0,x,"| %s |",titleText);
}

void draw_window(WINDOW *window,int size_y,int size_x,int y,int x,int color_pair,int attrib,char *titleText) {
	window = newwin(size_y, size_x, y, x);
	wattrset(window, COLOR_PAIR(color_pair) | attrib);
	wclrscr(window);
	box(window, 0, 0);
	wprintTitleCentered(window, titleText);
	touchwin(window);
	wrefresh(window);
}

