#include <curses.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>

#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define SONG_INFO_COLOR 3
#define EXPLORER_COLOR 4
#define EXPLORER_SEL_COLOR 5

#define MAX_FILE_NAME 256
#define MAX_LIST 1024

#define ENTER '\n'           	//carriage return (enter key)
#define ESC 0x1b               	//Escape key
#define TAB 0x09               	//Tab key
#define SPACE ' '
//#define LF 0x0a               //Line feed
//#define BACKSPACE 0x08        //Backspace
//#define SAVE 0x13             //Ctrl-S for Save
//#define HELP 0x08             //Ctrl-H for Help
//#define QUIT 0x11             //Ctrl-Q for Quit

void draw_window(WINDOW *window,int color_pair,int attrib,char *titleText);
int listDir(char *directory, char dir_list[MAX_LIST][MAX_FILE_NAME+1]);
void draw_explorer(WINDOW *window, char dir_list[MAX_LIST][MAX_FILE_NAME+1], int explorer_item);

int main(int argc, char *argv[]) {
	initscr();
	noecho(); 	//no output to terminal
	raw(); 		//no buffering
	keypad(stdscr,TRUE);
	touchwin(stdscr);
	wrefresh(stdscr); 	//I don't know why this is necessary, but it is!
	start_color(); 		//colors initialization
	init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
	init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
	init_pair(SONG_INFO_COLOR, COLOR_YELLOW, COLOR_BLACK);	
	init_pair(EXPLORER_COLOR, COLOR_GREEN, COLOR_BLACK);	
	init_pair(EXPLORER_SEL_COLOR, COLOR_BLACK, COLOR_GREEN);	

	int i, maxy, maxx;
	getmaxyx(stdscr,maxy,maxx);
	
	WINDOW *base_win, *playlist_win, *song_info_win, *explorer_win;
	base_win = newwin(maxy, maxx, 0, 0);
	draw_window(base_win, BASEWIN_COLOR, WA_BOLD, "Zoldatoff Media Player");
	explorer_win = newwin(maxy-2, maxx-2, 1, 1);
	draw_window(explorer_win, EXPLORER_COLOR, WA_BOLD, "Explorer");
	playlist_win = newwin(maxy-2, (3*maxx)/4 - 1, 1, maxx/4);
	draw_window(playlist_win, PLAYLIST_COLOR, WA_BOLD, "Playlist");
	song_info_win = newwin(maxy-2, maxx/4 - 1, 1, 1);
	draw_window(song_info_win, SONG_INFO_COLOR, WA_BOLD, "Song");
	
	char dir_list[MAX_LIST][MAX_FILE_NAME+1], playlist[MAX_LIST][MAX_FILE_NAME+1];
	int key, playlist_item=0, max_playlist_item=0, explorer_item=0, max_explorer_item=0, show_explorer=0;
	char *current_dir="/";

	max_explorer_item = listDir(current_dir, dir_list);
	mvwprintw(song_info_win,1,1,"max_expl=%d",max_explorer_item);
	wrefresh(song_info_win);
	
	i=2;
	keypad(playlist_win,TRUE);
	keypad(song_info_win,TRUE);
	keypad(base_win,TRUE);
	while (1) {
		key = wgetch(playlist_win);
		if (key=='q') break;
		switch (key) {
			case KEY_DOWN: 
				if (show_explorer) explorer_item++;
				else playlist_item++;
				
				if (explorer_item==max_explorer_item+1) explorer_item=0;
				if (playlist_item==max_playlist_item+1) playlist_item=0;
				
				draw_explorer(explorer_win,dir_list,explorer_item);
				break;
			case KEY_UP:
				if (show_explorer) explorer_item--;
				else playlist_item--;
				
				if (explorer_item==-1) explorer_item=max_explorer_item;
				if (playlist_item==-1) playlist_item=max_playlist_item;

				draw_explorer(explorer_win,dir_list,explorer_item);
				break;
			case KEY_LEFT:
				mvwprintw(song_info_win,i,1,"KEY_LEFT");
				wrefresh(song_info_win);
				i++;
				break;
			case KEY_RIGHT:
				mvwprintw(song_info_win,i,1,"KEY_RIGHT");
				wrefresh(song_info_win);
				i++;
				break;
			case TAB:
				if (!show_explorer) {
					draw_explorer(explorer_win,dir_list,explorer_item);
					show_explorer=1;
				}
				else {
					touchwin(song_info_win);
					touchwin(playlist_win);
					wrefresh(song_info_win);
					wrefresh(playlist_win);
					show_explorer=0;
				}	
				break;
			case SPACE:
				mvwprintw(song_info_win,i,1,"Space");
				wrefresh(song_info_win);
				i++;
				break;
			case ENTER:
				mvwprintw(song_info_win,i,1,"Enter");
				wrefresh(song_info_win);
				i++;
				break;
			case ESC:
				mvwprintw(song_info_win,i,1,"ESC");
				wrefresh(song_info_win);
				i++;
				break;
			case KEY_F(1):
				mvwprintw(song_info_win,i,1,"F1");
				wrefresh(song_info_win);
				i++;
				break;
			case 'w':
				mvwprintw(song_info_win,i,1,"w");
				wrefresh(song_info_win);
				i++;
			default:
				mvwprintw(song_info_win,i,1,"%c",key);
				wrefresh(song_info_win);
				i++;
				break;
		}
	}
	
	delwin(base_win); 	//kill all windows
	delwin(playlist_win); 	//kill all windows
	delwin(song_info_win); 	//kill all windows
	endwin(); 		//end curses environment
	return 0;	
}

void wclrscr(WINDOW *window) {
	int y, x, maxy, maxx;
	getmaxyx(window, maxy, maxx);
	for(y=1; y < maxy-1; y++)
	for(x=1; x < maxx-1; x++)
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

int listDir(char *directory, char dir_list[MAX_LIST][MAX_FILE_NAME+1]) {
	DIR *dp;
	struct dirent *ep;
	int i=-3;
	
	dp = opendir (directory);
	if (dp != NULL) {
		while (ep=readdir(dp)) {
			i++;
			if (i>=0) strcpy(dir_list[i],ep->d_name);
		}
		(void) closedir (dp);
	}
	return i;
}

void draw_explorer(WINDOW *window, char dir_list[MAX_LIST][MAX_FILE_NAME+1], int explorer_item) {
	int i;

	wclrscr(window);
	for (i=0; i<MAX_LIST; i++) {
		if (i==explorer_item) wattrset(window, COLOR_PAIR(EXPLORER_SEL_COLOR) | WA_BOLD);
		else wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
		if (dir_list[i]!="") mvwprintw(window,i+1,1,"%s",dir_list[i]);
		else break;
	}
	touchwin(window);
	wrefresh(window);
}
