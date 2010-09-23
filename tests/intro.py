
if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert('python', src=True, target='_doctest', run_doctest=False, 
                        add_testmod=False)    
#| some other
#>Welcome to mod2doctest
#>------------------------------------------------------------------------------
#|
#|Just enter in some python
#| 
#|.. warning::  
#|   make sure to examine your resulting docstr to make sure output is as 
#|   expected!

#|The basics: 
print 'Hello World!'

import os
import mod2doctest
x = [1, 20]
#>Extended Example
#>------------------------------------------------------------------------------
#|A little more:
somelist = [100, 2, -20, 340, 0, 0, 10, 10, 88, -3, 100, 2, -99, -1]
sorted(set(somelist))
           
