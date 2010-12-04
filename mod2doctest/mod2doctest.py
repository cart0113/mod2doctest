"""Converts a Python module to a |doctest| testable docstring.

The basic idea behind |mod2doctest| is provide a *snapshot* of the current
run of a module.  That is, you just point |mod2doctest| to a module and it
will:

*  Run the module in a interperter.
*  Add all the '>>>' and '...' as needed.
*  Copy all the output from the run and put it under the correct input.
*  Add ellipses where needed like to memory ids and tracebacks.
*  And provide other formating options.

This allows you to quickly turn any Python module into a test that you can use
later on to test refactors / regression testing / etc.

Attributes:

    convert (function): The public interface to |mod2doctest| is the
    :func:`convert` function.

    DEFAULT_DOCTEST_FLAGS (int): The default |doctest| flags used when 1)
    running doctest (if :func:`convert` is directed to run doctest) or
    when adding the ``if __name__ == '__main__'`` clause to an output
    ``target`` file.  The default options are::

        import doctest
        DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS |
                                 doctest.REPORT_ONLY_FIRST_FAILURE |
                                 doctest.NORMALIZE_WHITESPACE)

"""

import sys
import os
import inspect
import subprocess
import re
import doctest
import time
import pdb
import atexit


DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS |
                         doctest.REPORT_ONLY_FIRST_FAILURE |
                         doctest.NORMALIZE_WHITESPACE)

