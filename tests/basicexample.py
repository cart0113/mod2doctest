
if __name__ == '__main__':

    # Anything inside a __name__ == '__main__' block is removed
    
    import mod2doctest
    mod2doctest.convert('python', src=True, run_doctest=False)

#>Notes on documentation ..
#>==============================================================================
#|
#|mod2doctest allows you to create comments that show up in the docstr 
#|so you can easily add sphinx rest comments like this:
#| 
#|.. note::  
#|
#|   *  ``#|`` prints only to docstr
#|   *  ``#>`` prints to docstr and stdout
#|
#|For example: 
#|
#|This is just in the docs
#|
#>This prints to the docs and stdout. 
#|

#>Test Setup
#>==============================================================================
import pickle
import os

#|Btw, you can use 'if __name__' blocks anywhere you want, it will not show
#|up in the final docstring.  They are the mod2doctest 'comments', so to speak.
if __name__ == '__main__':
    import log

#>Make A List
#>==============================================================================
alist = [1, -4, 50] + list(set([10, 10, 10]))
alist.sort()
print alist

#>Pickle The List
#>==============================================================================
#|This will print the repr of the pickle string.  If this algorithm every
#|changes -- even if one character is different -- this test will 'break'. 
print repr(pickle.dumps(alist))

#>Ellipses #1: mod2doctest can (if you want) add ellipses to memory IDs
#>==============================================================================
class Foo(object):
    pass

print Foo
print Foo()

#>Ellipses #2: Also, you can add ellipses to file paths
#>==============================================================================
#|This will ellipse the module name
print pickle
#|This will ellipse the current path (only the final rel path will be there). 
os.getcwd()

#>Ellipses #3: mod2doctest can (if you want) add ellipses to tracebacks
#>==============================================================================
print pickle.dumps(os)

#>But, here's another way to exercise exceptions (that's a little cleaner IMHO).
#>==============================================================================
try:
    print pickle.dumps(os)
    print 'This is okay!'
except TypeError, e:    
    print 'Oh no it is not: %s' % e

#> EOF
#>==============================================================================
print "That's all folks."
raise SystemExit # could also do exit() on Python 2.5 or higher

#> Even thought there is more ... the exit prevented this from being called.
#>==============================================================================
print "Hello World?  Anybody there??"
