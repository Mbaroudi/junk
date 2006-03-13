#include <ncursesw/ncurses.h>
#include <string.h>


void redrawWindow(WINDOW* window)
{
	touchwin(window);
	wrefresh(window);
}

//Clear the window (box remains)
void wclrscr(WINDOW *window) 		//clear the space inside the window
{
        int y, x, maxy, maxx;
        getmaxyx(window, maxy, maxx);
        for(y=1; y < maxy-1; y++)
                for(x=1; x < maxx-1; x++)
                        mvwaddch(window, y, x, ' ');
}//wclrscr


//Print centered title
void wprintTitleCentered(WINDOW *window, char *titleText) 	//print the title of the window
{
        int x, maxy, maxx;
        getmaxyx(window,maxy,maxx);
        x = (maxx - 4 - strlen(titleText))/2;
        mvwprintw(window,0,x,"| %s |",titleText);
}//wprintTitleCentered


//Initial drawing of window with box & title
void drawWindow(WINDOW *window,int color_pair,char *titleText) 	//initial drawing of the empty window
{
        wattrset(window, COLOR_PAIR(color_pair) | WA_BOLD);
        wclrscr(window);
        box(window, 0, 0);
        wprintTitleCentered(window, titleText);
        redrawWindow(window);
}//drawWindow

void message(WINDOW *window, char *mess)
{
	int maxy, maxx, x;
	getmaxyx(window, maxy, maxx);
	//mvwprintw(window, 2, 2, "                                                                                                                                            ");
	for(x=1; x < maxx-1; x++) mvwaddch(window, 1, x, ' ');
	mvwprintw(window, 1, 1, "%s", mess);
	redrawWindow(window);
}

