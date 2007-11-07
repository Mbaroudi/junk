#include "zmp.h"
#include "interface.h"

void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item) 
/*! \brief Draws a playlist window and songs within it
 */
{
        int i, tmp, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
        wclrscr(window);

	tmp = item>maxy-15 ? item-maxy+15 : 0;
	
        for (i=tmp; (i<=max_item)&&(i<tmp+maxy-2); i++) {
                if (i==item)
                        wattrset(window, COLOR_PAIR(PLAYLIST_SEL_COLOR) | WA_BOLD);
                else
                        wattrset(window, COLOR_PAIR(PLAYLIST_COLOR) | WA_BOLD);
		if (play_list[i]->is_playing)
			wattrset(window, COLOR_PAIR(PLAYLIST_PLAYING_COLOR) | WA_BOLD);

		if (play_list[i]->is_selected)
                	mvwprintw(window,i+1-tmp,1," <%s> ",play_list[i]->title);
		else
                	mvwprintw(window,i+1-tmp,1,"  %s  ",play_list[i]->title);
                mvwprintw(window,i+1-tmp,maxx/3," | %s",play_list[i]->artist); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,maxx/2," | %s",play_list[i]->album); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,maxx-35," | %s",play_list[i]->genre); //it's only for debug....maybe
                mvwprintw(window,i+1-tmp,maxx-10," | %s",play_list[i]->year); //it's only for debug....maybe
        }
        redrawWindow(window);
}//drawPlaylist

int delfromPlaylist(struct playlist *play_list[], 
		int del_item, 
		int *max_playlist_item,
		int playlist_item)
/*! \brief Removes selected item from playlist
 */
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
/*! \brief Displays song information
 */
{
	int maxy, maxx, i, width;
	getmaxyx(window, maxy, maxx);
	width = maxx - 5;
	wattrset(window, COLOR_PAIR(SONG_INFO_COLOR) | WA_BOLD);
	wclrscr(window);

	if (playlist_play) {
		i=3;
		wattrset(window, COLOR_PAIR(SONG_INFO_SEL_COLOR) | WA_BOLD);
		mvwprintw(window, i, 2, "NOW PLAYING:");
		i++;
		wattrset(window, COLOR_PAIR(SONG_INFO_PLAYING_COLOR) | WA_BOLD);
		if (playlist_play->title!="") {
			mvwprintw(window, i, 2, "Title:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_play->title);
			i++;
		}
		if (playlist_play->artist!="") {
			mvwprintw(window, i, 2, "Artist:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_play->artist);
			i++;
		}
		if (playlist_play->genre!="") {
			mvwprintw(window, i, 2, "Genre:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_play->genre);
			i++;
		}
		if (playlist_play->album!="") {
			mvwprintw(window, i, 2, "Album:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_play->album);
			i++;
		}
		if (playlist_play->year!="") {
			mvwprintw(window, i, 2, "Year: %.*s", width, playlist_play->year);
			i++;
		}
	}
	
	if (playlist_sel) {
		i=maxy/2;
		mvwprintw(window, i, 2, "SELECTED:");
		i++;
		wattrset(window, COLOR_PAIR(SONG_INFO_SEL_COLOR) | WA_BOLD);
		if (playlist_sel->title!="") {
			mvwprintw(window, i, 2, "Title:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_sel->title);
			i++;
		}
		if (playlist_sel->artist!="") {
			mvwprintw(window, i, 2, "Artist:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_sel->artist);
			i++;
		}
		if (playlist_sel->genre!="") {
			mvwprintw(window, i, 2, "Genre:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_sel->genre);
			i++;
		}
		if (playlist_sel->album!="") {
			mvwprintw(window, i, 2, "Album:");
			i++;
			mvwprintw(window, i, 2, " %.*s", width, playlist_sel->album);
			i++;
		}
		if (playlist_sel->year!="") {
			mvwprintw(window, i, 2, "Year: %s", playlist_sel->year);
			i++;
		}
	}
	
        redrawWindow(window);
}
