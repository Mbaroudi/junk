#include <id3tag.h>
#include <string.h>
#include <stdlib.h>

#include "zmp.h"

char *id3_get_tag (struct id3_tag const *tag, char const *what, unsigned int maxlen)
{
        struct id3_frame const *frame = NULL;
        union id3_field const *field = NULL;
        int nstrings;
        int avail;
        int j;
        int tocopy;
        int len;
        char printable [1024];
        char *retval = NULL;
        id3_ucs4_t const *ucs4 = NULL;
        id3_latin1_t *latin1 = NULL;

        memset (printable, '\0', 1024);
        avail = 1024;
        if (strcmp (what, ID3_FRAME_COMMENT) == 0)
        {
                /*There may be sth wrong. I did not fully understand how to use
                *             libid3tag for retrieving comments  */
                j=0;
                frame = id3_tag_findframe(tag, ID3_FRAME_COMMENT, j++);
                if (!frame)
                        return (NULL);
                ucs4 = id3_field_getfullstring (&frame->fields[3]);
                if (!ucs4)
                        return (NULL);
                latin1 = id3_ucs4_latin1duplicate (ucs4);
                if (!latin1 || strlen(latin1) == 0)
                        return (NULL);
                len = strlen(latin1);
                if (avail > len)
                        tocopy = len;
                else
                        tocopy = 0;
                if (!tocopy)
                        return (NULL);
                avail-=tocopy;
                strncat (printable, latin1, tocopy);
                free (latin1);
        } else
        {
                frame = id3_tag_findframe (tag, what, 0);
                if (!frame)
                        return (NULL);
                field = &frame->fields[1];
                nstrings = id3_field_getnstrings(field);
                for (j=0; j<nstrings; ++j) {
                        ucs4 = id3_field_getstrings(field, j);
                        if (!ucs4)
                                return (NULL);
                        if (strcmp (what, ID3_FRAME_GENRE) == 0)
                                ucs4 = id3_genre_name(ucs4);
                        latin1 = id3_ucs4_latin1duplicate(ucs4);
                        if (!latin1)
                                break;
                        len = strlen(latin1);
                        if (avail > len)
                                tocopy = len;
                        else
                                tocopy = 0;
                        if (!tocopy)
                                break;
                        avail-=tocopy;
                        strncat (printable, latin1, tocopy);
                        free (latin1);
                }
        }
        retval = malloc (maxlen + 1);
        if (!retval)
                return (NULL);

        strncpy (retval, printable, maxlen);
        retval[maxlen] = '\0';

        len = strlen(printable);
        if (maxlen > len)
        {
                memset (retval + len, ' ', maxlen - len);
        }

        return (retval);
}




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
