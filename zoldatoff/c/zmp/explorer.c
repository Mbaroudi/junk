#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <ctype.h>
#include <string.h>

#include "zmp.h"
#include "interface.h"
#include "idtag.h"


int dircmp(const void *f1, const void *f2)
/*! \brief Sorting directories in ascending order
 *
 * This function compares two arguments in an array, 
 * so that this array can be sorted
 */
{
	return strcmp(*(int *)f1, *(int *)f2);
}


int listDir(const char *directory, struct filelist *dir_list[]) 	//the array of files in folder
/*! \brief Listing directory
 *
 * This functon lists all files & dirs the directory contains.
 *
 * \param directory a char string that represents the path to the directory listed
 * \param dir_list[] an array of pointers to all of the objects of directory
 */
{
        DIR *dp;
        struct dirent *ep;
	struct filelist *dirs[MAX_LIST];
	struct filelist *files[MAX_LIST];
	int i, i_dirs, i_files;
	
	for (i=0; i<MAX_LIST; i++)
		if (dir_list[i]!=NULL)
			dir_list[i]=NULL;
	
        i_dirs=i_files=-1;

        dp = opendir (directory);
        if (dp != NULL) {
                while (ep=readdir(dp)) {
			if (i_files+i_dirs==MAX_LIST-2) 
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
			free(buf);
			
			if (tmp[1]!='d') { 		//a VERY bad if....i think
				char string[4];
				for (i=0; i<4; i++) string[i] = tolower(ep->d_name[strlen(ep->d_name)-4+i]);
				string[4]='\0';
				if (!strcmp(string, ".mp3") || !strcmp(string, ".ogg"))
					tmp[1] = 'm';
			}
			
			if (tmp[1]=='d') {
				i_dirs++;
				dirs[i_dirs]=malloc(sizeof(struct filelist));
				strcpy(dirs[i_dirs]->f_name,ep->d_name);
				dirs[i_dirs]->f_type = tmp[1];
				dirs[i_dirs]->is_selected = 0;
			}
			else if (tmp[1]!='x' && tmp[1]!='l') {
				i_files++;
				files[i_files]=malloc(sizeof(struct filelist));
				strcpy(files[i_files]->f_name, ep->d_name);
				files[i_files]->f_type = tmp[1];
				files[i_files]->is_selected = 0;
			}
                }
                closedir(dp);
        }
	//if (i_dirs+i_files<0)
	//	return 0;
//	qsort(dir_list, i+1, sizeof(struct filelist *), dircmp);
	qsort(dirs, i_dirs+1, sizeof(struct filelist *), dircmp);
	qsort(files, i_files+1, sizeof(struct filelist *), dircmp);
	
	for (i=0; i<=i_dirs; i++)
		dir_list[i] = dirs[i];
	for (i=0; i<=i_files; i++)
		dir_list[i+i_dirs+1] = files[i];
	//if (i_files<0) i_files=0;
	//if (i_dirs<0) i_dirs=0;
        return i_dirs+i_files+1; 
}//listDir

//================================================================================					 

void drawExplorer(WINDOW *window,
		struct filelist *dir_list[],
		int item,
		int max_item)
/*! \brief Draw the list of files in explorer window
 *
 * \param window pointer to explorer window
 * \param dir_list array of pointers to all directory objects
 * \param item number of selected item in dir_list array
 * \param max_item the last item in dir_list array
 */
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(EXPLORER_COLOR) | WA_BOLD);
        wclrscr(window);

	tmp = item>maxy-15 ? item-maxy+15 : 0;
	
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
        //        mvwprintw(window,i+1-tmp,60,"  %c  ",dir_list[i]->f_type);   //for debug only!!
        //        mvwprintw(window,i+1-tmp,70,"  %d  ",dir_list[i]->is_selected);   //for debug only!!
        }
        redrawWindow(window);
}//drawExplorer

//================================================================================

char *upDir(char directory[]) 
/*! \brief Go to up level directory
 *
 * \param directory source directory
 * \return path to the up level directory
 */
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

void addFile(struct playlist *play_list[],
		struct filelist *dir_list[],
		char current_dir[],
		int playlist_item,
		int explorer_item)
/*! \brief add file to playlist
 *
 * Adds the file selected in explorer window to playlist
 * \param play_list array of pointers to playlist items
 * \param dir_list list of directory items
 * \param current_dir nothing to say
 * \param playlist_item selected playlist item
 * \param explorer_item selected item in explorer list
 */
{
	char tmp[MAX_FILE_NAME];
	if (playlist_item<MAX_LIST) {
		play_list[playlist_item]=malloc(sizeof(struct playlist));
		strcpy(play_list[playlist_item]->f_name, dir_list[explorer_item]->f_name);
		strcpy(tmp,current_dir);
		strcat(tmp,dir_list[explorer_item]->f_name);
		strcpy(play_list[playlist_item]->path, tmp);
		readTag(play_list[playlist_item]);
		play_list[playlist_item]->is_selected=0;
		play_list[playlist_item]->is_playing=0;
	}
}//addFile


//================================================================================					 

//Add folder to playlist
void addFolder(char dir[], 
		struct playlist *play_list[], 
		int *max_item)
/*! \brief Adds all files in folder and subfolders to playlist recurcevely
 *
 * \param dir path to the directory to add
 * \param play_list array of pointers to playlist items
 * \param max_item the number of the last playlist item
 */
{
	int num, i;
	struct filelist *list[MAX_LIST];
	num = listDir(dir, list);
	for (i=0; i<=num; i++) {
		if ( list[i]->f_type == 'm' ) {
			if ((*max_item)<MAX_LIST-1) 
				(*max_item)++;
			else
				break;
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

//================================================================================					 

void addtoPlaylist(struct filelist *dir_list[],
		struct playlist *play_list[],
		int explorer_item,
		char current_dir[],
		int *max_playlist_item)
/*! \brief Adds selected file of folder to playlist
 *
 * \param dir_list current directory structure
 * \param play_list current playlist structure
 * \param explorer_item selected item in explorer window
 * \param current_dir current directory :)
 * \param max_playlist_item the last playlist item
 */

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

