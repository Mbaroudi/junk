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
#define EXPLORER_DIR_COLOR 7
#define EXPLORER_DIR_SEL_COLOR 8
#define EXPLORER_MEDIA_COLOR 9
#define EXPLORER_MEDIA_SEL_COLOR 10

#define MAX_FILE_NAME 256
#define MAX_LIST 30000
#define MAX_TAG 128

#define ENTER '\n'           	//carriage return (enter key)
#define ESC 0x1b               	//Escape key
#define TAB 0x09               	//Tab key
#define SPACE ' '
#define PG_UP 0x153
#define PG_DOWN 0x152
//#define LF 0x0a               //Line feed
//#define BACKSPACE 0x08        //Backspace
//#define SAVE 0x13             //Ctrl-S for Save
//#define HELP 0x08             //Ctrl-H for Help
//#define QUIT 0x11             //Ctrl-Q for Quit

//================================================================================
struct filelist {
	char f_name[MAX_FILE_NAME];
	char f_type;
	int  is_selected;
};

struct playlist {
	char f_name[MAX_FILE_NAME];
	char path[MAX_FILE_NAME];
	char song[MAX_TAG];
	char artist[MAX_TAG];
	char genre[MAX_TAG];
	char album[MAX_TAG];
	int  is_selected;
};

//================================================================================
void wclrscr(WINDOW *window);

void drawWindow(WINDOW *window,int color_pair,char *titleText);

void redrawWindow(WINDOW* window);

int listDir(const char *directory, struct filelist *dir_list[]);

void drawExplorer(WINDOW *window, 
		struct filelist *dir_list[], 
		int item, 
		int max_item);

void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item); 		

void addFile(struct playlist *play_list[],
		struct filelist *dir_list[],
		char current_dir[],
		int explorer_item,
		int max_playlist_item);

void addFolder(char dir[], 
		struct playlist *play_list[], 
		int *max_item);

void addtoPlaylist(struct filelist *dir_list[],
		struct playlist *play_list[],
		int explorer_item,
		char current_dir[],
		int *max_playlist_item);

void delfromPlaylist(struct playlist *play_list[], 
		int playlist_item, 
		int *max_playlist_item);
					
char *upDir(char directory[]);

