#include <curses.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>

#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define SONG_INFO_COLOR 3

void draw_window(WINDOW *window,int color_pair,int attrib,char *titleText);
void listDir(WINDOW *window, char *directory);

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
	
//	mvwprintw(song_info_win,4,1,"zaebis");
//	wrefresh(song_info_win);

	listDir(playlist_win,"/");
	wrefresh(playlist_win);
	
	getch();
	delwin(base_win); 	//kill all windows
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

void listDir(WINDOW *window, char *directory) {
	DIR *dp;
	struct dirent *ep;
	int i=0;
	
	dp = opendir (directory);
	if (dp != NULL) {
		while (ep=readdir(dp)) {
			i++;
			mvwprintw(window,i,1,"%s",ep->d_name);
		}
		(void) closedir (dp);
	}
	else
	mvwprintw(window,1,1,"No such dir");
}
