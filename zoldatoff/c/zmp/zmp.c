#include <curses.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define PLAYLIST_SEL_COLOR 3
#define SONG_INFO_COLOR 4
#define EXPLORER_COLOR 5
#define EXPLORER_SEL_COLOR 6

#define MAX_FILE_NAME 256
#define MAX_LIST 1024
#define MAX_TAG 128

#define ENTER '\n'           	//carriage return (enter key)
#define ESC 0x1b               	//Escape key
#define TAB 0x09               	//Tab key
#define SPACE ' '
#define PG_UP 0x153
//#define LF 0x0a               //Line feed
//#define BACKSPACE 0x08        //Backspace
//#define SAVE 0x13             //Ctrl-S for Save
//#define HELP 0x08             //Ctrl-H for Help
//#define QUIT 0x11             //Ctrl-Q for Quit

struct filelist {
	char f_name[MAX_FILE_NAME];
	char f_type;
};

struct playlist {
	char f_name[MAX_FILE_NAME];
	char path[MAX_FILE_NAME];
	char song[MAX_TAG];
	char artist[MAX_TAG];
	char genre[MAX_TAG];
	char album[MAX_TAG];
};

void wclrscr(WINDOW *window);

void drawWindow(WINDOW *window,int color_pair,char *titleText);

int listDir(char *directory, struct filelist *dir_list[]);

void drawExplorer(WINDOW *window, 
		struct filelist *dir_list[], 
		int explorer_item, 
		int max_explorer_item);

void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item); 		//change to simply item, please....

addtoPlaylist(struct playlist play_list,
		struct dirlist dir_list,
		char current_dir[],
		int explorer_item,
		int max_playlist_item);

