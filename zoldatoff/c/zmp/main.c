#include <string.h>

#include "zmp.h"
#include "explorer.h"
#include "playlist.h"
#include "interface.h"

#include <SDL/SDL.h>
#include "SDL/SDL_mixer.h"

int incItem(int item, int max_item);
int decItem(int item, int max_item);
void musicFinished();
int musicPlaying = 1;
//==============================================================
int main(int argc, char *argv[])
{
        initscr();
        noecho(); 	//no output to terminal
        raw(); 		//no buffering
	curs_set(0);    //no cursor
        keypad(stdscr,TRUE);
        redrawWindow(stdscr);
	
	//Colors initialization
        start_color();
        init_pair(BASEWIN_COLOR, COLOR_BLUE, COLOR_BLACK);
        init_pair(PLAYLIST_COLOR, COLOR_RED, COLOR_BLACK);
        init_pair(PLAYLIST_SEL_COLOR, COLOR_RED, COLOR_BLUE);
        init_pair(PLAYLIST_PLAYING_COLOR, COLOR_YELLOW, COLOR_BLACK);
        init_pair(SONG_INFO_COLOR, COLOR_YELLOW, COLOR_BLACK);
        init_pair(SONG_INFO_PLAYING_COLOR, COLOR_GREEN, COLOR_BLACK);
        init_pair(SONG_INFO_SEL_COLOR, COLOR_WHITE, COLOR_BLACK);
        init_pair(EXPLORER_COLOR, COLOR_GREEN, COLOR_BLACK);
        init_pair(EXPLORER_SEL_COLOR, COLOR_GREEN, COLOR_BLUE);
        init_pair(EXPLORER_DIR_COLOR, COLOR_WHITE, COLOR_BLACK);
        init_pair(EXPLORER_DIR_SEL_COLOR, COLOR_WHITE, COLOR_BLUE);
        init_pair(EXPLORER_MEDIA_COLOR, COLOR_RED, COLOR_BLACK);
        init_pair(EXPLORER_MEDIA_SEL_COLOR, COLOR_RED, COLOR_BLUE);

        int maxy, maxx;
        WINDOW *base_win, *playlist_win, *song_info_win, *explorer_win, *status_win;
	
	// Draw windows
        getmaxyx(stdscr,maxy,maxx);
        base_win = newwin(maxy, maxx, 0, 0);
        drawWindow(base_win, BASEWIN_COLOR, "Zoldatoff Media Player");
        explorer_win = newwin(maxy-5, maxx-2, 1, 1);
        drawWindow(explorer_win, EXPLORER_COLOR, "Explorer");
        playlist_win = newwin(maxy-5, (3*maxx)/4, 1, maxx/4);
        drawWindow(playlist_win, PLAYLIST_COLOR, "Playlist");
        song_info_win = newwin(maxy-5, maxx/4 - 1, 1, 1);
        drawWindow(song_info_win, SONG_INFO_COLOR, "Song");
        status_win = newwin(3, maxx-2, maxy-4, 1);
        keypad(playlist_win,TRUE);
        keypad(song_info_win,TRUE);
        keypad(base_win,TRUE);
	
	wtimeout(playlist_win,10);
	
	//Arrays of directory listing and playlist
        struct playlist *play_list[MAX_LIST];
	struct filelist *dir_list[MAX_LIST];
		
	int k;
	for (k=0; k<MAX_LIST; k++)
		dir_list[k] = NULL;
	
        char current_dir[MAX_FILE_NAME]="/home/media/music/";
	char vol_str[SDL_MIX_MAXVOLUME+1];
	vol_str[SDL_MIX_MAXVOLUME]='\0';
        int playlist_item=0, max_playlist_item=-1, playing_item=0;
        int explorer_item=0, max_explorer_item=0, show_explorer=0;
	int playlist_sel = 0, explorer_sel = 0; 		//first item is selected in explorer & playlist 

        max_explorer_item = listDir(current_dir, dir_list);

	//Audio init
	Mix_Music *music;
        int audio_rate = 44100;
        Uint16 audio_format = AUDIO_S16SYS;
        int audio_channels = 2;
        int audio_buffers = 4096;
	int volume = SDL_MIX_MAXVOLUME;
	SDL_Init(SDL_INIT_AUDIO);
	Mix_OpenAudio(audio_rate, audio_format, audio_channels, audio_buffers);
	//End audio init
	
	int key;
        while (1) {
		if (!musicPlaying) {
			play_list[playing_item]->is_playing = 0;
			playing_item++;
			if (playing_item>max_playlist_item)
				playing_item = max_playlist_item;
			else {
				if (Mix_PlayingMusic())
					Mix_HaltMusic();
				music = Mix_LoadMUS(play_list[playing_item]->path);
				if (music!=NULL) {
					musicPlaying = 1;
					Mix_PlayMusic(music, 1);
					Mix_HookMusicFinished(musicFinished);
					play_list[playing_item]->is_playing = 1;
					message(status_win, "...playing next song...");
				}
				else
					message(status_win,"Cannot load music");
				if (!show_explorer) {
					drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
					drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				}
			}	
		}
			
                key = wgetch(playlist_win);
		if (key==ERR)
			continue;
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
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...down...");
			break;
		case KEY_UP: 		//DONE: scroll list up
                        if (show_explorer) {
                                explorer_item = decItem(explorer_item, max_explorer_item);
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        else {
                                playlist_item = decItem(playlist_item, max_playlist_item);
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...up...");
			break;
		case HOME: 		//DONE: scroll list up
                        if (show_explorer) {
                                explorer_item = 0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        else {
                                playlist_item = 0;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...up...");
			break;
		case END: 		//DONE: scroll list up
                        if (show_explorer) {
                                explorer_item = max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
                        else {
                                playlist_item = max_playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...up...");
			break;
                 case PG_DOWN:
			if (show_explorer) {
				explorer_item = (explorer_item<max_explorer_item-(maxy/2)) ? explorer_item+(maxy/2) : max_explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				playlist_item = (playlist_item<max_playlist_item-(maxy/2)) ? playlist_item+(maxy/2) : max_playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...page down...");
			break;
		case PG_UP:
			if (show_explorer) {
				explorer_item -= (explorer_item>(maxy/2)) ? (maxy/2) : explorer_item;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				playlist_item -= (playlist_item>(maxy/2)) ? (maxy/2) : playlist_item;
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...page up...");
			break;
		case TAB: 		//DONE: switch between playlist & explorer
                        if (!show_explorer) {
                                drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
                                show_explorer=1;
				message(status_win,"...explorer...");
                        } 
			else {
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
                                show_explorer=0;
				message(status_win,"...playlist...");
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
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
                        break;
                case KEY_RIGHT:
			if (!show_explorer && Mix_PlayingMusic()) {
				Mix_SetMusicPosition(+5);
				drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
                        	drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
			}
			message(status_win, "...scrolling song...");
			break;
		case ENTER: 		//add to playlist & play selected song //DONE: open folder
			if (show_explorer && dir_list[explorer_item]) {
				strcat(current_dir, dir_list[explorer_item]->f_name);
				strcat(current_dir, "/");
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item = explorer_sel = 0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else {
				play_list[playing_item]->is_playing = 0;
				playing_item = playlist_item;
				play_list[playing_item]->is_playing = 1;
				//message(status_win,play_list[playing_item]->path);
				if (Mix_PlayingMusic()) 
					Mix_HaltMusic();
				music = Mix_LoadMUS(play_list[playing_item]->path);
				if (music!=NULL) {
					musicPlaying = 1;
					Mix_PlayMusic(music, 1); 
					Mix_HookMusicFinished(musicFinished);
					drawPlaylist(playlist_win,play_list,playlist_item,max_playlist_item);
					drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
					message(status_win, "...playing selected song...");
				}
				else
					message(status_win,"Cannot load music");
			}
                        break;
		case 'p':
			if (Mix_PausedMusic())
				Mix_ResumeMusic();
			else
				Mix_PauseMusic();
			message(status_win, "...pause/unpause...");
			break;
		case KEY_LEFT: 		//DONE: go up one dir
			if (show_explorer) {
				strcpy(current_dir, upDir(current_dir));
        			max_explorer_item = listDir(current_dir, dir_list);
				explorer_item = explorer_sel = 0;
				drawExplorer(explorer_win,dir_list,explorer_item,max_explorer_item);
			}
			else if (Mix_PlayingMusic()) 
				Mix_SetMusicPosition(-5);
			break;
		case 'a': 		//add files to playlist
			if (show_explorer && dir_list[explorer_item]) {
				message(status_win,"...adding files & folders...");
				if (explorer_sel) {
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
				message(status_win,"...files & folders are added...");
			}
			break;
		case 'd': 		//delete items from playlist
			if (!show_explorer && play_list[playlist_item]) {
				if (playlist_sel) {
					for (k=0; k<=max_playlist_item;) {
						if (play_list[k]->is_selected) {
							playlist_item = delfromPlaylist(play_list, k, &max_playlist_item, playlist_item);	
							if (playing_item>=k)
								playing_item--;
						}
						else 
							k++;
					}
				}
				else {
					playlist_item = delfromPlaylist(play_list, playlist_item, &max_playlist_item,playlist_item);
					if (playing_item>=playlist_item)
						playing_item--;
				}
			
				drawPlaylist(playlist_win, play_list, playlist_item, max_playlist_item);
				drawSong(song_info_win, play_list[playing_item], play_list[playlist_item]);
				playlist_sel = 0;
			}
			break;
		case '+': 		//volume up
		case '=': 		//volume up
			volume = volume<(SDL_MIX_MAXVOLUME-5) ? (volume + 5) : SDL_MIX_MAXVOLUME;
		        Mix_VolumeMusic(volume);
			for (k=0; k<volume; k++) vol_str[k]='|';
			for (; k<SDL_MIX_MAXVOLUME; k++) vol_str[k]=':';
			message(status_win, vol_str);
			break;
		case '-': 		//volume down
			volume = volume>5 ? (volume-5) : 0;
		        Mix_VolumeMusic(volume);	
			for (k=0; k<volume; k++) vol_str[k]='|';
			for (; k<SDL_MIX_MAXVOLUME; k++) vol_str[k]=':';
			message(status_win, vol_str);
			break; 		
                case ESC: 		//do you want to exit?
                        //mvwprintw(song_info_win,i,1,"ESC");
                        //wrefresh(song_info_win);
                        //i++;
                        break;
                case KEY_F(1): 		//help & something else .............
                        //mvwprintw(song_info_win,i,1,"F1");
                        //wrefresh(song_info_win);
                        //i++;
                        break;
                case 'w': 		//write configuration (what configuration?)
                        //mvwprintw(song_info_win,i,1,"w");
                        //wrefresh(song_info_win);
                        //i++;
			break;
                default: 		//what is this doing here?!
                        mvwprintw(song_info_win,10,1,"%x",key);
                        wrefresh(song_info_win);
                        break;
                }
        }

	//Stop audio engine
	Mix_FreeMusic(music);
	Mix_CloseAudio();
	SDL_Quit();
			
	
        delwin(base_win); 	//kill all windows
        delwin(playlist_win); 	//kill all windows
        delwin(song_info_win); 	//kill all windows
        endwin(); 		//end curses environment
        return 0;
}

int incItem(int item, int max_item)
{
        return item<max_item ? ++item : 0;
}

//================================================================================

int decItem(int item, int max_item)
{
        return item>0 ? --item : max_item;
}
        
void musicFinished()
{
	musicPlaying = 0;
}

