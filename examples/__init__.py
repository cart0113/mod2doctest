# PYTHON
import re
import doctest
# MOD2DOCTEST
import mod2doctest

main_re = re.compile(r'("""[\s.]*?""")[\s.]*')

delimit = 'Type "help", "copyright", "credits" or "license" for more information.'
end = '\n\nif __name__ == \'__main__\':\n    import doctest\n    doctest.testmod(optionflags=268)'

def process_docstr(docstr):
    docstr = docstr.split(delimit)[1].strip()
    return docstr.replace(end, '')
    
def run_all():
    for file in ['basicexample', 'blanklines', 'fix_input_whitespace']:
        output = process_docstr(mod2doctest.convert(src='%s.py' % file, 
                                                    target=None, 
                                                    run_doctest=False, 
                                                    ))
        known_to_be_good_output = process_docstr(open('%s_doctest.py' % file).read())
        print `output`
        print `known_to_be_good_output`
        assert(output == known_to_be_good_output)
        

if __name__ == '__main__':
    run_all()

