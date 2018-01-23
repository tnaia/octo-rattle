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

An example.

    This line is text. It is just ignored.
    More text, ignored as well.
    
    - and this is, too;
    - so is this;
    - getting bored now.
    
    The fenced block below is a **code chunk**. Most lines reference
    other chunks, whose text is to be inserted in the place where the
    reference lies.

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
    
Tangling the above generates two files. File `foo-bar` contains the lines

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
        
and file `foo-bar-2` contains the line

    Another file.

For help and options run `python3 visconde.py -h`.

## Todo

- Features
  - [x] basic weave (assumes input is [GFM](https://help.github.com/articles/about-writing-and-formatting-on-github/) outputs markdown plus some html tags)
  - [x] weave: chunk cross-references
  - [x] weave: dumb word index (see next item)
  - [x] process fenced blocks having a language spec on the open-fence line (not default action, but controllable by command line option)
  - [ ] weave: allow references to chunks from the text
  - [ ] identify first appearance of word/identifier
  - [ ] better weaving backend (incorporate markdown parser, be smart about which language is used)
  - [ ] section-awareness (e.g: table of contents word index also over code in text sections
  - [ ] option to set language for all fenced blocks

- Warnings
  - [x] generate a file for each root chunk
  - [x] if multiple root files are found, only generate multiple output
        files if a flag is set)
  - [ ] chunk without name
  - [ ] file ends before code chunk does
  - [ ] circular chunk dependencies
  - [ ] warn if distinct blocks of same code chunk have different languages
- Flags/arguments
  - [ ] flag for dry-run (just warnings, no output)
  - [ ] generate file with expansion of given chunk (let user specify filename)
- weave

## Nice to have

- [x] changefile!
- [ ] section index
## Known bugs

Please let us know!

- [ ] produce output even when there is no input file
- [ ] assumes markdown input when weaving (no flag to prevent this)
- [ ] code chunks in code. e.g.: `@{x}` on a line of its own in code chunk
- [ ] html tags in code chunks e.g., `</pre>` inside of code chunk

## Thanks

[Knuth](http://www-cs-faculty.stanford.edu/~knuth/), [Zachary Yedidia](https://github.com/zyedidia), [José Augusto](http://www.ime.usp.br/~jose/), [Monteiro Lobato](https://en.wikipedia.org/wiki/Monteiro_Lobato).

## Apology

I'm sorry.

## License

Copyright (c) 2018: Tássio Naia. GPL version 3.0 or later. See LICENSE for details.

## Keywords

Visconde de Sabugosa, literate cob, literate toy.

