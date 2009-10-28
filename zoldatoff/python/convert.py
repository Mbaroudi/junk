#!/usr/bin/env python3

from optparse import OptionParser
import subprocess, os, re

VERSION = "0.2 beta"
PROGRAM = "/usr/local/bin/HandBrakeCLI"
PROFILE = "iPhone & iPod Touch"
N_THREADS = 2

STYLE = {
    "default"    :     "\033[m",
    # styles
    "bold"       :     "\033[1m",
    "underline"  :     "\033[4m",
    "blink"      :     "\033[5m",
    "reverse"    :     "\033[7m",
    "concealed"  :     "\033[8m",
    # font colors
    "black"      :     "\033[30m", 
    "red"        :     "\033[31m",
    "green"      :     "\033[32m",
    "yellow"     :     "\033[33m",
    "blue"       :     "\033[34m",
    "magenta"    :     "\033[35m",
    "cyan"       :     "\033[36m",
    "white"      :     "\033[37m",
    # background colors
    "on_black"   :     "\033[40m", 
    "on_red"     :     "\033[41m",
    "on_green"   :     "\033[42m",
    "on_yellow"  :     "\033[43m",
    "on_blue"    :     "\033[44m",
    "on_magenta" :     "\033[45m",
    "on_cyan"    :     "\033[46m",
    "on_white"   :     "\033[47m" 
}

def cprint(text, color="white"):
    try:
        print(STYLE[color] + text + STYLE["white"])
    except KeyError:
        print(STYLE["white"] + text)

def main():
    # Program options definition
    usage = "Usage: %prog [path]"
    parser = OptionParser(usage=usage, version=VERSION)
    parser.add_option("-l", "--leave",
                      action="store_true",
                      default=False,
                      help="leave Makefile after process completion [default: off]")
    parser.add_option("-t", "--threads",
                      type="int",
                      default=2,
                      help="number of threads [default: 2]")
    parser.add_option("-r", "--remove",
                      action="store_true",
                      default=False,
                      help="remove source files after conversion [default: off]")
    opts, args = parser.parse_args()
    if args == []: args = "."
    os.chdir(args[0])
    
    # Go & see the list of files. Construct Makefile.
    line = "all:"
    i = 0
    filelist = []
    
    cprint("\n======================================================="
           "\nBuilding file list...", "magenta")
    for file in os.listdir(args[0]):
        name, extension = ( x for x in os.path.splitext(file) )    
        # TODO: MIME
        if (extension != '.py') & (name != 'Makefile') & (not file.startswith(".")): 
            i += 1
            newname = re.sub('\W+', '_', name)
            for file in filelist:
                if newname + '.avi' == file[1]:
                    newname += str(i)
            try:       
                os.rename(name + extension, newname + '.avi')
                filelist.append( (name + extension, newname + '.avi') )
                line += " " + newname + ".m4v"
                message = "{0:>2n}. {1:<.50}  --> {2:<}".format(i, name + extension, newname + '.avi')
                cprint(message, "cyan")
            except OSError:
                cprint("Failed to add file " + name + extension, "red")
    
    if filelist == []:
        cprint("Nothing to convert, exiting", "red")
        return 0
    line += "\n\n%.m4v: %.avi\n\t" 
    line += PROGRAM + " -Z '" + PROFILE 
    line += "' -i $< -o $@\n"
    
    # Write Makefile
    #cprint("\nWriting Makefile...", "magenta")
    fh = None
    try:
        fh = open("Makefile", "w")
        fh.write(line)
    except EnvironmentError:
        cprint("Error writing Makefile, exiting", "red")
        return 0
    finally:
        if fh: fh.close()
        
    # Run HandBrakeCLI
    cprint("\n======================================================="
           "\nConverting...", "magenta")
    try:
        print(STYLE["green"])
        n_threads = opts.threads if (opts.threads >= 1) & (opts.threads <= 10) else N_THREADS
        res = subprocess.Popen("make -j" + str(n_threads), shell=True)
        res.wait()
    except OSError:
        cprint("Execution failed", "red")
        
    # Renaming/removing source files
    cprint("\n======================================================="
           "\nCleaning up...", "magenta")
    try:
        if not opts.leave: 
            os.remove("Makefile")
        else:
            print("...Leaving Makefile")
    except OSError:
        cprint("Cannot remove Makefile", "red")
        
    if not opts.remove:
        for file in filelist:
            try:
                os.rename(file[1], file[0])
                cprint("...Renamed " + file[1] + " -> " + file[0], "cyan")
            except OSError:
                cprint("Cannot rename " + file[1] + " -> " + file[0], "red")
    else:
        for file in filelist:
            try:
                os.remove(file[1])
                cprint("...Removed " + file[1], "red")
            except OSError:
                cprint("Cannot remove " + file[1], "red")
                
    cprint("\nFinished!\n", "magenta")
    
main()