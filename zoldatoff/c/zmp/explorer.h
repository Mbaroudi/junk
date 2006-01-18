int listDir(const char *directory, struct filelist *dir_list[]);

void drawExplorer(WINDOW *window, 
		struct filelist *dir_list[], 
		int item, 
		int max_item);

void addFile(struct playlist *play_list,
		struct filelist *dir_list,
		char current_dir[],
		int playlist_item,
		int explorer_item);

void addFolder(char dir[], 
		struct playlist *play_list[], 
		int *max_item);

void addtoPlaylist(struct filelist *dir_list[],
		struct playlist *play_list[],
		int explorer_item,
		char current_dir[],
		int *max_playlist_item);

char *upDir(char directory[]);

void message(WINDOW *window, char *mess);
