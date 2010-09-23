
if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert('python', src=True, target='_doctest', run_doctest=True)

class Foobar(object):
    
    def __init__(self, i):
        print 'Hi #%d.' % i
    
    
  
    

      
for i in range(2):
    print Foobar(i)
for i in range(3):
    print Foobar(i)
     
        
class Baz(object):
    
    
    def __init__(self, i):
        print 'Bye #%d.' % i
for i in range(3):
    print Baz(i)

def doit():
    print 'did it ..'    

for i in range(2):
    print doit()
    
try:
    print 'foobar' + 1
except:
    print 'foobar'
finally:
    print 'foobar' + 'foobar'

print 'hi'