int incItem(int item, int max_item);
int decItem(int item, int max_item);
//==============================================================
int main(int argc, char *argv[])
{
        initscr();
        noecho(); 	//no output to terminal
        raw(); 		//no buffering
	curs_set(0);
        keypad(stdscr,TRUE);
        redrawWindow(stdscr);
	
	//Colors initialization
        start_color();
        init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
        init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
        init_pair(PLAYLIST_SEL_COLOR, COLOR_RED, COLOR_BLUE);
        init_pair(SONG_INFO_COLOR, COLOR_YELLOW, COLOR_BLACK);
        init_pair(EXPLORER_COLOR, COLOR_GREEN, COLOR_BLACK);
        init_pair(EXPLORER_SEL_COLOR, COLOR_GREEN, COLOR_BLUE);
        init_pair(EXPLORER_DIR_COLOR, COLOR_WHITE, COLOR_BLACK);
        init_pair(EXPLORER_DIR_SEL_COLOR, COLOR_WHITE, COLOR_BLUE);
        init_pair(EXPLORER_MEDIA_COLOR, COLOR_RED, COLOR_BLACK);
        init_pair(EXPLORER_MEDIA_SEL_COLOR, COLOR_RED, COLOR_BLUE);

        int maxy, maxx;
        WINDOW *base_win, *playlist_win, *song_info_win, *explorer_win;
	
	// Draw windows
        getmaxyx(stdscr,maxy,maxx);
        base_win = newwin(maxy, maxx, 0, 0);
        drawWindow(base_win, BASEWIN_COLOR, "Zoldatoff Media Player");
        explorer_win = newwin(maxy-2, maxx-2, 1, 1);
        drawWindow(explorer_win, EXPLORER_COLOR, "Explorer");
        playlist_win = newwin(maxy-2, (3*maxx)/4, 1, maxx/4);
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
	
        char current_dir[MAX_FILE_NAME]="/home/media/music/";
        int playlist_item=0, max_playlist_item=-1;
        int explorer_item=0, max_explorer_item=0, show_explorer=0;

        max_explorer_item = listDir(current_dir, dir_list);

        int key, i=2;  //i is unneeded!!
	int playlist_sel = 0, explorer_sel = 0; 		//there are no selected items in explorer & playlist 
	
        while (1) {
                key = wgetch(playlist_win);
                if (key=='q')
                        break;
                switch (key) {
		case KEY_DOWN: 		//DONE: scroll list down
                        if (show_explorer) {
                                explorer_item = incItem(explorer_item, max_explorer_item);
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        else {
                                playlist_item = incItem(playlist_item, max_playlist_item);
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
			}
			break;
		case KEY_UP: 		//DONE: scroll list up
                        if (show_explorer) {
                                explorer_item = decItem(explorer_item, max_explorer_item);
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        else {
                                playlist_item = decItem(playlist_item, max_playlist_item);
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
			}
			break;
                 case PG_DOWN:
			if (show_explorer) {
				explorer_item = (explorer_item<max_explorer_item-(maxy/2)) ? explorer_item+(maxy/2) : max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				playlist_item = (playlist_item<max_playlist_item-(maxy/2)) ? playlist_item+(maxy/2) : max_playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
			}
			break;
		case PG_UP:
			if (show_explorer) {
				explorer_item -= (explorer_item>(maxy/2)) ? (maxy/2) : explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				playlist_item -= (playlist_item>(maxy/2)) ? (maxy/2) : playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
			}
			break;
		case TAB: 		//DONE: switch between playlist & explorer
                        if (!show_explorer) {
                                drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
                                show_explorer=1;
                        } 
			else {
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
                                redrawWindow(song_info_win);
                                show_explorer=0;
                        }
                        break;
		case SPACE: 		//TODO: mark files and playlist items
			if (show_explorer) {
				if ( dir_list[explorer_item]->is_selected ) {
				       dir_list[explorer_item]->is_selected = 0;
				       explorer_sel--;
				}
				else {
				       dir_list[explorer_item]->is_selected = 1;
				       explorer_sel++;
				}
				explorer_item = explorer_item<max_explorer_item ? ++explorer_item : max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				if ( play_list[playlist_item]->is_selected ) {
				       play_list[playlist_item]->is_selected = 0;
				       playlist_sel--;
				}
				else {
				       play_list[playlist_item]->is_selected = 1;
				       playlist_sel++;
				}
				playlist_item = playlist_item<max_playlist_item ? ++playlist_item : max_playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
			}
                        break;
                case KEY_RIGHT: 	//as Enter....
		case ENTER: 		//add to playlist & play selected song //DONE: open folder
			if (show_explorer && dir_list[explorer_item]) {
				strcat(current_dir, dir_list[explorer_item]->f_name);
				strcat(current_dir, "/");
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item = explorer_sel = 0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        break;
		case KEY_LEFT: 		//DONE: go up one dir
			if (show_explorer) {
				strcpy(current_dir, upDir(current_dir));
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item = explorer_sel = 0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			break;
		case 'a': 		//add files to playlist
			if (show_explorer && dir_list[explorer_item]) {
				if (explorer_sel) {
					int k;
					for (k=0; k<=max_explorer_item; k++) {
						if (dir_list[k]->is_selected)
							addtoPlaylist(dir_list, play_list, k, current_dir, &max_playlist_item);	
						dir_list[k]->is_selected = 0;
					}
				}
				else
					addtoPlaylist(dir_list, play_list, explorer_item, current_dir, &max_playlist_item);	
					
				explorer_item = explorer_item<max_explorer_item ? ++explorer_item : max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
				explorer_sel = 0;
			}
			break;
		case 'd': 		//delete items from playlist
			if (!show_explorer && play_list[playlist_item]) {
				if (playlist_sel) {
					int k;
					for (k=0; k<=max_playlist_item; k++) {
						if (play_list[k]->is_selected)
							delfromPlaylist(play_list, k, &max_playlist_item);	
						play_list[k]->is_selected = 0;
					}
				}
				else
					delfromPlaylist(play_list, playlist_item, &max_playlist_item);
			
				//do something with playlist_item!!!	
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				playlist_sel = 0;
			}
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

//================================================================================

//Clear the window (box remains)
void wclrscr(WINDOW *window) 		//clear the space inside the window
{
        int y, x, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        for(y=1; y < maxy-1; y++)
                for(x=1; x < maxx-1; x++)
                        mvwaddch(window, y, x, ' ');
}//wclrscr

//================================================================================

//Print centered title
void wprintTitleCentered(WINDOW *window, const char *titleText) 	//print the title of the window
{
        int x, maxy, maxx;
        getmaxyx(window,maxy,maxx);
        x = (maxx - 4 - strlen(titleText))/2;
        mvwprintw(window,0,x,"| %s |",titleText);
}//wprintTitleCentered

//================================================================================

//Initial drawing of window with box & title
void drawWindow(WINDOW *window,int color_pair,char *titleText) 	//initial drawing of the empty window
{
        wattrset(window, COLOR_PAIR(color_pair) | WA_BOLD);
        wclrscr(window);
        box(window, 0, 0);
        wprintTitleCentered(window, titleText);
        redrawWindow(window);
}//drawWindow

//================================================================================

//For sorting directories in ascending order
int dircmp(const void *f1, const void *f2)
{
	return strcmp(*(int *)f1, *(int *)f2);
}//dircmp

//================================================================================

//List contents of directory
int listDir(const char *directory, struct filelist *dir_list[]) 	//the array of files in folder
{
        DIR *dp;
        struct dirent *ep;
	int i;
	
	for (i=0; i<MAX_LIST; i++)
		dir_list[i]=NULL;
	
        i=-1;

        dp = opendir (directory);
        if (dp != NULL) {
                while (ep=readdir(dp)) {
			if (i==MAX_LIST-1) 
				break;
			if ( (ep->d_name)[0]=='.' )
				continue;
                        
			char tmp[MAX_FILE_NAME]; 		//TODO: is's not good to use tmp in such a way...
			strcpy(tmp,directory);
			strcat(tmp,ep->d_name);
			struct stat *buf;
			buf = malloc(sizeof(struct stat));
			lstat(tmp, buf);
			
			tmp[1] = 'x';
			if (S_ISLNK(buf->st_mode))
				tmp[1] = 'l';
			if (S_ISDIR(buf->st_mode))
				tmp[1] = 'd';
			if (S_ISREG(buf->st_mode))
				tmp[1] = 'f';
			if (tmp[1]!='d') { 		//a VERY bad if....i think
				char *string;
				string=& (ep->d_name[strlen(ep->d_name)-4]);
				if ( (string[0]=='.') && (tolower(string[1])=='m') && (tolower(string[2])=='p') && (string[3]=='3') )
					tmp[1] = 'm';
			}

			if (tmp[1]!='x') {
				i++;
				dir_list[i]=malloc(sizeof(struct filelist));
				strcpy(dir_list[i]->f_name, ep->d_name);
				dir_list[i]->f_type = tmp[1];
			}
                }
                closedir(dp);
        }
	if (i<0)
		return -1;
	qsort(dir_list, i+1, sizeof(struct filelist *), dircmp);
        return i; 
}//listDir

//================================================================================					 
//Add folder to playlist
void addFolder(char dir[], 
		struct playlist *play_list[], 
		int *max_item)
{
	int num, i;
	struct filelist *list[MAX_LIST];
	num = listDir(dir, list);
	for (i=0; i<=num; i++) {
		if ( list[i]->f_type == 'm' ) {
			(*max_item)++;
			addFile(play_list, list, dir, i, *max_item);
		}

		if ( list[i]->f_type == 'd' ) {
			char tmp[MAX_FILE_NAME];
			strcpy(tmp,dir);
			strcat(tmp,list[i]->f_name);
			strcat(tmp,"/");
			addFolder(tmp, play_list, max_item);
		}
	}
}

//================================================================================					 

//draw the list of files in the explorer window
void drawExplorer(WINDOW *window,
		struct filelist *dir_list[],
		int item,
		int max_item)
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
        wclrscr(window);

	tmp = item>maxy-3 ? item-maxy+3 : 0;
	
        for (i=tmp; (i<=max_item)&&(i<tmp+maxy-2); i++) {
		switch (dir_list[i]->f_type) {
			case 'd':
				if (i==item) wattrset(window, COLOR_PAIR(EXPLORER_DIR_SEL_COLOR) | WA_BOLD);
				else wattrset(window, COLOR_PAIR(EXPLORER_DIR_COLOR) | WA_BOLD);
				if (dir_list[i]->is_selected) mvwprintw(window,i+1-tmp,1, " </%s> ",dir_list[i]->f_name);
				else mvwprintw(window,i+1-tmp,1, "  /%s  ",dir_list[i]->f_name);
				break;
			case 'f':
				if (i==item) wattrset(window, COLOR_PAIR(EXPLORER_SEL_COLOR) | WA_BOLD);
				else wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
                		if (dir_list[i]->is_selected) mvwprintw(window,i+1-tmp,1, " <%s> ",dir_list[i]->f_name);
				else mvwprintw(window,i+1-tmp,1, "  %s  ",dir_list[i]->f_name); 
				break;
			case 'm':
				if (i==item) wattrset(window, COLOR_PAIR(EXPLORER_MEDIA_SEL_COLOR) | WA_BOLD);
				else wattrset(window, COLOR_PAIR(EXPLORER_MEDIA_COLOR) | WA_BOLD);
                		if (dir_list[i]->is_selected) mvwprintw(window,i+1-tmp,1, " <%s> ",dir_list[i]->f_name);
				else mvwprintw(window,i+1-tmp,1, "  %s  ",dir_list[i]->f_name);
				break;
		}
                mvwprintw(window,i+1-tmp,60,"  %c  ",dir_list[i]->f_type);   //for debug only!!
                mvwprintw(window,i+1-tmp,70,"  %d  ",dir_list[i]->is_selected);   //for debug only!!
        }
        redrawWindow(window);
}//drawExplorer

//================================================================================

//Go one directory up
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
}//upDir

//================================================================================

//Draw playlist window
void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item) 
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
        wclrscr(window);

	tmp = item>maxy-3 ? item-maxy+3 : 0;
	
        for (i=tmp; (i<=max_item)&&(i<tmp+maxy-2); i++) {
                if (i==item)
                        wattrset(window, COLOR_PAIR(PLAYLIST_SEL_COLOR) | WA_BOLD);
                else
                        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
		
		if (play_list[i]->is_selected)
                	mvwprintw(window,i+1-tmp,1," <%s> ",play_list[i]->f_name);
		else
                	mvwprintw(window,i+1-tmp,1,"  %s  ",play_list[i]->f_name);
                //mvwprintw(window,i+1-tmp,30,"%s",play_list[i]->path); //it's only for debug....
        }
        redrawWindow(window);
}//drawPlaylist

//================================================================================

//Add file to playlist
void addFile(struct playlist *play_list[],
		struct filelist *dir_list[],
		char current_dir[],
		int explorer_item,
		int max_playlist_item)
{
	char tmp[MAX_FILE_NAME];
	play_list[max_playlist_item]=malloc(sizeof(struct playlist));
	strcpy(play_list[max_playlist_item]->f_name, dir_list[explorer_item]->f_name);
	strcpy(tmp,current_dir);
	strcat(tmp,dir_list[explorer_item]->f_name);
	strcpy(play_list[max_playlist_item]->path, tmp);
}//addFile

//================================================================================

int incItem(int item, int max_item)
{
	return item<max_item ? ++item : 0;
}

//================================================================================

int decItem(int item, int max_item)
{
	return item>0 ? --item : max_item;
}

//================================================================================

void redrawWindow(WINDOW* window)
{
	touchwin(window);
	wrefresh(window);
}

//================================================================================

//Add file or folder to playlist
void addtoPlaylist(struct filelist *dir_list[],
		struct playlist *play_list[],
		int explorer_item,
		char current_dir[],
		int *max_playlist_item)
{
	if (dir_list[explorer_item]->f_type == 'm') {
		(*max_playlist_item)++;
		addFile(play_list,dir_list,current_dir,explorer_item,*max_playlist_item);
	}
		
	if (dir_list[explorer_item]->f_type == 'd') {
		char tmp[MAX_FILE_NAME];
		strcpy(tmp,current_dir);
		strcat(tmp,dir_list[explorer_item]->f_name);
		strcat(tmp,"/");
		addFolder(tmp, play_list, max_playlist_item);
	}
}

//================================================================================

//Delete item from playlist
void delfromPlaylist(struct playlist *play_list[], 
		int playlist_item, 
		int *max_playlist_item)
{
}
