#!/bin/bash

set -e
set -v

pip install jip
jip install $JYTHON
#jip install joda-time:joda-time:2.3

#
# Install Jython
#
NON_GROUP_ID=${JYTHON#*:}
_JYTHON_BASENAME=${NON_GROUP_ID/:/-}
export CLASSPATH=$VIRTUAL_ENV/javalib/*
java -jar $VIRTUAL_ENV/javalib/${_JYTHON_BASENAME}.jar -s -d $HOME/jython
ls $HOME/jython/bin

#
# Create virtual environment
#
virtualenv --version
virtualenv -p $HOME/jython/bin/jython $HOME/myvirtualenv

#
# Install packages into the jython virtual environment
#
export PATH=$HOME/myvirtualenv/bin:$PATH
export PYTHON=$HOME/myvirtualenv/bin/python
