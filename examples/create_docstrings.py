
# Import the basics ...
import sys
sys.path.insert(0, '/home/ajcarter/workspace/GIT_MOD2DOCTEST')
import mod2docstring

mod2docstring.convert(
    src='./simple_example.py', dst=True, difftool='bcompare')



