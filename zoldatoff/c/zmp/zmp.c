#include <curses.h>
#include <string.h>
#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define SONG_INFO_COLOR 3

void draw_window(WINDOW *window,int color_pair,int attrib,char *titleText);

int main(int argc, char *argv[]) {
	initscr();
	touchwin(stdscr);
	wrefresh(stdscr); 	//I don't know why this is necessary, but it is!
	start_color(); 		//colors initialization
	init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
	init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
	init_pair(SONG_INFO_COLOR, COLOR_YELLOW, COLOR_BLACK);	

	int maxy, maxx;
	getmaxyx(stdscr,maxy,maxx);
	
	WINDOW *base_win, *playlist_win, *song_info_win;
	base_win = newwin(maxy, maxx, 0, 0);
	draw_window(base_win, BASEWIN_COLOR, WA_BOLD, "Z");
	playlist_win = newwin(maxy-2, (3*maxx)/4 - 1, 1, maxx/4);
	draw_window(playlist_win, PLAYLIST_COLOR, WA_BOLD, "P");
	song_info_win = newwin(maxy-2, maxx/4 - 1, 1, 1);
	draw_window(song_info_win, SONG_INFO_COLOR, WA_BOLD, "S");
	
	wattrset(song_info_win, COLOR_PAIR(SONG_INFO_COLOR) | WA_BOLD);
	mvwprintw(song_info_win,4,1,"zaebis");
	//touchwin(base_win);
	wrefresh(base_win);
	//touchwin(playlist_win);
	wrefresh(playlist_win);
	touchline(song_info_win,1,maxy-3);
	//touchwin(song_info_win);
	wrefresh(song_info_win);
	refresh();
	
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

void draw_window(WINDOW *window,int color_pair,int attrib,char *titleText) {
	wattrset(window, COLOR_PAIR(color_pair) | attrib);
	wclrscr(window);
	box(window, 0, 0);
	wprintTitleCentered(window, titleText);
	touchwin(window);
	wrefresh(window);
}

