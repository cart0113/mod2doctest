set HOME=C:\Users\Owner
rd /S /Q C:\eclipse\workspace\HG_MOD2DOCTEST\doc\build\doctrees
rd /S /Q C:\eclipse\workspace\HG_MOD2DOCTEST\doc\build\html

rem LOCAL DOCS
rem C:\Python26\scripts\sphinx-build.exe -b html C:\eclipse\workspace\HG_MOD2DOCTEST\doc\source C:\eclipse\workspace\HG_MOD2DOCTEST\doc\build\html

rem UPLOAD DOCS
rem cd C:\eclipse\workspace\HG_MOD2DOCTEST
rem C:\Python26\python.exe setup.py build_sphinx
rem C:\Python26\python.exe setup.py upload_sphinx
pause