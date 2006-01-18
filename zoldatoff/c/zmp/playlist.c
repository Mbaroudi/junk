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
                	mvwprintw(window,i+1-tmp,1," <%s> ",play_list[i]->title);
		else
                	mvwprintw(window,i+1-tmp,1,"  %s  ",play_list[i]->title);
                mvwprintw(window,i+1-tmp,40,"| %s",play_list[i]->artist); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,60,"| %s",play_list[i]->album); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,80,"| %s",play_list[i]->genre); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,100,"| %s",play_list[i]->year); //it's only for debug....maybe
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

void drawSong (WINDOW *window,
		struct playlist *playlist_play,
		struct playlist *playlist_sel)
{
	int maxy, maxx, i;
	getmaxyx(window, maxy, maxx);
	wattrset(window, COLOR_PAIR(SONG_INFO_COLOR) | WA_BOLD);
	wclrscr(window);

	if (playlist_play) {
		i=3;
		wattrset(window, COLOR_PAIR(SONG_INFO_PLAYING_COLOR) | WA_BOLD);
		if (playlist_play->title!="") {
			mvwprintw(window, i, 2, "Title:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_play->title);
			i++;
		}
		if (playlist_play->artist!="") {
			mvwprintw(window, i, 2, "Artist:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_play->artist);
			i++;
		}
		if (playlist_play->genre!="") {
			mvwprintw(window, i, 2, "Genre:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_play->genre);
			i++;
		}
		if (playlist_play->album!="") {
			mvwprintw(window, i, 2, "Album:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_play->album);
			i++;
		}
		if (playlist_play->year!="") {
			mvwprintw(window, i, 2, "Year: %s", playlist_play->year);
			i++;
		}
	}
	
	if (playlist_sel) {
		i+=10;
		wattrset(window, COLOR_PAIR(SONG_INFO_SEL_COLOR) | WA_BOLD);
		if (playlist_sel->title!="") {
			mvwprintw(window, i, 2, "Title:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_sel->title);
			i++;
		}
		if (playlist_sel->artist!="") {
			mvwprintw(window, i, 2, "Artist:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_sel->artist);
			i++;
		}
		if (playlist_sel->genre!="") {
			mvwprintw(window, i, 2, "Genre:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_sel->genre);
			i++;
		}
		if (playlist_sel->album!="") {
			mvwprintw(window, i, 2, "Album:");
			i++;
			mvwprintw(window, i, 2, " %s", playlist_sel->album);
			i++;
		}
		if (playlist_sel->year!="") {
			mvwprintw(window, i, 2, "Year: %s", playlist_sel->year);
			i++;
		}
	}
	
        redrawWindow(window);
}
