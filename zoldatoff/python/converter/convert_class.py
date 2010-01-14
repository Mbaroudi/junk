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
        
def printerror(text):
    cprint(text, "red")  
    
def printinfo(text):
    cprint(text, "cyan")       
    
def printmessage(text):
    cprint("\n=======================================================\n" + text, "magenta")    
    
def changecolor(color):
    print(STYLE[color])     

class file:
    namelist = set()
    append = 0
    
    def __init__(self, filename):
        self.name, self.extension = ( x for x in os.path.splitext(filename) )    
        if self.isvideo():
            self.nname = re.sub('\W+', '_', self.name)
            if self.nname in self.namelist:
                self.nname += str(self.append)
                self.append += 1
            self.namelist.add(self.nname)
            self.nextension = ".avi"
        else:
            self.nname, self.nextension = None, None
    
    #@staticmethod    
    def isvideo(self):
        if self.name == "Makefile": return False
        if self.name.startswith("."): return False
        if self.extension == ".py": return False
        if self.extension == "": return False
        return True
    
    def fullname(self):
        return self.name + self.extension
    
    def nfullname(self):
        if self.isvideo():
            return self.nname + self.nextension
        else: 
            return ""
        
    def renameforward(self):
        if self.isvideo():
            try:
                os.rename(self.fullname(), self.nfullname())
                printinfo("...Renamed " + self.fullname() + " -> " + self.nfullname())
                return True
            except OSError:
                printerror("Failed to rename file " + self.fullname() + " to " + self.nfullname())
                return False
        return False
    
    def renameback(self):
        if self.isvideo():
            try:
                os.rename(self.nfullname(), self.fullname())
                printinfo("...Renamed " + self.nfullname() + " -> " + self.fullname())
                return True
            except OSError:
                printerror("Failed to rename file " + self.nfullname() + " to " + self.fullname())
                return False
        return False
    
    def removenfile(self):
        if self.isvideo():
            try:
                os.remove(self.nfullname())
                printinfo("...Removed " + self.nfullname())
                return True
            except OSError:
                printerror("Cannot remove " + self.nfullname())
                return False
        return False
    
class filelist():
    def __init__(self, path):
        self.list = []
        i = 0
        os.chdir(path)
        printmessage("Building file list...")
        
        for filename in os.listdir(path):
            newfile = file(filename)
            if newfile.isvideo():
                i += 1
                self.list.append(newfile)
                newfile.renameforward()
                    
        self.length = i
                
    def writemakefile(self):
        line = "all:"
        for f in self.list:
            line += " " + f.nname + ".m4v"
        line += "\n\n%.m4v: %.avi\n\t" 
        line += PROGRAM + " -Z '" + PROFILE 
        line += "' -i $< -o $@\n"
        
        fh = None
        try:
            fh = open("Makefile", "w")
            fh.write(line)
        except EnvironmentError:
            printerror("Error writing Makefile, exiting")
            return False
        finally:
            if fh: fh.close()
        
        return True
               
    def convert(self, n_threads):
        printmessage("Converting...")
        try:
            changecolor("green")
            n_threads = n_threads if (n_threads >= 1) & (n_threads <= 10) else N_THREADS
            res = subprocess.Popen("make -j" + str(n_threads), shell=True)
            res.wait()
            return True
        except OSError:
            printerror("Execution failed")
            return False
        
    def cleanfiles(self, leave, remove):
        printmessage("Cleaning up...")
        try:
            if not leave: 
                os.remove("Makefile")
            else:
                printinfo("...Leaving Makefile")
        except OSError:
            printerror("Cannot remove Makefile", "red")
            
        for f in self.list:
            if remove:
                f.removenfile()
            else:
                f.renameback()
    

def main():
    # Program options definition
    usage = "Usage: %prog [path]"
    parser = OptionParser(usage=usage, version=VERSION)
    parser.add_option("-l", "--leave",
                      action="store_true",
                      default=False,
                      help="leave Makefile after process completion [default: off]")
    parser.add_option("-r", "--remove",
                      action="store_true",
                      default=False,
                      help="remove source files after conversion [default: off]")
    parser.add_option("-t", "--threads",
                      type="int",
                      default=2,
                      help="number of threads [default: 2]")
    
    opts, args = parser.parse_args()
    if args == []: args = "."
    
    fl = filelist(args[0])
    if fl.length > 0:
        fl.writemakefile()
        fl.convert(opts.threads)
        fl.cleanfiles(opts.leave, opts.remove)
        printmessage("Finished!")
    else:
        printerror("Nothing to convert, exiting")
                
main()