def convert(python_cmd,
            src=True,
            target='_doctest',
            add_autogen=True,
            add_testmod=True,
            ellipse_memid=True,
            ellipse_traceback=True,
            ellipse_path=True,
            run_doctest=False,
            doctest_flags=DEFAULT_DOCTEST_FLAGS,
            fn_process_input=None,
            fn_process_docstr=None,
            fn_title_docstr=None,
            ):
    """
    :summary: Runs a module in shell, grabs output and creates a docstring.

    :param python_cmd: The python command that starts the shell (e.g. python
                       or /bin/python2.4, etc).
    :type python_cmd:  str

    :param src: The python module to be converted. If ``True`` is given, the
                current module is used.  Otherwise, you need to provide
                either 1) a valid python module object or 2) a path (string)
                to the module to be run.
    :type src:  True, module or file path

    :param target: Where you want the output docstring to be placed:

                   * ``None``, the docstring is not saved anywhere (but it is
                     returned by this function and convert will not exit).
                   * ``True`` is given, the src module is used (the
                     docstring is prepended to the file).
                   * A path (of type str) is provided, the docstr is saved to
                     that file.
                   * And finally, a simple convention: if a string is given
                     that starts with '_' (e.g. '_doctest'), the output is saved
                     to a file with the same name as the input, but with that
                     string inserted right before the '.py' of the file name.
                     For example, if the src filename is 'mytest.py' and the
                     target is '_doctest' the docstring output will be saved to a
                     file called 'mytest_doctest.py'

    :type target:  None, True, str file path, or str starting with '_'

    :param add_autogen: If True adds boilerplate python version / timestamp
                        of current run to top of docstr.
    :type add_autogen:  True or False

    :param add_testmod: If True a ``if __name__ == '__main__'`` block is added
                        to the output file IF the ``target`` parameter is an
                        external file (str path).
    :type add_testmod:  True or False

    :param ellipse_memid: Add ellipse for memory ids.
    :type ellipse_memid: True or False

    :param ellipse_paths: Add ellipse for front path of path (up to final rel
                          path)
    :type ellipse_paths:  True or False

    :param ellipse_traceback: Ellipse middle part of traceback.
    :type ellipse_traceback: True or False

    :param run_doctest: If True doctest is run on the resulting docstring.
    :type run_doctest:  True or False

    :param doctest_flags: Valid OR'd together :mod:`doctest`
                          flags.  The default flags are ``(doctest.ELLIPSIS |
                          doctest.REPORT_ONLY_FIRST_FAILURE |
                          doctest.NORMALIZE_WHITESPACE)``
    :type doctest_flags: :mod:`doctest` flags

    :param fn_process_input: A function that is called and is passed the
                             module input.  Used for preprocessing.
    :type fn_process_input:  callable


    :param fn_process_docstr: A function that is called and is passed the
                              final docstring before saving.  Used for post
                              processing. You can use this function to perform
                              your own custom regular expressions
                              replacements and remove temporal / local data
                              from your output before |doctest| is run.
    :type fn_process_docstr:  callable

    :param fn_title_docstr: A function that is called and should return a
                            string that will be used for the title.
    :type fn_title_docstr:  callable

    :returns: None or, if ``target=None`` a docstring of type str.
    """

    if src is True:
        src = sys.modules['__main__']
    elif isinstance(src, str):
        if not os.path.isfile(src):
            raise SystemError, "Cannot find src file %s ..." % src
    else:
        raise SystemError, "Unknown src type %s ..." % src

    if inspect.ismodule(src):
        input = open(src.__file__, 'r').read()
    elif isinstance(src, str) and os.path.isfile(src):
        input = open(src, 'r').read()
    elif isinstance(src, str):
        input = src
    else:
        raise SystemError, ("'src' %s must be a valid module or file path, "
                            "or string ...") % obj

    # First, remove the docstring.  Keep the input variable around, it's
    # needed later on (the raw input with just the docstring removed).
    input = _input_remove_docstring(input)

    pinput = _input_fix_whitespace(input)

    pinput = _input_escape_shell_prompt(pinput)
    pinput = _input_remove_name_eq_main(pinput)

    # Remove extra whitespace at end.
    # You need to do this AFTER the removing of ``if __name__ == '__main__'``
    pinput = pinput.strip()
    pinput = pinput.replace('\r', '')
    pinput = pinput.replace('\t', '    ')

    popen = subprocess.Popen(args="%s -i" % python_cmd,
                             bufsize=-1,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )

    docstr = _communicate(pinput, popen)

    if ellipse_memid:
        docstr = _docstr_ellipse_mem_id(docstr)

    if ellipse_path:
        docstr = _docstr_ellipse_paths(docstr)

    if ellipse_traceback:
        docstr = _docstr_ellipse_traceback(docstr)

    docstr = _process_docstr_markers(docstr)

    if fn_process_docstr:
        docstr = fn_process_docstr(docstr)

    if add_autogen is False:
        fn_title_docstr = lambda docstr: ''

    if fn_title_docstr:
        doctitle = fn_title_docstr(docstr)

    if add_autogen:
        doctitle = '%s\n' % _docstr_get_title()
    else:
        doctitle = '\n'
        docstr = '\n'.join(docstr.split('\n')[3:-2]).lstrip()

    # Remember to remove any triple quotes """
    docstr = docstr.replace("'''", '"""')

    docstr = "'''%s%s\n\n'''" % (doctitle, docstr.strip())

    docstr = _docstr_cleanup_docstr(docstr)

    if target:
        target = _docstr_save(docstr, src, target, input, add_testmod)
        if run_doctest:
            _run_doctest(target, doctest_flags)
        raise SystemExit
    else:
        return docstr

_ADD_TESTMOD_STR = """
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=%d)
"""

_RE_INPUT_PROCESS = re.compile(r"""
^\s*            # Start of file, exclude whitespace
(r|R)?          # Allow for raw-strings
'''             # First triple quote.
(.|\n)*?        # Everything in-between, but a non-greedy match
'''             # Second triple quote.
\s*             # Get rid of all other whitespace.
""", flags=re.VERBOSE)
def _input_remove_docstring(input):
    """Strips the input and removes the first docstring from the input.

    .. note;:

       The first docstring is never treated as part of the input file.
       Most notably, because this is when -- if directed -- mod2doctest
       will put the output docstring (at the top of the file).

    """
    input = '\n\n' + _RE_INPUT_PROCESS.sub('', input).strip() + '\n'
    return input.replace(r'\r', r'')

