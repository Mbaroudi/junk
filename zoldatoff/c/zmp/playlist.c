#include "zmp.h"
#include "interface.h"

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

//Delete item from playlist
int delfromPlaylist(struct playlist *play_list[], 
		int del_item, 
		int *max_playlist_item,
		int playlist_item)
{
	int i, item;
	for (i=del_item; i<(*max_playlist_item); i++)
		play_list[i]=play_list[i+1];

	play_list[*max_playlist_item]=NULL;
	(*max_playlist_item)--;
	
	item = del_item<playlist_item ? playlist_item-1 : playlist_item;
	if (item<0) item = 0;
	if (item>*max_playlist_item) item = *max_playlist_item;
	return item;
}
