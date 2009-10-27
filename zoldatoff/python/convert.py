#!/usr/bin/python

from optparse import OptionParser
import subprocess, os, re

#TODO: remove Makefile, remove source files, prefix or folder for destination files, number of threads

VERSION = "0.1 alpha"
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
    opts, args = parser.parse_args()
    if args == []: args = "."
    
    # Go & see the list of files. Construct Makefile.
    os.chdir(args[0])
    line = "all:"
    i = 0
    cprint("\n======================================================="
           "\nBuilding file list...", "magenta")
    for file in os.listdir(args[0]):
        name, extension = ( x for x in os.path.splitext(file) )    
        # TODO: MIME
        if (extension != '.py') & (name != 'Makefile') & (not file.startswith(".")): 
            i += 1
            newname = re.sub('\W+', '_', name)  
            os.rename(name + extension, newname + '.avi')
            line += " " + newname + ".m4v"
            #message = "{0>.2n} {1<.50}  --> {2<}".format(i, name + extension, newname + '.avi')
            cprint(str(i) + ". " + name + extension + "\t-->\t" + newname + '.avi', "cyan")
    
    line += "\n\n%.m4v: %.avi\n\t" 
    line += PROGRAM + " -Z '" + PROFILE 
    line += "' -i $< -o $@\n"
    
    # Write Makefile
    #cprint("\nWriting Makefile...", "magenta")
    fh = None
    try:
        fh = os.open("Makefile", os.O_CREAT | os.O_WRONLY)
        os.write(fh, line)
    except EnvironmentError:
        cprint("Error writing to file", "red")
    finally:
        if fh: os.close(fh)
        
    # Run HandBrakeCLI
    cprint("\n======================================================="
           "\nConverting...", "magenta")
    try:
        print(STYLE["green"])
        res = subprocess.Popen("make -j" + str(N_THREADS), shell=True)
        res.wait()
        os.remove("Makefile")
        print(STYLE["white"])
    except OSError:
        cprint("Execution failed", "red")
        
    cprint("Finished!\n", "magenta")
    
main()