#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <ctype.h>
#include <string.h>
#include <wchar.h>

#include "zmp.h"
#include "interface.h"
#include "idtag.h"


//For sorting directories in ascending order
int dircmp(const void *f1, const void *f2)
{
	return strcmp(*(int *)f1, *(int *)f2);
}//dircmp

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

//Add file to playlist
void addFile(struct playlist *play_list[],
		struct filelist *dir_list[],
		char current_dir[],
		int playlist_item,
		int explorer_item)
{
	char tmp[MAX_FILE_NAME];
	play_list[playlist_item]=malloc(sizeof(struct playlist));
	strcpy(play_list[playlist_item]->f_name, dir_list[explorer_item]->f_name);
	strcpy(tmp,current_dir);
	strcat(tmp,dir_list[explorer_item]->f_name);
	strcpy(play_list[playlist_item]->path, tmp);
	readTag(play_list[playlist_item]);
	play_list[playlist_item]->is_selected=0;
}//addFile


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
			addFile(play_list, list, dir,*max_item,i);
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
//Add file or folder to playlist
//
//
void addtoPlaylist(struct filelist *dir_list[],
		struct playlist *play_list[],
		int explorer_item,
		char current_dir[],
		int *max_playlist_item)
{
	if (dir_list[explorer_item]->f_type == 'm') {
		(*max_playlist_item)++;
		addFile(play_list,dir_list,current_dir,*max_playlist_item,explorer_item);
	}
		
	if (dir_list[explorer_item]->f_type == 'd') {
		char tmp[MAX_FILE_NAME];
		strcpy(tmp,current_dir);
		strcat(tmp,dir_list[explorer_item]->f_name);
		strcat(tmp,"/");
		addFolder(tmp, play_list, max_playlist_item);
	}
}

