#!/usr/bin/python3

import argparse
from subprocess import call
import os

parser = argparse.ArgumentParser(description='Create and setup a C/C++ project')
parser.add_argument('C/C++', choices=['C', 'C++'])
parser.add_argument('project_name')
parser.add_argument('-l', '--link', required=False)
parser.add_argument('-f', '--flags', required=False, default='-Wall -Werror')
args = parser.parse_args()
args = vars(args)

name = args['project_name']
if os.path.exists(name) and os.path.isdir(name):
    print("The folder already exists!\nExiting...")
    exit(1)

flags = args['flags']

if args['link']:
    call(["git", "clone", args['link'], args['project_name']])

dirs = ('src', 'obj', 'bin', 'include', 'lib', 'depends')

for i in dirs:
    call(["mkdir", "-p", '/'.join((name, i))])

readme = """This is a sample readme for %s.
You should change it as soon as possible!""" % name
if args['link']:
    readme += "It is linked to %s" % args['link']

call("printf \"" + readme + "\" > " + '/'.join((name, 'README.md')), shell=True)

cc = 'gcc'
if args['C/C++'] == 'C++':
    cc = 'g++'

ext = 'c'
if args['C/C++'] == 'C++':
    ext = 'cpp'

common = """TOP := $(dir $(lastword $(MAKEFILE_LIST)))
SRC_DIR := $(TOP)src/
INCLUDE_DIR := $(TOP)include/
BIN_DIR := $(TOP)bin/
OBJ_DIR := $(TOP)obj/
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
LDFLAGS :=

$(OBJ_DIR)%.o: $(SRC_DIR)%.{2}
\t$(CC) $(CPPFLAGS) $(CFLAGS) $< -o $@

$(DEPENDS_DIR)%.d: $(SRC_DIR)%.{2}
\t$(CC) $(CPPFLAGS) $(CFLAGS) -MM $(<:$(SRC_DIR).{2}=.o) $^ > $@
""".format(cc, flags, ext)

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

call("echo \'" + common + "\' > " + '/'.join((name, 'Makefile.common')), shell=True)
call("echo \'" + makefile + "\' > " + '/'.join((name, 'Makefile')), shell=True)

hello = """#include <stdio.h>

int main() {
    printf("Hello world!");
    return 0;
}
"""
call("echo \'" + hello + "\' > " + '/'.join((name, 'src', 'main.' + ext)), shell=True)
print("Done")
