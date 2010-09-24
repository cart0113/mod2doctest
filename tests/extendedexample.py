
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
            
            
        
        
        
