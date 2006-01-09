void drawPlaylist(WINDOW *window, 
		struct playlist *play_list[], 
		int item, 
		int max_item); 		

int delfromPlaylist(struct playlist *play_list[], 
		int del_item, 
		int *max_playlist_item,
		int playlist_item);
					
