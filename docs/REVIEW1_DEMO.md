# Review 1 demonstration (about 3 minutes)

1. Run `.\.venv\Scripts\python.exe app.py` from the project folder and open
   <http://127.0.0.1:5000>. Explain: “This is a controlled-English compiler. The
   accepted language is defined by a formal grammar.”
2. Use the preloaded five-line college-fest example. Select **Build page**.
   Point out the title, heading, paragraph, and blue **Register** button. The button
   is bold because of the fifth instruction; it does not submit anything.
3. Expand **Behind the page**, then **Build details**, then **Normalized Input** and **Tokens**. Show `Create` becoming `add`,
   original line numbers, and `STRING`, `ELEMENT`, `SIZE`, `COLOR`, and `BOLD` tokens.
   Quoted text is not lowercased.
4. Expand **Ast** and **Symbol Table**. The fifth statement has
   `reference: "it"` and `resolved_id: "element3"`. The corresponding button
   record has `font-weight: "bold"`. Explain that the last introduced eligible
   element is selected deterministically.
5. Expand **HTML** and **CSS** inside **Behind the page**, or open/download the files.
   The browser uses ordinary HTML and CSS. Save both files together if downloading.
6. Append `Paint the whole page rainbow.` on line 6 and compile again. Show the
   line 6 syntax error and absence of a preview for this attempt. No new output
   files were written. Independent malformed lines are collected; this is basic
   line-based handling, not full panic-mode recovery.
7. Remove the malformed line and compile again to restore the preview.

Optional reference-error example:

```text
Create a page titled "Reference Error".
Make it bold.
```

This reports line 2 because a page title is not a formatting target and no element
has been introduced.

Command-line fallback:

```powershell
.\.venv\Scripts\python.exe -m text2web examples\fest.sp --output build\fest --debug --force
Start-Process .\build\fest\index.html
.\.venv\Scripts\python.exe -m text2web examples\invalid.sp --output build\invalid
.\.venv\Scripts\python.exe -m pytest -q
```

The invalid example should exit with status 1 and report line 3. `build/invalid`
is not created by that failed compilation.

Explain progress accurately: “Stages 1–3 work for this small language. Stage 4 has
basic symbol-table reference resolution, and stage 8 produces static files.
Stages 5–7 still need layout constraints, substantive type/accessibility checks,
a page-tree IR, and optimization. The working subset is our Review 1 milestone;
we have not measured it as exactly 30% of the complete project.”
