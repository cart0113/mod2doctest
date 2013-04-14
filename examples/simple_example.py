

if __name__ == '__main__':
    # Import the basics ...
    import sys
    sys.path.insert(0, '/home/ajcarter/workspace/GIT_MOD2DOCTEST')
    import mod2docstring
    mod2docstring.convert(difftool='bcompare')


# Welcome to mod2doctest
# ======================
#
# You can easily mix ReST syntax with you expected python.
#
# .. warning::
#    make sure to examine your resulting docstr to make sure output is as
#    expected!

# The basics:
print 'Hello World!'

# Show that sets, sorting do really work
# ======================================
#
# A little more:
somelist = [100, 2, -20, 3400, 0, 0, 0, 10, 10, 10, 88, -3, 100, 2, -99, -1]
sorted(set(somelist))


# Notes on sphinx formatting
# ==========================
#
# A little more:
somelist = [100, 2, -20, 340, 0, 0, 0, 0, 0, 10, 10, 88, -3, 100, 2, -99, -1]
sorted(set(somelist))

##
## Double 'pound' commments do not show up at all in the final docstr
## for x in range(10):
##     yield x
##
##
# But single '#' comments do show up.

# Stack Traces
# ============
#
raise KeyError


# Define classes, functions inline -- useful for setup, teardown, other things.
# =============================================================================

# Here is the setup
#
import os
def setup():

    os.mkdir('foobar')

# This comment describes the function below and shows up as inline ReST.
def teardown():
    # This internal comment is retained within the python suite.
    os.rmdir('foobar')


setup()
print os.path.isdir('foobar')


teardown()
print os.path.isdir('foobar')


print teardown()

# Note, stack traces do not stop the program -- you can have many, many
print teardown()

# Another great way to handle :class:`Exceptions`:
try:
    teardown()
except OSError:
    print 'directory "foobar" has already been removed.'





















