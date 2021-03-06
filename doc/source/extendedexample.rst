extendedexample.py: An example that has timing / threading 
**********************************************************

Input Module
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		
This is the input module::

	if __name__ == '__main__':
	
	    # Anything inside a __name__ == '__main__' block is removed
	    
	    import mod2doctest
	    mod2doctest.convert('python', src=True, target='_doctest', 
	                        run_doctest=False)    
	
	#>Test Setup
	#>------------------------------------------------------------------------------
	import os
	import shutil
	import time
	import threading
	
	#>Setup test: note -- the weird newlines / whitespacing is to stress mod2doctest
	#>------------------------------------------------------------------------------
	dir_main = 'dirmain'
	try:
	    shutil.rmtree(dir_main)    
	except OSError:
	    pass
	finally:
	    print 'Setup complete'
	    os.mkdir(dir_main)
	
	
	#>Make threading class
	#>------------------------------------------------------------------------------
	class Foo(threading.Thread):
	    
	    has_exit = False
	    
	    main_file = os.path.join(dir_main, 'foo.txt')
	    
	    def run(self):
	        
	        while self.has_exit is False:
	            time.sleep(0.100)
	            try:
	                data = open(self.main_file, 'r').read()
	            except IOError:
	                print 'Nothing there ...'
	            else:
	                if 'DONE' in data:                
	                    print 'All done!'
	                    self.has_exit = True
	                elif 'PROCESSING' in data:
	                    print 'Still working ... (note backslash is for doctest)'
	                else:
	                    print 'Cannot deal with %s' % data            
	            finally:
	                print 'I get printed every time.'
	            
	            time.sleep(2)
	
	print 'Made the class'
	
	#>Now, put it all together -- q
	#>------------------------------------------------------------------------------
	print 'Starting test ...'
	
	foo = Foo()
	foo.start()   
	
	time.sleep(1)
	open(Foo.main_file, 'w').write('PROCESSING')           
	
	time.sleep(4)
	open(Foo.main_file, 'w').write('BAZ')           
	            
	time.sleep(4)
	open(Foo.main_file, 'w').write('DONE')     
	
	foo.join()
	
	#>Finally, cleanup test
	#>------------------------------------------------------------------------------
	shutil.rmtree(dir_main)
	print 'All cleaned up!'

printout to stdout/stderr
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

It prints to stdout/stderr like this::
            

	Python 2.6.2 (r262:71605, Apr 14 2009, 22:40:02) [MSC v.1500 32 bit (Intel)] on win32
	Type "help", "copyright", "credits" or "license" for more information.
	
	
	Test Setup
	------------------------------------------------------------------------------
	
	
	Setup test: note -- the weird newlines / whitespacing is to stress mod2doctest
	------------------------------------------------------------------------------
	Setup complete
	
	
	Make threading class
	------------------------------------------------------------------------------
	Made the class
	
	
	Now, put it all together -- q
	------------------------------------------------------------------------------
	Starting test \...
	Nothing there \...
	I get printed every time.
	Still working \... (note backslash is for doctest)
	I get printed every time.
	Still working \... (note backslash is for doctest)
	I get printed every time.
	Cannot deal with BAZ
	I get printed every time.
	Cannot deal with BAZ
	I get printed every time.
	All done!
	I get printed every time.
	
	
	Finally, cleanup test
	------------------------------------------------------------------------------
	All cleaned up!

creates the following output '_doctest' module::

	r"""
	================================================================================
	Auto generated by mod2doctest on Sat Sep 25 15:53:10 2010
	================================================================================
	Python 2.6.2 (r262:71605, Apr 14 2009, 22:40:02) [MSC v.1500 32 bit (Intel)] on win32
	Type "help", "copyright", "credits" or "license" for more information.
	
	Test Setup
	------------------------------------------------------------------------------
	 
	>>> import os
	>>> import shutil
	>>> import time
	>>> import threading
	
	Setup test: note -- the weird newlines / whitespacing is to stress mod2doctest
	------------------------------------------------------------------------------
	 
	>>> dir_main = 'dirmain'
	>>> try:
	...     shutil.rmtree(dir_main)
	... except OSError:
	...     pass
	... finally:
	...     print 'Setup complete'
	...     os.mkdir(dir_main)
	... 
	Setup complete
	
	Make threading class
	------------------------------------------------------------------------------
	 
	>>> class Foo(threading.Thread):
	...     
	...     has_exit = False
	...     
	...     main_file = os.path.join(dir_main, 'foo.txt')
	...     
	...     def run(self):
	...         
	...         while self.has_exit is False:
	...             
	...             time.sleep(0.100)
	...             
	...             try:
	...                 data = open(self.main_file, 'r').read()
	...             except IOError:
	...                 print 'Nothing there \...'
	...             else:
	...                 if 'DONE' in data:
	...                     print 'All done!'
	...                     self.has_exit = True
	...                 elif 'PROCESSING' in data:
	...                     print 'Still working \... (note backslash is for doctest)'
	...                 else:
	...                     print 'Cannot deal with %s' % data
	...             finally:
	...                 
	...                 print 'I get printed every time.'
	...             
	...             time.sleep(1.900)
	... 
	>>> print 'Made the class'
	Made the class
	
	Now, put it all together -- q
	------------------------------------------------------------------------------
	 
	>>> print 'Starting test \...'
	Starting test \...
	>>> 
	>>> foo = Foo()
	>>> foo.start()
	>>> 
	>>> time.sleep(1)
	Nothing there \...
	I get printed every time.
	>>> open(Foo.main_file, 'w').write('PROCESSING')
	>>> 
	>>> time.sleep(4)
	Still working \... (note backslash is for doctest)
	I get printed every time.
	Still working \... (note backslash is for doctest)
	I get printed every time.
	>>> open(Foo.main_file, 'w').write('BAZ')
	>>> 
	>>> time.sleep(4)
	Cannot deal with BAZ
	I get printed every time.
	Cannot deal with BAZ
	I get printed every time.
	>>> open(Foo.main_file, 'w').write('DONE')
	>>> 
	>>> foo.join()
	All done!
	I get printed every time.
	
	Finally, cleanup test
	------------------------------------------------------------------------------
	 
	>>> shutil.rmtree(dir_main)
	>>> print 'All cleaned up!'
	All cleaned up!
	
	"""
	
	if __name__ == '__main__':
	    import doctest
	    doctest.testmod(optionflags=524)


which looks like this when you use an ``automodule`` sphinx directive: 

.. automodule:: tests.extendedexample_doctest


