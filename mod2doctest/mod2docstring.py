"""\
Converts a Python module to a |doctest| testable docstring.

The basic idea behind |mod2doctest| is provide a *snapshot* of the current
run of a module.  That is, you just point |mod2doctest| to a source file 
or module and it will convert it to a fully formed docstring. 

*  Run the module in your interperter of choice (defaults to 'python') and
   grabs the stdout/stderr from that interperter.
*  Add all the '>>>' and '...' as needed.
*  Copy all the output from the run and put it under the correct input.
*  Add ellipses where needed like to memory ids and tracebacks.
*  And provide other formating options to make a 'pretty' docstring.

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

import sys as _sys
import os as _os
import types as _types
import inspect as _inspect
import subprocess as _subprocess
import re as _re
import doctest as _doctest
import time as _time
import pdb as _pdb
import atexit as _atexit
from pprint import pprint

def convert(
    src=None,
    fns=None,
    dst=True,
    difftool=None,
    confirm=True,
    python_cmd='python',
    add_if_name_equals_main=True,
    ellipse_memids=True,
    ellipse_tracebacks=True,
    ellipse_paths=True,
    clean_blanklines=True,
    ):
    """
    :summary: Runs a module in shell, grabs output and creates a docstring.

    :param src: The python module to be converted. If ``True`` is given, the
                current module is used.  Otherwise, you need to provide
                either 1) a valid python module object or 2) a path (string)
                to the module to be run.
    :type src:  ``True``, module or file path.

    :param python_cmd: The python command that starts the shell to which 
                       the module contents will be piped. (e.g. 'python'
                       or /usr/bin/python2.7 etc).
    :type python_cmd:  str (default is 'python').

    :param target: Where you want the output docstring to be placed:

                   * If ``True`` the output is 
                     saved to a file with the same name as the input, but with
                     a '_docstr' inserted right before the '.py' of the file 
                     name. For example, if the src filename is 'mytest.py' the 
                     docstring output will be saved to a file called 
                     'mytest_doctest.py'
                   * A path (of type str) is provided, the docstring is saved to
                     that file.
                   * ``None``, the docstring is not saved (but the final 
                     doc string is still returned).
    :type target:  ``True``, ``None``, or str file path (default ``True``).

    :param add_autogen: If True adds boilerplate python version / timestamp
                        of current run to top of docstring.
    :type add_autogen:  ``True`` or ``False`` (default ``False``).

    :param ellipse_memids: Add ellipse for memory ids.
    :type ellipse_memids: ``True`` or ``False``

    :param ellipse_paths: Add ellipse for front path of path (up to final
                          relative path)
    :type ellipse_paths:  ``True`` or ``False``

    :param ellipse_traceback: Ellipse middle part of traceback.
    :type ellipse_traceback: True or False

    :param clean_blanklines: If ``True``, then railing blanklines in the src
                             which are converted to trailing '>>>' in the 
                             docstring are removed.  For example, this::
                             
                                 >>> print 'hi'
                                 'hi'
                                 >>>
                                 >>>
                             
                                 Now, another example. 
                             
                             is converted to::
                             
                                 >>> print 'hi'
                                 'hi'
                                 
                                 
                                 Now, another example. 
                             
    :type clean_blanklines:  ``True`` or ``False`` (default ``True``).

    :returns: The final docstring text.
    """
    convertor = Convertor(
            src=src,
            dst=dst,
            fns=fns,
            difftool=difftool,
            confirm=confirm,
            python_cmd=python_cmd,
            add_if_name_equals_main=add_if_name_equals_main,
            ellipse_memids=ellipse_memids,
            ellipse_paths=ellipse_paths,
            ellipse_tracebacks=ellipse_tracebacks,
            clean_blanklines=clean_blanklines)
    return convertor.convert()


class Convertor(object):

    def __init__(
        self, src=None, fns=None, dst=True, difftool=None,
        confirm=True, python_cmd='python', add_if_name_equals_main=True,
        ellipse_memids=True, ellipse_paths=True,
        ellipse_tracebacks=True, clean_blanklines=True):
        if src is None:
            self._src = src = _sys.argv[0]

        self._src = src
        self._difftool = difftool
        self._confirm = confirm
        self._dst = dst
        self._python_path = python_cmd
        self._add_if_name_equals_main = add_if_name_equals_main
        self._ellipse_memids = ellipse_memids
        self._ellipse_paths = ellipse_paths
        self._ellipse_tracebacks = ellipse_tracebacks
        self._clean_blanklines = clean_blanklines

    def convert(self):

        docstring = self.convert_src_to_docstring_text()

        dst_path = self.get_dst_path()

        if not dst_path:
            return docstring

        lock_path = _os.path.join(
            _os.path.dirname(dst_path),
            '.{}.mod2docstring.lock'.format(_os.path.basename(dst_path)))

        if _os.path.exists(lock_path):
            raise OSError(
                "Cannot create\n\n    {}\n\nbecause lock path:\n\n    {}"
                "\n\nexists.  Another instance of mod2docstring must be "
                "running.".format(dst_path, lock_path))
            
        try:
            with open(lock_path, 'w') as fileobj:
                fileobj.write('lock')

            difference = self.detect_output_difference(dst_path, docstring)

            if difference is False:
                _sys.stdout.write(
                    '\nDocstring not written, no diff found from '
                    '{}\n'.format(dst_path))
                return docstring

            if difference is True and self._difftool:
                self.launch_difftool(dst_path, docstring)

            if self._confirm:
                overwrite = self.confirm_write_docstring(dst_path)
            else:
                overwrite = True

            if overwrite:
                self.save_docstring(dst_path, docstring)

            return docstring

        finally:

            _os.unlink(lock_path)

    def convert_src_to_docstring_text(self):
        src_text = self.get_src_text(self._src)
        popen_object = self.get_popen_object(python_cmd=self._python_path)
        stdout, stderr = self.get_process_stdout_stderr(src_text, popen_object)
        docstring = self.convert_stdout_to_docstring(
            src_text,
            stdout,
            ellipse_memids=self._ellipse_memids,
            ellipse_paths=self._ellipse_paths,
            ellipse_tracebacks=self._ellipse_tracebacks,
            clean_blanklines=self._clean_blanklines)
        return docstring

    def get_src_text(self, src):
        src_text = self._load_src_text(self._src)
        src_text = self._remove_name_eq_main(src_text)
        src_text = self._fixup_whitespace(src_text)
        src_text = self._fixup_escape_shell_prompt(src_text)
        src_text = self._fixup_tabs(src_text)
        return src_text

    def _load_src_text(self, src):

        if not _os.path.isfile(src):
            raise EnvironmentError, "Cannot find src file {}".format(src)

        with open(src, 'r') as fileobj:
            src_text = open(src, 'r').read().strip()

        return src_text

    _re_name_eq_main = _re.compile(
        '^if\s*__name__\s*==\s*[\'"]__main__[\'"]:', _re.I)
    def _remove_name_eq_main(self, src_text):

        output_lines = []

        in_name_eq_main = False
        re_name_eq_main = self._re_name_eq_main
        for line in src_text.splitlines():
            if re_name_eq_main.match(line):
                in_name_eq_main = True
                continue
            elif in_name_eq_main and line and line.startswith((' ', '\t',)):
                continue
            else:
                in_name_eq_main = False
                output_lines.append(line)
        return '\n'.join(output_lines)






    _re_find_quote = _re.compile(r"((?:''')|(?:\"\"\"))((?:.|\n)*?)(\1)")
    def _fixup_whitespace(self, src_text):
        """\
        Fixes problems with spaces in the input that cause interpreter errors.
        
    
        There are two major problems and will use ^ to denote spaces
        Normally, a statement like::
    
            def fn():
    
            ^^^^print 'foobar'
    
        will not work if directly copied / pasted because there are no spaces 
        after the ``def fn():`` line.
    
        Also::
    
            def fn():
            ^^^^print 'hi'
            def fx():
            ^^^^print 'bye'
    
        does not allow direct copy paste either (you need a newline betwen the 
        fn calls). This will run fine within a module but **not** if pasted 
        into the interpreter. This function fixes these problem.
    
        The strategy is to collect all whitespace/comments and hold them in the
        ``hold`` list.  Then, track the current indent level.  When a non
        whitespace/comment line is encountered, apply the stored whitespace
        with the correct level of indentation.  Also, add a blank line between
        statements like those shown above.
    
        .. note::
    
           This function makes assumptions about the Python syntax as taken
           from http://docs.python.org/reference/compound_stmts.html
    
        """
        blocks = self._re_find_quote.split(src_text)
        for i, block in enumerate(blocks):
            if i % 4 == 0:
                blocks[i] = self._fixup_whitespace_block(block)
        return ''.join(blocks)

    def _fixup_whitespace_block(self, block):
        lines = []
        block = block.replace('\r', '')
        block = block.replace('\t', ' ' * 4)
        hold = []
        last_indent = 0
        stackable_tokens = set(['else', 'elif', 'except', 'finally'])
        for line in block.split('\n'):
            lstripped = line.lstrip()
            if not lstripped or lstripped.startswith('#'):
                # collect all blank lines or full comment lines
                hold.append(lstripped)
            else:
                new_indent = len(line) - len(lstripped)
                if lstripped.split()[0].split(':')[0] not in stackable_tokens:
                    # Add whitespace if, for example, two functions are defined
                    # with no whitespace in between
                    if not hold and new_indent < last_indent:
                        lines.append(' ' * new_indent)
                    last_indent = new_indent

                hold = ['%s%s' % (' ' * last_indent, h,) for h in hold]
                lines.extend(hold)
                hold = []

                lines.append(line.rstrip())

        lines.extend(hold)

        # For some reason, you need to have a statement at the end of the text
        # stream -- if you have a comment it raises an Exception
        lines.extend(['', 'raise SystemExit'])

        return '\n'.join(lines)

    def _fixup_escape_shell_prompt(self, src_text):
        """\
        Replaces `>>>` and '...' with escaped versions.  This is needed if
        these tokens actually appear in the output of a program (like, if
        you are testing mod2doctest itself using mod2doctest :)
        """
        src_text = src_text.replace('>>>', '\>>>')
        return src_text.replace('...', '\...')

    def _fixup_tabs(self, src_text):
        src_text = src_text.strip()
        src_text = src_text.replace('\r', '')
        src_text = src_text.replace('\t', '    ')
        return src_text

    def get_popen_object(self, python_cmd):
        popen_object = _subprocess.Popen(
            args="%s -i" % python_cmd,
            bufsize= -1,
            shell=True,
            stdin=_subprocess.PIPE,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.STDOUT,
            )
        return popen_object

    def get_process_stdout_stderr(self, src_text, popen_object):
        stdout, stderr = popen_object.communicate(src_text)
        return stdout, stderr

    def convert_stdout_to_docstring(
        self, src_text, stdout, ellipse_memids, ellipse_paths,
        ellipse_tracebacks, clean_blanklines):

        docstring = self._get_raw_docstring(
            src_text, stdout, ellipse_memids, ellipse_paths, ellipse_tracebacks)

        docstring = self._process_docstr_markers(docstring)

        if clean_blanklines:
            docstring = self._clean_docstr_blanklines(docstring)

        # Remove the boiler plate python startup header
        docstring = '\n'.join(docstring.splitlines()[4:])

        docstring = self._add_docstring_triple_quotes(docstring)

        if self._add_if_name_equals_main:
            name_equals_main = self.get_if_name_equals_main_block()
            docstring = '{}\n\n{}\n'.format(docstring, name_equals_main)

        return docstring

    def _get_raw_docstring(
        self, src_text, stdout, ellipse_memids, ellipse_paths,
        ellipse_tracebacks):

        src_lines = src_text.split('\n')

        stdout_lines = stdout.split('\n')

        docstr_lines = []

        intraceback = False
        startheader = True

        for stdout_line in stdout_lines:

            stdout_line = stdout_line.replace('\r', '')
            stdout_line = stdout_line.replace('\t', '    ')

            if ellipse_memids:
                stdout_line = self._add_memid_ellipse(stdout_line)

            if ellipse_paths:
                stdout_line = self._add_path_ellipse(stdout_line)

            for line in self._match_input_to_output(src_lines, stdout_line):
                docstr_lines.append(line)

        docstring = '\n'.join(docstr_lines)

        if self._ellipse_tracebacks:
            docstring = self._add_traceback_ellipses(docstring)

        return docstring


    _re_ellipse_memid = _re.compile(r'<(?:(?:\w+\.)*)(.*? at 0x)\w+>')
    def _add_memid_ellipse(self, line):
        return self._re_ellipse_memid.sub(r'<...\1...>', line)

    _re_path_chars = 'a-zA-Z0-9_[]{}:'
    _re_unix_local_path = _re.compile(
        r"(?:(?:[/][{0}/]+)+)([/][{0}/]+)".format(_re_path_chars))
    _re_windows_local_path = _re.compile(
        r"(?:\w:(?:[\\][{0}\\]+)+)([\\][{0}\\]+)".format(_re_path_chars))
    def _add_path_ellipse(self, line):
        line = self._re_unix_local_path.sub(r'...\1', line)
        line = self._re_windows_local_path.sub(r'...\1', line)
        return line

    _re_ellipse_traceback = _re.compile(
        r"""
        (\nTraceback\s\(most\srecent\scall\slast\):)
        (?:(?:\n[ |\t]+.*)*)
        (\n\w+.*)
        """, flags=_re.MULTILINE | _re.VERBOSE)
    def _add_traceback_ellipses(self, docstring):
        return self._re_ellipse_traceback.sub(r'\1\n    ...\2', docstring)

    def _match_input_to_output(self, input_lines, stdout_line):

        has_input = True

        while has_input:
            if stdout_line.startswith('>>> ') or stdout_line.startswith('... '):
                if input_lines:
                    yield "%s%s" % (stdout_line[0:4], input_lines.pop(0),)
                    stdout_line = stdout_line[4:]
                else:
                    yield ""
                    has_input = False
            else:
                yield stdout_line
                has_input = False

    def _process_docstr_markers(self, raw_docstring):

        processed_lines = []
        in_print = False

        for line in raw_docstring.split('\n'):
            line_no_space = line.strip().replace(' ', '')
            if line.startswith(('>>> ###', '... ###',)):
                continue
            elif line.startswith(('>>> ##', '... ##',)):
                if in_print is True:
                    in_print = False
                line = '%s%s' % (line[:4], line[5:],)
            elif line.startswith(('>>> #', '... #',)):
                if in_print is False:
                    processed_lines.append('')
                in_print = True
                line = line[6:]
            elif line.startswith(('>>> #', '... #',)):
                if in_print is False:
                    processed_lines.append('')
                in_print = True
                line = line[5:]
            elif line.startswith('>>> ') or line.startswith('... '):
                if in_print is True and line.strip() == '...':
                    line = ''
                elif in_print is True:
                    in_print = False
                    processed_lines.append(' ')
                    if line.startswith('...'):
                        line = '>>> %s' % line[4:]

            processed_lines.append(line)

        # The 'negative 3' is to remove the added raise SystemExit
        return '\n'.join(processed_lines[:-3])

    def get_if_name_equals_main_block(self):
        return (
            "\nif __name__ == '__main__':"
            "\n    import doctest"
            "\n    doctest.testmod("
            "\n        optionflags=doctest.ELLIPSIS |"
            "\n        doctest.REPORT_ONLY_FIRST_FAILURE |"
            "\n        doctest.NORMALIZE_WHITESPACE)"
            "\n")

    def _clean_docstr_blanklines(self, docstring):
        lines = []
        lastline = None
        enters = []
        for line in docstring.split('\n'):
            lastline = line
            if line.strip() == '>>>':
                enters.append(line)
                continue
            elif line.startswith('>>>') and enters:
                lines.extend(enters)
                del enters[:]
            elif enters:
                lines.extend([''] * len(enters))
                del enters[:]
            lines.append(line)
        return '\n'.join(lines)

    def _add_docstring_triple_quotes(self, docstring):
        docstring = docstring.replace("'''", '"""')
        docstring = "'''\n\n{}\n\n'''".format(docstring.strip())
        return docstring

    def get_dst_path(self):
        dst_path = self._dst
        if not dst_path:
            return None
        if dst_path is True:
            left, right = self._src.rsplit('.', 1)
            dst_path = '{}_doctest.{}'.format(left, right)
        if not isinstance(dst_path, basestring):
            raise TypeError(dst_path)
        return dst_path

    def detect_output_difference(self, dst_path, docstring):
        if not _os.path.isfile(dst_path):
            return None
        with open(dst_path, 'r') as fileobj:
            return fileobj.read() != docstring

    def launch_difftool(self, dst_path, docstring):
        difftool = self._difftool
        temp_path = '{}.temp'.format(dst_path)
        try:
            with open(temp_path, 'w') as fileobj:
                fileobj.write(docstring)
            _subprocess.call([difftool, dst_path, temp_path])
        finally:
            try:
                _os.unlink(temp_path)
            except EnvironmentError:
                pass

    def confirm_write_docstring(self, dst_path):
        _sys.stdout.write('\n')
        while True:
            dst_path = _os.path.basename(dst_path)
            yn = raw_input(
                "\nOverwrite new docstring '{}' [yN]: ".format(dst_path))
            yn = yn.strip().lower()
            if yn == 'y':
                return True
            elif yn == 'n':
                _sys.stdout.write('Docstring not written ...')
                return False

    def save_docstring(self, dst_path, docstring):
        with open(dst_path, 'w') as fileobj:
            fileobj.write(docstring)
        _sys.stdout.write('Docstring written to {}\n'.format(dst_path))