def _input_escape_shell_prompt(input):
    """Replaces `>>>` and '...' with escaped versions."""
    input = input.replace('>>>', '\>>>')
    return input.replace('...', '\...')

def _input_fix_whitespace(input):
    """Fixes problems with spaces in the input that cause interpreter errors.

    There are two major problems and will use ^ to denote spaces
    Normally, a statement like::

        def fn():

        ^^^^print 'foobar'

    will not work if directly copied / pasted because there are no spaces after
    the ``def fn():`` line.

    Also::

        def fn():
        ^^^^print 'hi'
        def fx():
        ^^^^print 'bye'

    does not allow direct copy paste either (you need a newline betwen the fn
    calls). This will run fine within a module but **not** if pasted into the
    interpreter. This function fixes these problem.

    The strategy is to collect all whitespace/comments and hold them in the
    ``hold`` list.  Then, track the current indent level.  When a non
    whitespace/comment line is encountered, apply the stored whitespace
    with the correct level of indentation.  Also, add a blank line between
    statements like those shown above.

    .. note::

       This function makes assumptions about the Python syntax as taken
       from http://docs.python.org/reference/compound_stmts.html

    """
    lines = []
    input = input.replace('\r', '')
    input = input.replace('\t', ' '*4)
    hold = []
    last_indent = 0
    stackable_tokens = set(['else', 'elif', 'except', 'finally'])
    for line in input.split('\n'):
        left_stripped = line.lstrip()
        if not left_stripped or left_stripped.startswith('#'):
            # collect all blank lines or full comment lines
            hold.append(left_stripped)
        else:
            new_indent = len(line) - len(left_stripped)
            if left_stripped.split()[0].split(':')[0] not in stackable_tokens:
                # Add whitespace if, for example, two functions are defined
                # with no whitespace in between
                if not hold and new_indent < last_indent:
                    lines.append(' '*new_indent)
                last_indent = new_indent

            hold = ['%s%s' % (' '*last_indent, h,) for h in hold]
            lines.extend(hold)
            hold = []

            lines.append(line.rstrip())

    return '\n'.join(lines)

_RE_NEM = re.compile(r"""^if\s+__name__\s*==\s*['"]+__main__['"]+\s*:""",
                     flags=re.IGNORECASE)
def _input_remove_name_eq_main(input):
    lines = []
    in_nem = False
    for line in input.split('\n'):
        if _RE_NEM.match(line):
            in_nem = True
            lines.append('') # add one blank line for every nem
        elif in_nem and line.strip() and line[0] not in ' \t':
            in_nem = False
        if in_nem is False:
            lines.append(line)
    return '\n'.join(lines)

def _communicate(pinput, popen):

    pinput = '%s\n\nraise SystemExit\n\n' % pinput

    pinputlines = pinput.split('\n')

    stdout, stderr = popen.communicate(pinput)

    docstrlines = []

    intraceback = False
    startheader = True

    for outputline in stdout.split('\n'):
        outputline = outputline.replace('\r', '')
        outputline = outputline.replace('\t', '    ')

        for line in _match_input_to_output(pinputlines, outputline):

            docstrlines.append(line)

            if line.startswith('>>> #>') or line.startswith('... #>'):
                if startheader:
                    print '\n'
                line = line[6:]
                startheader = False
            elif line.startswith('>>> ') or line.startswith('...'):
                startheader = True
                continue

            if line.startswith('Traceback') or line.startswith('Exception'):
                intraceback = True
            elif intraceback and not line.startswith(' '):
                intraceback = None

            if intraceback is False:
                print line
            else:
                time.sleep(0.010)
                print >> sys.stderr, line
                time.sleep(0.010)

            if intraceback is None:
                intraceback = False

    return '\n'.join(docstrlines)

def _match_input_to_output(inputlines, outputline):

    has_input = True

    while has_input:
        if outputline.startswith('>>> ') or outputline.startswith('... '):
            if inputlines:
                yield "%s%s" % (outputline[0:4], inputlines.pop(0),)
                outputline = outputline[4:]
            else:
                yield ""
                has_input = False
        else:
            yield outputline
            has_input = False

