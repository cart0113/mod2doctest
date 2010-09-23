.. role:: raw-html(raw)
   :format: html

.. |mod2doctest|    replace:: :mod:`mod2doctest`
.. |doctest|  		replace:: :mod:`doctest`

mod2doctest
***********

Why mod2doctest?
================


With |mod2doctest| you can set up a test the "quick and dirty" way -- just by
making a module that tests your code, running it, and then inspecting the 
output.  Then, you can use |mod2doctest| to take a snapshot of the output and 
convert it to a permanent test fixture -- a :mod:`doctest` testable docstring.  
This docstring is now something that you can add to a test suite or can be 
picked up by module like :mod:`nose`.

In a nut shell, |mod2doctest| saves you from copying and pasting output 
into "doctest-able" docstrings.  So, if you've ever been bothered by having 
to cut and paste output into your docstring (or unit test assert function, 
too) then maybe give |mod2doctest| a try.

Also, by using :class:`m2d_print` utility functions and following a few 
conventions, you can easily make pretty printed docstrings that looks better
than a raw interpreter shell dump.  Also, these strings play nicely with 
Sphinx so you can easily have a web front end for your test suite. Check out 
the Tests_ to see example of simple python modules that are converted to test 
documentation. 



But what could be easier than just writing a docstring?
-------------------------------------------------------

|doctest| is great and really makes writing unit/functional tests easier. 
However, there are still some manual steps. Also, if you choose to write 
doctests in the docstring directly, you'll lose IDE features like code 
completion, debugging, etc. If you have a bigger test, 
this can lead to some pain if you need to go back and changes and need to 
re-updated the entire docstring each time.  

|mod2doctest| also formats the output for nice display and  
provides many conveniences like: 

*  Adding all '>>>' and '...' if you write doctest docstrings directly. 

*  Or if you create tests in the interpreter (or copy them from a module to 
   the interpreter) you still need to copy and paste output from the 
   interpreter (or from the doctest 'expected' output).

*  And then, you need to format the output, add ellipses for certain fields, 
   etc. 
   
*  Adding whitespace, etc. so the test output is more readable. 

*  Allowing you to develop your test in a normal python module where you
   can take advantage of many IDE features like code completion, debugging, 
   etc. 

*  Processing comments so they don't show up in the '>>>' output -- they
   just show up as text in the docstr, which is what you want. 

