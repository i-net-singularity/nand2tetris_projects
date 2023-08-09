#!python
import sys,os,html
from collections import deque
from typing import List,Dict

# Symbol kinds
SK_STATIC   = "static"
SK_FIELD    = "field"
SK_ARG      = "argument"
SK_VAR      = "var"
SK_NONE     = "none"


