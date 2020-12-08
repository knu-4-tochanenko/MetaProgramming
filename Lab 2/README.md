# Metaprogramming. Java style and documentation fixer

# Requirements

Python: 3.4

# Install PyPI package

```
pip install javaccflab
```

# Help


usage: javaccflab [-h] [-p P] [-d D] [-f F] [-v] [-c]

JavaCCF is utility to fix style and documentation comments in Java files

optional arguments:
  -h, --help     show this help message and exit
  -p P           Path to Java project directory to verify or correct mistakes.
  -d D           Path to directory with Java files to verify or correct
                 mistakes.
  -f F           Path to Java file to verify or correct mistakes.
  -v, --verify   Verify code style and documentation comments
  -c, --correct  Correct styling mistakes in code and documentation comments
  
# Examples

```
python java_ccf.py -f 'C:\Users\Vlad\Java\MyClass.java' --verify
```

```
python java_ccf.py -p 'C:\Users\Vlad\Projects\MyProject' --correct
```

Using installed PyPI package:

```
javaccflab -f 'C:\Users\Vlad\Java\MyClass.java' --correct
```