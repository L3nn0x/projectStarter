#!/usr/bin/python3

import argparse
from subprocess import call
import os

def getPathName(pathname):
    tmp = os.path.split(pathname)
    return tmp[-1]

parser = argparse.ArgumentParser(description='Create and setup a C/C++ project')
parser.add_argument('C/C++', choices=['C', 'C++'])
parser.add_argument('project_name')
parser.add_argument('-f', '--flags', required=False)
parser.add_argument('-l', '--ldflags', required=False)
args = parser.parse_args()
args = vars(args)

pathname = args['project_name']
name = getPathName(pathname)

if os.path.exists(pathname) == True or os.path.isdir(pathname) == True:
    print("The folder already exists!\nExiting...")
    exit(1)

ldflags = args['ldflags']
flags = args['flags']
if not flags:
    flags = '-Wall -Werror'
    if args['C/C++'] == 'C++':
        flags += ' -std=c++11'

dirs = ('src', 'obj', 'bin', 'include', 'lib', 'depends')

print("Creating folders...")
for i in dirs:
    os.makedirs(os.path.join(pathname, i))
print("Done!")

readme = """This is a sample readme for %s.
You should change it as soon as possible!""" % name

print("Writing README...")
with open(os.path.join(pathname, 'README.md'), 'w') as f:
    f.write(readme)
print("Done!")

cc = 'gcc'
ext = 'c'
if args['C/C++'] == 'C++':
    cc = 'g++'
    ext = 'cpp'

common = """TOP := $(dir $(lastword $(MAKEFILE_LIST)))
SRC_DIR := $(TOP)src/
INCLUDE_DIR := $(TOP)include/
BIN_DIR := $(TOP)bin/
OBJ_DIR := $(TOP)obj/
LIB_DIR := $(TOP)lib/
DEPENDS_DIR := $(TOP)depends/

CC := {0}
CFLAGS := -c {1}
DEBUG ?= yes
ifeq ($(DEBUG), yes)
\tCFLAGS += -g
else
\tCFLAGS += -O2
endif
CPPFLAGS := -I$(INCLUDE_DIR)
LDFLAGS := -L$(LIB_DIR) {3}

$(OBJ_DIR)%.o: $(SRC_DIR)%.{2}
\t$(CC) $(CPPFLAGS) $(CFLAGS) $< -o $@

$(DEPENDS_DIR)%.d: $(SRC_DIR)%.{2}
\t$(CC) $(CPPFLAGS) $(CFLAGS) -MM $(<:$(SRC_DIR).{2}=.o) $^ > $@
""".format(cc, flags, ext, ldflags)

makefile = """include Makefile.common

OUTFILE := $(BIN_DIR){0}
SRC_FILES := $(wildcard $(SRC_DIR)*.{1})
OBJ_FILES := $(subst $(SRC_DIR),$(OBJ_DIR),$(SRC_FILES:%.{1}=%.o))

.PHONY: all clean mrproper

all: $(OUTFILE)

$(OUTFILE) : $(OBJ_FILES)
\t$(CC) $^ -o $@ $(LDFLAGS)

clean:
\tfind -name "*.o" -delete
\tfind -name "*~" -delete
\tfind -name "\#*" -delete

mrproper: clean
\t$(RM) $(BIN_DIR)
\tfind -name "*.d" -delete
\t$(RM) TAGS

include $(subst $(SRC_DIR),$(DEPENDS_DIR),$(SRC_FILES:%.{1}=%.d))
""".format(name, ext)

print("Writing Makefile.common...")
with open(os.path.join(pathname, 'Makefile.common'), 'w') as f:
    f.write(common)
print("Done!")
print("Writing Makefile...")
with open(os.path.join(pathname, 'Makefile'), 'w') as f:
    f.write(makefile)
print("Done!")

hello = """#include <stdio.h>

int main() {
    printf("Hello world!\\n");
    return 0;
}
"""

print("Writing default src file...")
with open(os.path.join(os.path.join(pathname, 'src'), 'main.' + ext), 'w') as f:
    f.write(hello)
print("Done!")

gitignore = """%s
*.o
*.d
*~
#*
*.*.sw*
""" % name
print("Adding .gitignore to every folders...")
for i in dirs:
    with open(os.path.join(os.path.join(pathname, i), '.gitignore'), 'w') as f:
        f.write(gitignore)

print("Initializing git repository and creating first commit")
w = os.getcwd()
os.chdir(pathname)
call(['git', 'init'])
call(['git', 'add', '.'])
call(['git', 'commit', '-m', 'First commit'])
os.chdir(w)
print("Done!")
print("\n\nWorking folder configured!")
