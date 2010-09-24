
if __name__ == '__main__':

    # All __name__ == '__main__' blocks are removed, serving as mod2doctest 
    # comments
    
    import mod2doctest
    mod2doctest.convert('python', src=True, target='_doctest', run_doctest=False, 
                        add_testmod=False, add_autogen=False)    

#>Welcome to mod2doctest
#>++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#|
#|Just enter in some python
#| 
#|.. warning::  
#|   make sure to examine your resulting docstr to make sure output is as 
#|   expected!

#|The basics: 
print 'Hello World!'

#>Extended Example
#>++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#|A little more:
somelist = [100, 2, -20, 340, 0, 0, 10, 10, 88, -3, 100, 2, -99, -1]
sorted(set(somelist))