*  Removes and ``if __name__ == '__main__'`` blocks from the input.  
   This allows you to create code that does not show up in the docstring
   (like importing |mod2doctest| itself. 

*  Adding :mod:`doctest` ellipses to common things like file paths, memory
   ids, and tracebacks. 

*  Allows you to pass your own functions to pre/post process data (using
   regular expressions or any way you like). 

*  Providing the :class:`m2d_print` functions which both pretty prints to 
   stdout and the docstr in a way that just 'makes sense'. 

*  Breaking the '>>>' stream on two newlines.  This allows you to easily
   create whitespace 'breaks' in the output docstring module (something 
   not possible when you copy and paste from shell). 

*  Right strips lines to avoid extra '...' in the docstrings. 

*  If you want, auto add ``if __name__ == '__main__':`` :mod:`doctest` blocks 
   to your output docstring. 

*  Automatically run :mod:`doctest` for you to see if there were any problems. 

*  Fixes several other common white space problems. 
  
Also, a goal is to make nice looking :mod:`sphinx` compatibale docstrings that 
can be included in your documentation.  See the `Tests`_ section for examples.

Basically, after you get used to how |mod2doctest| works, you can write a 
module with the final output docstring in mind.  This way, all you need to do 
is run your module but you get sphinx ready docstrings with no extra effort. 




Installation for Python 2.4 through 2.6
=======================================

Try::

	easy_install mod2doctest

If that does not work go to http://pypi.python.org/pypi/mod2doctest/.

There you can grab the windows installer, egg, or source directly. 

Also, go to http://bitbucket.org/cart0113/mod2doctest/ to grab the latest repo.



Basic Example
=============

Let's say we have a script ``myscript.py`` like the one below.  Please
first note:

*  The ``if __name__ == '__main__'`` clause which actually calls 
   |mod2doctest|.  It needs to be first because, when you run the module, 
   there is an error in it (which will get captured in the docstr).
   
*  The ``if __name__ == '__main__'`` gets stripped out by |mod2doctest|. 

with that said, here's the module contents::

	if __name__ == '__main__':
	    import mod2doctest
	    mod2doctest.convert(src=True, target=True, run_doctest=True)
	
	
	#===============================================================================
	# Test Setup
	#===============================================================================
	import pickle
	import os
	
	
	#===============================================================================
	# Make A List
	#===============================================================================
	alist = [1, -4, 50] + list(set([10, 10, 10]))
	alist.sort()
	print alist
	
	
	#===============================================================================
	# Pickle The List
	#===============================================================================
	print `pickle.dumps(alist)`
	
	
	#===============================================================================
	# Add some ellipses
	#===============================================================================
	class Foo(object):
	    pass
	
	print Foo()
	print pickle
	os.getcwd()
	
	
	#===============================================================================
	# This should cause an error
	#===============================================================================
	print pickle.dumps(os)

	
We now end up with this docstring that is prepended to the ``myscript.py``::

	r"""
	================================================================================
	Auto generated by mod2doctest on Sat Nov 28 13:54:55 2009
	================================================================================
	
	Python 2.4.4 (#71, Oct 18 2006, 08:34:43) [MSC v.1310 32 bit (Intel)] on win32
	Type "help", "copyright", "credits" or "license" for more information.
	
	
	===============================================================================
	Test Setup
	===============================================================================
	>>> import pickle
	>>> import os
	
	
	===============================================================================
	Make A List
	===============================================================================
	>>> alist = [1, -4, 50] + list(set([10, 10, 10]))
	>>> alist.sort()
	>>> print alist
	[-4, 1, 10, 50]
	
	
	===============================================================================
	Pickle The List
	===============================================================================
	>>> print `pickle.dumps(alist)`
	'(lp0\nI-4\naI1\naI10\naI50\na.'
	
	
	===============================================================================
	Add some ellipses
	===============================================================================
	>>> class Foo(object):
	...     pass
	...
	>>> print Foo()
	<...Foo object at 0x...>
	>>> print pickle
	<module 'pickle' from '...pickle.pyc'>
	>>> os.getcwd()
	'...tests'
	
	
	===============================================================================
	This should cause an error
	===============================================================================
	>>> print pickle.dumps(os)
	Traceback (most recent call last):
	...
	TypeError: can't pickle module objects
	
	"""

Note, we used ``src=True`` and ``target=True`` in our call to :func:`convert`. 
This told |mod2doctest| to use the current module as the source and to prepend
the docstring to the current module.  ``target`` can also be a file path which
will then contain the docstring output. 

	



A Word Of Warning
=================

Here's the warning: **make sure to carefully inspect the output docstring or
final sphinx webpage generated by mod2doctest**. 

|mod2doctest| basically provides a 'snapshot' of the current module run.  
Since it automatically copies the output to the docstring, it can be easy to 
skip the step of actually checking the output and have wrong output in the 
docstring.  That is, just because the test ran does not mean it is what you 
really want. 

To be a useful test fixture that can be used for, say regression testing you
need to make sure the 'snapshot' contains the intended results. 


Just One More Thing: Running Your Test. 
=======================================

Just a quick note -- :mod:`mod2doctest` can run your script up to two times
if the ``run_doctest`` parameter is set to ``True``. 

For the example script::

	if __name__ == '__main__':
		import mod2doctest
		mod2doctest.convert(src=True, target='_doctest', run_doctest=True)
	
	print 'Foobar'   

will be execute two times: once when the script is piped to a shell and once
by doctest itself (to check if the doctest does in fact pass)

The script::

	if __name__ == '__main__':
		import mod2doctest
		mod2doctest.convert(src=True, target='_doctest', run_doctest=False)
	
	print 'Foobar'   

will run only once (this one is not run in doctest).

will run once -- just when the module code is piped to the shell.    

.. note:: 

   You may notice this if you have sleep / delay / blocking in your test and 
   your test is slow to run.   If you run mod2doctest like the first example it 
   takes two times longer to run than you might have been expecting.  


API
===

.. automodule:: mod2doctest
.. autofunction:: mod2doctest.convert
.. autoclass:: mod2doctest.FLAGS
.. autoclass:: mod2doctest.m2d_print


Tests
=====

One great thing about |doctest| is that your tests can easily be converted
to webpages using :mod:`sphinx`.  Even for large test programs the linear 
webpage output is a really great tool to understand the test setup and overall
test structure (which is a great reason to use |doctest| over :mod:`unittest`
even for large programs). 

By using the comment stripping feature and the :class:`m2d_print` utility
functions, |mod2doctest| can convert those `quick and dirty` scripts you threw 
together to test your module into usable documentation.  

The following tests below were generated using these techniques. 

.. note::

   In this case, to best understand what's going on, look in mod2doctest.tests 
   package.  And, if you want, go to 
   http://bitbucket.org/cart0113/mod2doctest/, clone the repo, and
   check out how those modules and how they are used in the Sphinx 
   documentation. 

.. toctree::
   :maxdepth: 1
	
   basicexample


How Does |mod2doctest| Work?
============================

Basically, |mod2doctest| takes your input, pipes it to an interpreter using the
:mod:`subprocess` module and then uses a bunch of :mod:`re` regular expressions
to massage the output.  It is, really, just a chain of regular expressions. 


Indices and Tables
==================
* :ref:`genindex`
* :ref:`search`