_RE_SPLIT_TRACEBACK = re.compile(r"""
                                  (Traceback.*
                                  (?:\n[ |\t]+.*)*
                                  \n\w+.*)
                                  """, flags=re.MULTILINE | re.VERBOSE)

_RE_OUTPUT_FIXUP = re.compile(r'^[ \t]*$', flags=re.MULTILINE)
def _docstr_fix_blanklines(docstr):
    return _RE_OUTPUT_FIXUP.sub(r'<BLANKLINE>', docstr)

def _docstr_get_title():
    return "\n%s\nAuto generated by mod2doctest on %s\n%s" % \
           ('='*80, time.ctime(), '='*80)

def _docstr_save(docstr, src, target, input, add_testmod):

    if inspect.ismodule(src):
        src = src.__file__
    elif not isinstance(src, str):
        raise SystemError, "Unknown src type %s ..." % src

    if target is True:
        target = src
    elif isinstance(target, str):
        if target.startswith('_'):
            target = '%s%s.py' % (src.replace('.py', ''), target)
        # Then, if target a string (not True) it is different than the src
        # Therefore, blank out the input so we just get a docstring.
        input = ''
    else:
        raise SystemError, "Unknown target type %s ..." % target

    if add_testmod and src is not target:
        if add_testmod is True:
            add_testmod  = _ADD_TESTMOD_STR % DEFAULT_DOCTEST_FLAGS
    else:
        add_testmod = ''

    output = 'r%s\n%s\n%s' % (docstr,
                              add_testmod,
                              input)

    open(target, 'w').write(output)

    return target

_RE_ELLIPSE_MEM_ID = re.compile(r'<(?:(?:\w+\.)*)(.*? at 0x)\w+>')
def _docstr_ellipse_mem_id(docstr):
    return _RE_ELLIPSE_MEM_ID.sub(r'<...\1...>', docstr)

_RE_ELLIPSE_TRACEBACK = re.compile(r"""
                                    (Traceback.*)
                                    (?:(?:\n[ |\t]+.*)*)
                                    (\n\w+.*)
                                    """, flags=re.MULTILINE | re.VERBOSE)
def _docstr_ellipse_traceback(docstr):
    return _RE_ELLIPSE_TRACEBACK.sub(r'\1\n    ...\2', docstr)

_RE_LOCAL_PATH = re.compile(r"""
                             (?:\S*(?:[/\\][^\s/\\]+)+)
a                            ([/\\][^\s/\\]+)
                             """, flags=re.VERBOSE)
def _docstr_ellipse_paths(output):
    return _RE_LOCAL_PATH.sub(r'...\1', output)

_RE_PRINT_MARKER = re.compile(r'(?:>>>|...)\s#[>|]')
def _process_docstr_markers(docstr):

    lines = []
    in_print = False

    for line in docstr.split('\n'):
        if _RE_PRINT_MARKER.match(line):
            if in_print is False:
                lines.append('')
            in_print = True
            if len(line) >= 8 and line[6] == ' ' and line[7] != '':
                line = line[7:]
            else:
                line = line[6:]
        elif line.startswith('>>> ') or line.startswith('... '):
            if in_print is True and line.strip() == '...':
                line = ''
            elif in_print is True:
                in_print = False
                lines.append(' ')
                if line.startswith('...'):
                    line = '>>> %s' % line[4:]

        lines.append(line)

    return '\n'.join(lines)

def _docstr_cleanup_docstr(docstr):

    lines = []

    extra_marker = None
    for line in docstr.split('\n'):
        test = line.strip()
        if test == '>>>' or test == '...':
            extra_marker = line
        else:
            if extra_marker and test:
                lines.append(extra_marker)
            extra_marker = None
            lines.append(line)

    return '\n'.join(lines)

def _run_doctest(target, doctest_flags):
    doctest.testfile(target, optionflags=doctest_flags)




