#include <id3tag.h>

#include "zmp.h"

void readTag(struct playlist *play_list)
{
	struct id3_file *file;
	struct id3_tag *tag;
	file = id3_file_open(play_list->path, ID3_FILE_MODE_READONLY);
	tag = id3_file_tag (file);

	/*struct {
		int index;
		char const *id;
		char const *name;
	} const info[] = {
	{ 0,    ID3_FRAME_TITLE,  "Title  : "   },
	{ 1,    ID3_FRAME_ARTIST, "  Artist: "  },
	{ 2,    ID3_FRAME_ALBUM,  "Album  : "   },
	{ 3,    ID3_FRAME_YEAR,   "  Year  : "  },
	{ 4,    ID3_FRAME_COMMENT,"Comment: "   },
	{ 5,    ID3_FRAME_GENRE,  "  Genre : "  }
	};*/

	char *name;
	name=id3_get_tag(tag, "Artist", 30);
	strcpy(play_list->artist, name);
	name=id3_get_tag(tag, "Year", 4);
	strcpy(play_list->year, name);
}
