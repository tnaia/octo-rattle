# Changes to visconde

## v 0.1.4

- Create `CHANGELOG.md`
- Basic and buggy weave, dangerous!
- Arguments obtained via `argparse`.
- Flags:
  - `fencedwithlanguage`: visconde treats the (stripped) characters between the opening fence and the first space character as a language specification for the code block; the remaining (stripped) characters of the line are therefore the code chunk name. 
  - `manyoutputs` allow generation of multiple tangled files
  - `tangle` allow the generation of any (at all) tangled files
- Makefile! wrap weaved source into proper html syntax, add some css.

## v 0.1.3

- much better literate source
- warns of undefined chunk

## v 0.1.1

- basic tangling