char *upDir(char directory[]);
//==============================================================
int main(int argc, char *argv[])
{
        initscr();
        noecho(); 	//no output to terminal
        raw(); 		//no buffering
	curs_set(0);
        keypad(stdscr,TRUE);
        touchwin(stdscr);
        wrefresh(stdscr); 	//I don't know why this is necessary, but it is!
	
	//Colors initialization
        start_color();
        init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
        init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
        init_pair(PLAYLIST_SEL_COLOR, COLOR_RED, COLOR_BLUE);
        init_pair(SONG_INFO_COLOR, COLOR_YELLOW, COLOR_BLACK);
        init_pair(EXPLORER_COLOR, COLOR_GREEN, COLOR_BLACK);
        init_pair(EXPLORER_SEL_COLOR, COLOR_GREEN, COLOR_BLUE);

        int maxy, maxx;
        WINDOW *base_win, *playlist_win, *song_info_win, *explorer_win;
	
	// Draw windows
        getmaxyx(stdscr,maxy,maxx);
        base_win = newwin(maxy, maxx, 0, 0);
        drawWindow(base_win, BASEWIN_COLOR, "Zoldatoff Media Player");
        explorer_win = newwin(maxy-2, maxx-2, 1, 1);
        drawWindow(explorer_win, EXPLORER_COLOR, "Explorer");
        playlist_win = newwin(maxy-2, (3*maxx)/4 - 1, 1, maxx/4);
        drawWindow(playlist_win, PLAYLIST_COLOR, "Playlist");
        song_info_win = newwin(maxy-2, maxx/4 - 1, 1, 1);
        drawWindow(song_info_win, SONG_INFO_COLOR, "Song");
        keypad(playlist_win,TRUE);
        keypad(song_info_win,TRUE);
        keypad(base_win,TRUE);
	
	//Arrays of directory listing and playlist
        struct playlist *play_list[MAX_LIST];
	struct filelist *dir_list[MAX_LIST];
		
	int t;
	for (t=0; t<MAX_LIST; t++)
		dir_list[t] = NULL;
	
        char current_dir[MAX_FILE_NAME]="/";
        int playlist_item=0, max_playlist_item=-1;
        int explorer_item=0, max_explorer_item=0, show_explorer=0;

        max_explorer_item = listDir(current_dir, dir_list);

        int key, i=2;  //i is unneeded!!
	
        while (1) {
                key = wgetch(playlist_win);
                if (key=='q')
                        break;
                switch (key) {
                case KEY_DOWN: 		//scroll list down (done)
                        if (show_explorer)
                                explorer_item++;
                        else
                                playlist_item++;

                        if (explorer_item==max_explorer_item+1)
                                explorer_item=0;
                        if (playlist_item==max_playlist_item+1)
                                playlist_item=0;

                        if (show_explorer) 
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			else
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
                        break;
                case KEY_UP: 		//scroll list up (done)
                        if (show_explorer)
                                explorer_item--;
                        else
                                playlist_item--;

                        if (explorer_item==-1)
                                explorer_item=max_explorer_item;
                        if (playlist_item==-1)
                                playlist_item=max_playlist_item;

                        if (show_explorer)
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			else
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
                        break;
                case TAB: 		//switch between playlist & explorer (done)
                        if (!show_explorer) {
                                drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
                                show_explorer=1;
                        } 
			else {
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
                                touchwin(song_info_win);
                                wrefresh(song_info_win);
                                show_explorer=0;
                        }
                        break;
		case SPACE: 		//TODO: mark files and playlist items
                        mvwprintw(song_info_win,i,1,"Space");
                        wrefresh(song_info_win);
                        i++;
                        break;
                case KEY_RIGHT: 	//as Enter....
                case ENTER: 		//add to playlist //play selected song //go to folder
			if (show_explorer && dir_list[explorer_item]) {
				strcat(current_dir, dir_list[explorer_item]->f_name);
				strcat(current_dir, "/");
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item=0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        break;
                case KEY_LEFT: 	//go up one dir (done)
		case PG_UP: 	//go up one dir (done)
			if (show_explorer) {
				strcpy(current_dir, upDir(current_dir));
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item=0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			break;
		case 'a': 		//add files to playlist
			if (show_explorer && dir_list[explorer_item]) {
				addtoPlaylist(play_list,dir_list,current_dir,explorer_item,max_playlist_item);
                                explorer_item++;
                        	if (explorer_item==max_explorer_item+1)
                                	explorer_item=max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			break;
		case 'd': 		//delete items from playlist
			break;
		case '+': 		//volume up
			break;
		case '-': 		//volume down
		case '=': 		//volume down
			break; 		
                case ESC: 		//do you want to exit?
                        mvwprintw(song_info_win,i,1,"ESC");
                        wrefresh(song_info_win);
                        i++;
                        break;
                case KEY_F(1): 		//help & something else .............
                        mvwprintw(song_info_win,i,1,"F1");
                        wrefresh(song_info_win);
                        i++;
                        break;
                case 'w': 		//write configuration (what configuration?)
                        mvwprintw(song_info_win,i,1,"w");
                        wrefresh(song_info_win);
                        i++;
                default: 		//what is this doing here?!
                        mvwprintw(song_info_win,i,1,"%x",key);
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

void wclrscr(WINDOW *window) 		//clear the space inside the window
{
        int y, x, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        for(y=1; y < maxy-1; y++)
                for(x=1; x < maxx-1; x++)
                        mvwaddch(window, y, x, ' ');
}

void wprintTitleCentered(WINDOW *window, const char *titleText) 	//print the title of the window
{
        int x, maxy, maxx;
        getmaxyx(window,maxy,maxx);
        x = (maxx - 4 - strlen(titleText))/2;
        mvwprintw(window,0,x,"| %s |",titleText);
}

void drawWindow(WINDOW *window,int color_pair,char *titleText) 	//initial drawing of the empty window
{
        wattrset(window, COLOR_PAIR(color_pair) | WA_BOLD);
        wclrscr(window);
        box(window, 0, 0);
        wprintTitleCentered(window, titleText);
        touchwin(window);
        wrefresh(window);
}

int dircmp(const void *f1, const void *f2)
{
	return strcmp(*(int *)f1, *(int *)f2);
}

int listDir(char *directory, struct filelist *dir_list[]) 	//the array of files in folder
{
        DIR *dp;
        struct dirent *ep;
	int i;
	
	for (i=0; i<MAX_LIST; i++)
			dir_list[i]=NULL;
	
        i=-3; 		//it's not good...

        dp = opendir (directory);
        if (dp != NULL) {
                while (ep=readdir(dp)) {
			if (i==MAX_LIST-1) 
				break;
                        i++;
                        if (i>=0) {
				dir_list[i]=malloc(sizeof(struct filelist));
                                strcpy(dir_list[i]->f_name, ep->d_name);
				//
				char tmp[MAX_FILE_NAME];
				strcpy(tmp,directory);
				strcat(tmp,ep->d_name);
				struct stat *buf;
				buf = malloc(sizeof(struct stat));
				lstat(tmp, buf);
				dir_list[i]->f_type = 'x';
				if (S_ISLNK(buf->st_mode))
					dir_list[i]->f_type = 'l';
				if (S_ISDIR(buf->st_mode))
					dir_list[i]->f_type = 'd';
				if (S_ISREG(buf->st_mode))
					dir_list[i]->f_type = 'f';
				//
			}
                }
                closedir(dp);
        }
	if (i<0) 		//it's not good......
		return -1;
	qsort(dir_list, i+1, sizeof(struct filelist *), dircmp);
        return i; 
}
					 
//draw the list of files in the explorer window
void drawExplorer(WINDOW *window,
		struct filelist *dir_list[],
		int explorer_item,
		int max_explorer_item)
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
        wclrscr(window);

	if (explorer_item>maxy-3)
		tmp=explorer_item-maxy+3;
	else
		tmp=0;
	
        for (i=tmp; (i<=max_explorer_item)&&(i<tmp+maxy-2); i++) {
                if (i==explorer_item)
                        wattrset(window, COLOR_PAIR(EXPLORER_SEL_COLOR) | WA_BOLD);
                else
                        wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
		
                //if (dir_list[i]!="")
                        mvwprintw(window,i+1-tmp,1,"  %s  ",dir_list[i]->f_name);
                        mvwprintw(window,i+1-tmp,30,"%c",dir_list[i]->f_type);
                //else
                //        break;
        }
        touchwin(window);
        wrefresh(window);
}

char *upDir(char directory[]) 
{
	int i, len;
	if (!strcmp(directory, "/")) 
		return directory;
	
	len = strlen(directory);
	for (i=len-2; i>=0; i--)
		if (directory[i] == '/') {
			directory[i+1]='\0';
			break;
		}
	return directory;
}

void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item) 
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
        wclrscr(window);

	if (item>maxy-3)
		tmp=item-maxy+3;
	else
		tmp=0;
	
        for (i=tmp; (i<=max_item)&&(i<tmp+maxy-2); i++) {
                if (i==item)
                        wattrset(window, COLOR_PAIR(PLAYLIST_SEL_COLOR) | WA_BOLD);
                else
                        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
		
                mvwprintw(window,i+1-tmp,1,"  %s  ",play_list[i]->f_name);
                mvwprintw(window,i+1-tmp,30,"%s",play_list[i]->path);
        }
        touchwin(window);
        wrefresh(window);
}	

addtoPlaylist(struct playlist play_list,
		struct dirlist dir_list,
		char current_dir[],
		int explorer_item,
		int max_playlist_item)
{
	char tmp[MAX_FILE_NAME];
	max_playlist_item++;
	play_list[max_playlist_item]=malloc(sizeof(struct playlist));
	strcpy(play_list[max_playlist_item]->f_name, dir_list[explorer_item]->f_name);
	strcpy(tmp,current_dir);
	strcat(tmp,dir_list[explorer_item]->f_name);
	strcpy(play_list[max_playlist_item]->path, tmp);
}
