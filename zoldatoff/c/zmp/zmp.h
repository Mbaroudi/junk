#include <ncursesw/ncurses.h>

#define BASEWIN_COLOR 1
#define PLAYLIST_COLOR 2
#define PLAYLIST_SEL_COLOR 3
#define SONG_INFO_COLOR 4
#define SONG_INFO_PLAYING_COLOR 5
#define SONG_INFO_SEL_COLOR 6
#define EXPLORER_COLOR 7
#define EXPLORER_SEL_COLOR 8
#define EXPLORER_DIR_COLOR 9
#define EXPLORER_DIR_SEL_COLOR 10
#define EXPLORER_MEDIA_COLOR 11
#define EXPLORER_MEDIA_SEL_COLOR 12

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
	char title[31];
	char artist[31];
	char genre[31];
	char album[31];
	char year[5];
	int  is_selected;
};

