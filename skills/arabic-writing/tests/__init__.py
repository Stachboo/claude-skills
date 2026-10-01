# Marks tests/ as a package so `python -m unittest discover -s tests -t .` works.
# Without it, discovery raises ImportError (with -s tests) or silently reports
# "Ran 0 tests" and exits 0 -- a false green that would hide real failures.
