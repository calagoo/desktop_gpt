import re

example_line = """# Here is a test section
**bold text**
*italicized text*
***bold and italicized text***
### Header 3
## Header 2

**_bold and italicized text_**
__*bold and italicized text*__
___bold and italicized text___

** bold text ** : *italicized text*

~~Strikethrough~~
<u>Underline</u>

--- 

Link: [Google](https://www.google.com)



## Testing python syntax highlighting
```python
import os
len("text")
# Test Comment "Hello!"
def test_function():
    '''This is a 
    test function def'''
    print("Hello, World!") # Prints Hello, World! def
    if True:
        return
```

"# Fake Header"
'# Another Fake Header'
"""

ex_2 = """# This is a H1 header

## This is a H2 header

**This is bold text**

*This is italicized text*

***This is both bold and italicized text***

Here is some inline code: `print("Hello, World!")`"""

def syntax(text):
    """Converts text to html with syntax highlighting"""
    code_block = {"started": False, "start": 0, "end": 0}

    split_text = text.split("\n")
    markdown = ""

    ix = 0
    while True:
        line = split_text[ix]

        if line.startswith("```") and code_block["started"]:
            code_block["end"] = ix+1
            code_markdown = code_syntax(split_text[code_block["start"]:code_block["end"]])
            code_block = {"started": False, "start": 0, "end": 0}
            markdown += code_markdown

        if line.startswith("```python"):
            code_block = {"started": True, "start": ix, "end": 0}

        if code_block["started"]:
            ix += 1
            continue

        if line.startswith("```"):
            ix += 1
            continue

        # Check Bold and Italics
        bld_italics = ["***", "___", "**_", "__*"] # All different types of bold and italics
        for bld in bld_italics:
            bld2 = bld
            if bld == "**_" or bld == "__*": # Then they are asymmetrical
                bld2 = bld[::-1]
            if bld in line and bld2 in line:
                line = line.replace(bld, "<strong><em>", 1)
                line = line.replace(bld2, "</em></strong>", 1)

        # Check Bold
        if "**" in line:
            line = line.replace("**", "<strong>", 1)
            line = line.replace("**", "</strong>", 1)

        # Check Italics
        if "*" in line:
            line = line.replace("*", "<em>", 1)
            line = line.replace("*", "</em>", 1)

        # Check Headers
        if line.startswith("###"):
            line = f"<h3>{line[4:]}</h3>"
        if line.startswith("##"):
            line = f"<h2>{line[3:]}</h2>"
        if line.startswith("#"):
            line = f"<h1>{line[2:]}</h1>"

        # Check Strikethrough
        if "~~" in line:
            line = line.replace("~~", "<s>", 1)
            line = line.replace("~~", "</s>", 1)

        # Check Underline
        if "<u>" in line:
            line = line.replace("<u>", "<u>", 1)
            line = line.replace("</u>", "</u>", 1)
        
        # Check Links (No hyperlink, just a hyperlink looking www link)
        # Example: [Google](https://www.google.com)
        # should be https://www.google.com
        hyperlink_regex = r'\[.*?\]\((https?:\/\/[^\)]+)\)'
        match = re.search(hyperlink_regex, line)
        if match:
            line = "<a href='" + match.group(1) + "'>" + match.group(1) + "</a>"

        # Check horizontal rule
        if line.startswith("---"):
            line = "<hr>"

        markdown += line + "<br>"

        ix += 1
        if ix >= len(split_text):
            break
    return markdown[:-4] # Remove the last <br> tag

