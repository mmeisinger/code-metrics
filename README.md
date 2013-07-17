code-metrics
============

Collects various kinds of code metrics for OOI repositories

OOI ION Release 1:
> python run-metrics.py

OOI ION Release 2:
> python run-metrics-r2.py

The script lists a number of git repositories to scan in the source code.
The repository directories are all expected within the parent directory of this script,
i.e. in ../<repo>

There are 2 flags in the code that toggle whether git pull should be called before counting,
and whether metrics should be calculated by committer name as well.

Caveats:
- The script only counts files in defined directories. If there are additional files on other,
  not listed directories, then these will not be counted
- The script applies a very simple method to eliminate empty and comment lines (by file type)
- The script cannot distinguish code copied from external sources and counts it as well
- The by name count also counts empty lines and comments. It uses git blame
- Committers that modify someone else's code (e.g. indent it one level) get credited with other code
- Committers that duplicate code or paste code from the web get credited with that code
- And of course SLOC is not a good metric for measuring software progress and quality
