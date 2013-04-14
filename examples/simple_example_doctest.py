'''

Welcome to mod2doctest
======================

You can easily mix ReST syntax with you expected python.

.. warning::
   make sure to examine your resulting docstr to make sure output is as
   expected!

The basics:
 
>>> print 'Hello World!'
Hello World!

Show that sets, sorting do really work
======================================

A little more:
 
>>> somelist = [100, 2, -20, 3400, 0, 0, 0, 10, 10, 10, 88, -3, 100, 2, -99, -1]
>>> sorted(set(somelist))
[-99, -20, -3, -1, 0, 2, 10, 88, 100, 3400]

Notes on sphinx formatting
==========================

A little more:
 
>>> somelist = [100, 2, -20, 340, 0, 0, 0, 0, 0, 10, 10, 88, -3, 100, 2, -99, -1]
>>> sorted(set(somelist))
[-99, -20, -3, -1, 0, 2, 10, 88, 100, 340]

But single '#' comments do show up.

Stack Traces
============

 
>>> raise KeyError
Traceback (most recent call last):
    ...
KeyError

Define classes, functions inline -- useful for setup, teardown, other things.
=============================================================================

Here is the setup

 
>>> import os
>>> def setup():
...     
...     os.mkdir('foobar')
... 

This comment describes the function below and shows up as inline ReST.
 
>>> def teardown():
...     # This internal comment is retained within the python suite.
...     os.rmdir('foobar')
... 
>>> 
>>> setup()
>>> print os.path.isdir('foobar')
True
>>> 
>>> 
>>> teardown()
>>> print os.path.isdir('foobar')
False
>>> 
>>> 
>>> print teardown()
Traceback (most recent call last):
    ...
OSError: [Errno 2] No such file or directory: 'foobar'

Note, stack traces do not stop the program -- you can have many, many
 
>>> print teardown()
Traceback (most recent call last):
    ...
OSError: [Errno 2] No such file or directory: 'foobar'

Another great way to handle :class:`Exceptions`:
 
>>> try:
...     teardown()
... except OSError:
...     print 'directory "foobar" has already been removed.'
... 
directory "foobar" has already been removed.

'''


if __name__ == '__main__':
    import doctest
    doctest.testmod(
        optionflags=doctest.ELLIPSIS |
        doctest.REPORT_ONLY_FIRST_FAILURE |
        doctest.NORMALIZE_WHITESPACE)

