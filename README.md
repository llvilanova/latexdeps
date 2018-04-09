# latexdeps

*Latexdeps* can automatically produce missing files (identified in a TeX log
file) from other existing files.

This can be used, for example, to take a source file (e.g., SVG) and produce a
PDF file that will be included in your final document.  This way, you don't need
to worry about manually producing your figure files, ensuring they are always
up-to-date from their original source format.

For example, if you have a ``document.tex`` file that wants to include
``figure.svg`` in your final TeX document:

```latex
\begin{figure}
  \includegraphics[width=\columnwidth]{figure}
\end{figure}
```

You can first compile ``document.text``, generate its dependencies with
``latexdeps``, and finally recompile it to get the final document:

<pre>
pdflatex document.tex
latexdeps document.log
pdflatex document.tex
</pre>

Note that the ``includegraphics`` above does not specify the image's target
format, which will be PDF in this case since we're using ``pdflatex``.
