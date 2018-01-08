# Visconde, a literate cob :corn:

Literate programming is great, right?

This is a toy program for playing with literate programming.

- `visconde.py` is a simple tangler (written in python 3)
- `visconde.lt` is the literate source for `visconde.py`

Run `python3 visconde.py your-source-file-here` to compile generate
extract the non-literate code from the literate source `your-source-file`.

As it is, the tangler is language-agnostic. 

## Basic usage

Code appears between fenced lines (like in GitHub flavoured Markdown);
each code chunk is named (their name appears after the fence, on the same line)
fences may have three or more backticks, 
(so long as open- and close-fence have the same number of them).
Write `@{fla fli flow}` on a line of its own to refer to chunk
named `fla fli flow`. 

    This line is text. It is just ignored.
    More text, ignored as well.
    
    - and this is, too;
    - so is this;
    - getting bored now.

    ``` foo-bar
    @{two}
        @{one}
    if True:
        @{two}
    @{one}
    ```
    
    You may or may not have text between chunks.
    
    `````` one
    --1--
    --1-- ends here
    ``````
    
    ``` two
    --2-- 
        @{three}
    --2-- ends here
    ```

    ``` three
    --3--
    ```

    ``` foo-bar-2
    Another file.
    ```
    
When tangled, generates two files. 

File `foo-bar` contains the lines

    --2--
        --3--
    --2-- ends here
        --1--
        --1-- ends here
    if True:
        --2--
            --3--
        --2-- ends here
    --1--
    --1-- ends here
        
and file `foo-bar-2` contains the lines

    Another file.


## Todo

- Warnings
  - [ ] file ends before code chunk does
  - [ ] circular chunk dependencies
  - [ ] multiple root files are found (only generate multiple output
    files if a flag is set)
- Flags
  - [ ] generate a file for each root chunk
  - [ ] flag for dry-run (just warnigs, no output)
  - [ ] generate file with expansion of chunk (let user specify filename)
- [ ] weave!

## Nice to have

- [ ] changefiles?

## Known bugs

Please let us know!

## Thanks

[Knuth](http://www-cs-faculty.stanford.edu/~knuth/), [Zachary Yedidia](https://github.com/zyedidia), [José Augusto](http://www.ime.usp.br/~jose/).

## Apology

I'm sorry.

## License

Copyright (c) 2018: Tássio Naia. GPL version 3.0 or later. See LICENSE for details.

## Keywords

Visconde de Sabugosa, literate cob, literate toy.