def code_syntax(block):
    """Syntax highlighting for code block into html"""

    # Things to check for:
    #- Comments
    #- Functions
    #- Strings
    #- Multiline Strings
    #- Comments in strings / strings in comments
    #- Comments after code

    if block[0].startswith("```"):
        block = block[1:]
    if block[-1].startswith("```"):
        block = block[:-1]

    jblk = "\n".join(block)
    jblk += "\n"

    # print(jblk)

    in_comment = False
    in_string = False
    in_multiline_string = False
    in_function = False
    init_search_ix = 0
    search_ix = 0

    markdown = '<pre style="background-color: #2b2b2b; color: #f8f8f2; padding: 10px; border-radius: 5px;"><code>'
    
    ix = 0
    while True:
        if jblk[ix] == "#": ## Comment
            in_comment = True
            # Make text green to start
            markdown += "<span style='color:green;'>"

        if (jblk[ix] == "'" or jblk[ix] == '"') and not in_comment:
            quote_type = "'" if jblk[ix] == "'" else '"'
            # Checking if multiline delimiter
            char2 = jblk[ix+1]
            char3 = jblk[ix+2]
            if char2 == jblk[ix] and char3 == jblk[ix]: ## Multiline string
                ix += 3
                in_multiline_string = not in_multiline_string
                if in_multiline_string:
                    # Make text green to start
                    markdown += f"<span style='color:orange;'>{quote_type*3}"
                else:
                    # Close the span tag
                    markdown += f"{quote_type*3}</span>"
            else: ## Single line string
                in_string = not in_string 
                if in_string:
                    # Make text orange to start
                    markdown += "<span style='color:orange;'>"
                else:
                    # Close the span tag
                    markdown += f"{quote_type}</span>"
                    ix+=1

        # Highlighting functions
        # Use forward search to find parentheses, unless new line or empty space
        if (jblk[ix].isalpha() or jblk[ix] == "(") and not in_comment and not in_string and not in_multiline_string:        
            # print(jblk[ix],end="")
            if in_function:
                if ix >= search_ix:
                    in_function = False
                    markdown += "<span style='color:lightblue;'>" + jblk[init_search_ix:search_ix] + "</span>"
                    search_ix = ix
                    init_search_ix = ix
            else:
                init_search_ix = ix
            # search for parentheses
            search_ix = ix
            while jblk[search_ix] != "(":
                search_ix += 1
                if jblk[search_ix] == "\n":
                    # search_ix = ix
                    break
                if jblk[search_ix] == " ":
                    # search_ix = ix
                    break
                if search_ix >= len(jblk):
                    # search_ix = ix
                    break
            if jblk[search_ix] == "(" and ix < search_ix:
                in_function = True

        ## Highlighting keywords (def, while, if, else, etc.)
        if jblk[ix].isalpha() and not in_comment and not in_string and not in_multiline_string and not in_function:
            word = ""
            while jblk[ix].isalpha():
                word += jblk[ix]
                ix += 1
                if ix >= len(jblk):
                    break

            keywords_blue = ["def", "True", "False", "not", "in", "is", "and", "or", "None", "class", "lambda"]
            keywords_purple = ["if", "else", "return", "break", "import", "while", "for", "from", "with", "from", "global", "del", "yield", "try", "except", "finally", "raise", "assert", "pass", "continue", "async", "await"]
            if word in keywords_blue:
                markdown += "<span style='color:blue;'>"
                markdown += word
                markdown += "</span>"

            if word in keywords_purple:
                markdown += "<span style='color:magenta;'>"
                markdown += word
                markdown += "</span>"

            if word not in keywords_blue and word not in keywords_purple:
                markdown += word
                # ix -= count_ix

        # Adding newline
        if jblk[ix] == "\n":
            if in_comment:
                in_comment = False
                markdown += "</span>"

            in_string = False

        if in_multiline_string:
            markdown += jblk[ix]

        if in_string:
            markdown += jblk[ix]

        if in_comment:
            markdown += jblk[ix]
        
        if not in_comment and not in_string and not in_multiline_string and not in_function:
            markdown += jblk[ix]

        ix += 1
        if ix >= len(jblk):
            break
    
    markdown += "</code></pre>"
    return markdown

def main():
    x = syntax(example_line)
    print(x)

if __name__ == "__main__":
    main()