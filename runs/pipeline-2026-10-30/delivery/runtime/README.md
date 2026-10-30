# Hybrid runtime pilot

Both LuaLaTeX and XeLaTeX compiled the bounded corpus with no missing glyphs. Every audit page contains one isolated math role; MuPDF inspected the rendered PDF font of its glyphs. The exact five PostScript names were separately checked with pdffonts. Default letters, figures, explicit alphabets, literal Unicode styled Latin, named operators and three math sizes passed. An unsupported gamma produced the required hard error on each engine.

The original commercial Storm files are external and hash-pinned. All PDFs, embedded-font diagnostics, logs and raster proofs are below ignored `private/`. See `summary.json` for actual role evidence and limitations. Passing this technical audit does not approve visual design or establish full AMS coverage.
