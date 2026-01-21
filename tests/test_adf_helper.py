"""Tests for adf_helper module."""

import pytest

from confluence_as import (
    adf_to_markdown,
    adf_to_text,
    create_adf_doc,
    create_blockquote,
    create_bullet_list,
    create_code_block,
    create_heading,
    create_link,
    create_ordered_list,
    create_paragraph,
    create_rule,
    create_table,
    create_text,
    markdown_to_adf,
    text_to_adf,
    validate_adf,
)


class TestCreateAdfDoc:
    """Tests for create_adf_doc."""

    def test_creates_doc_structure(self):
        content = [create_paragraph(text="Hello")]
        doc = create_adf_doc(content)

        assert doc["type"] == "doc"
        assert doc["version"] == 1
        assert len(doc["content"]) == 1

    def test_empty_content(self):
        doc = create_adf_doc([])
        assert doc["content"] == []


class TestCreateParagraph:
    """Tests for create_paragraph."""

    def test_with_text(self):
        para = create_paragraph(text="Hello, World!")
        assert para["type"] == "paragraph"
        assert len(para["content"]) == 1
        assert para["content"][0]["text"] == "Hello, World!"

    def test_with_content(self):
        content = [create_text("Bold", marks=[{"type": "strong"}])]
        para = create_paragraph(content=content)
        assert para["content"][0]["marks"][0]["type"] == "strong"


class TestCreateText:
    """Tests for create_text."""

    def test_simple_text(self):
        text = create_text("Hello")
        assert text["type"] == "text"
        assert text["text"] == "Hello"
        assert "marks" not in text

    def test_with_marks(self):
        text = create_text("Bold", marks=[{"type": "strong"}])
        assert text["marks"][0]["type"] == "strong"


class TestCreateHeading:
    """Tests for create_heading."""

    def test_heading_level_1(self):
        heading = create_heading("Title", level=1)
        assert heading["type"] == "heading"
        assert heading["attrs"]["level"] == 1
        assert heading["content"][0]["text"] == "Title"

    def test_clamps_level(self):
        heading = create_heading("Title", level=10)
        assert heading["attrs"]["level"] == 6

        heading = create_heading("Title", level=0)
        assert heading["attrs"]["level"] == 1


class TestCreateLists:
    """Tests for list creation functions."""

    def test_bullet_list(self):
        items = ["Item 1", "Item 2", "Item 3"]
        bullet_list = create_bullet_list(items)

        assert bullet_list["type"] == "bulletList"
        assert len(bullet_list["content"]) == 3
        assert bullet_list["content"][0]["type"] == "listItem"

    def test_ordered_list(self):
        items = ["First", "Second"]
        ordered_list = create_ordered_list(items)

        assert ordered_list["type"] == "orderedList"
        assert ordered_list["attrs"]["order"] == 1

    def test_ordered_list_custom_start(self):
        ordered_list = create_ordered_list(["Item"], start=5)
        assert ordered_list["attrs"]["order"] == 5


class TestCreateCodeBlock:
    """Tests for create_code_block."""

    def test_without_language(self):
        code = create_code_block("print('hello')")
        assert code["type"] == "codeBlock"
        assert "attrs" not in code

    def test_with_language(self):
        code = create_code_block("print('hello')", language="python")
        assert code["attrs"]["language"] == "python"


class TestCreateBlockquote:
    """Tests for create_blockquote."""

    def test_creates_blockquote(self):
        quote = create_blockquote("Quote text")
        assert quote["type"] == "blockquote"
        assert quote["content"][0]["type"] == "paragraph"


class TestCreateRule:
    """Tests for create_rule."""

    def test_creates_rule(self):
        rule = create_rule()
        assert rule["type"] == "rule"


class TestCreateTable:
    """Tests for create_table."""

    def test_table_with_header(self):
        rows = [["Header 1", "Header 2"], ["Value 1", "Value 2"]]
        table = create_table(rows, header=True)

        assert table["type"] == "table"
        assert table["content"][0]["content"][0]["type"] == "tableHeader"
        assert table["content"][1]["content"][0]["type"] == "tableCell"

    def test_table_without_header(self):
        rows = [["A", "B"], ["C", "D"]]
        table = create_table(rows, header=False)

        assert table["content"][0]["content"][0]["type"] == "tableCell"


class TestCreateLink:
    """Tests for create_link."""

    def test_creates_link(self):
        link = create_link("Click here", "https://example.com")
        assert link["text"] == "Click here"
        assert link["marks"][0]["type"] == "link"
        assert link["marks"][0]["attrs"]["href"] == "https://example.com"


class TestTextToAdf:
    """Tests for text_to_adf."""

    def test_simple_text(self):
        adf = text_to_adf("Hello, World!")
        assert adf["type"] == "doc"
        assert adf["content"][0]["content"][0]["text"] == "Hello, World!"

    def test_paragraphs(self):
        adf = text_to_adf("Para 1\n\nPara 2")
        assert len(adf["content"]) == 2

    def test_empty_text(self):
        adf = text_to_adf("")
        assert adf["type"] == "doc"


class TestMarkdownToAdf:
    """Tests for markdown_to_adf."""

    def test_heading(self):
        adf = markdown_to_adf("# Title")
        assert adf["content"][0]["type"] == "heading"
        assert adf["content"][0]["attrs"]["level"] == 1

    def test_bold(self):
        adf = markdown_to_adf("This is **bold** text")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "strong"
            for node in content
            if "marks" in node
        )

    def test_bullet_list(self):
        adf = markdown_to_adf("- Item 1\n- Item 2")
        assert adf["content"][0]["type"] == "bulletList"

    def test_code_block(self):
        adf = markdown_to_adf("```python\nprint('hello')\n```")
        assert adf["content"][0]["type"] == "codeBlock"
        assert adf["content"][0]["attrs"]["language"] == "python"

    def test_horizontal_rule(self):
        adf = markdown_to_adf("---")
        assert adf["content"][0]["type"] == "rule"


class TestAdfToText:
    """Tests for adf_to_text."""

    def test_simple_paragraph(self):
        adf = create_adf_doc([create_paragraph(text="Hello")])
        assert adf_to_text(adf) == "Hello"

    def test_multiple_paragraphs(self):
        adf = create_adf_doc(
            [
                create_paragraph(text="Para 1"),
                create_paragraph(text="Para 2"),
            ]
        )
        text = adf_to_text(adf)
        assert "Para 1" in text
        assert "Para 2" in text

    def test_empty_adf(self):
        assert adf_to_text({}) == ""
        assert adf_to_text(None) == ""


class TestAdfToMarkdown:
    """Tests for adf_to_markdown."""

    def test_heading(self):
        adf = create_adf_doc([create_heading("Title", level=2)])
        md = adf_to_markdown(adf)
        assert md == "## Title"

    def test_bullet_list(self):
        adf = create_adf_doc([create_bullet_list(["Item 1", "Item 2"])])
        md = adf_to_markdown(adf)
        assert "- Item 1" in md
        assert "- Item 2" in md

    def test_code_block(self):
        adf = create_adf_doc([create_code_block("code", language="python")])
        md = adf_to_markdown(adf)
        assert "```python" in md
        assert "code" in md


class TestValidateAdf:
    """Tests for validate_adf."""

    def test_valid_adf(self):
        adf = create_adf_doc([create_paragraph(text="Hello")])
        assert validate_adf(adf) is True

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            validate_adf("not a dict")

    def test_missing_doc_type(self):
        with pytest.raises(ValueError):
            validate_adf({"type": "paragraph", "content": []})

    def test_missing_content(self):
        with pytest.raises(ValueError):
            validate_adf({"type": "doc"})

    def test_content_not_list(self):
        with pytest.raises(ValueError, match="content must be a list"):
            validate_adf({"type": "doc", "content": "not a list"})


class TestCreateParagraphEdgeCases:
    """Additional tests for create_paragraph edge cases."""

    def test_no_text_no_content(self):
        """Paragraph with neither text nor content creates empty paragraph."""
        para = create_paragraph()
        assert para["type"] == "paragraph"
        assert para["content"] == []


class TestMarkdownToAdfExtended:
    """Extended tests for markdown_to_adf covering more cases."""

    def test_empty_markdown(self):
        """Empty markdown returns empty paragraph."""
        adf = markdown_to_adf("")
        assert adf["type"] == "doc"
        assert len(adf["content"]) == 1
        assert adf["content"][0]["type"] == "paragraph"

    def test_blockquote(self):
        """Blockquote is converted correctly."""
        adf = markdown_to_adf("> This is a quote")
        assert adf["content"][0]["type"] == "blockquote"

    def test_ordered_list(self):
        """Ordered list is converted correctly."""
        adf = markdown_to_adf("1. First\n2. Second")
        assert adf["content"][0]["type"] == "orderedList"

    def test_italic_asterisk(self):
        """Italic with asterisk is parsed."""
        adf = markdown_to_adf("This is *italic* text")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "em"
            for node in content
            if "marks" in node
        )

    def test_italic_underscore(self):
        """Italic with underscore is parsed."""
        adf = markdown_to_adf("This is _italic_ text")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "em"
            for node in content
            if "marks" in node
        )

    def test_bold_underscore(self):
        """Bold with underscore is parsed."""
        adf = markdown_to_adf("This is __bold__ text")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "strong"
            for node in content
            if "marks" in node
        )

    def test_inline_code(self):
        """Inline code is parsed."""
        adf = markdown_to_adf("Use `code` here")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "code"
            for node in content
            if "marks" in node
        )

    def test_link(self):
        """Links are parsed."""
        adf = markdown_to_adf("Click [here](https://example.com) now")
        content = adf["content"][0]["content"]
        assert any(
            node.get("marks", [{}])[0].get("type") == "link"
            for node in content
            if "marks" in node
        )


class TestAdfToTextExtended:
    """Extended tests for adf_to_text covering more node types."""

    def test_heading(self):
        """Heading is converted to text."""
        adf = create_adf_doc([create_heading("Title", level=2)])
        text = adf_to_text(adf)
        assert "Title" in text

    def test_bullet_list(self):
        """Bullet list is converted to text."""
        adf = create_adf_doc([create_bullet_list(["Item 1", "Item 2"])])
        text = adf_to_text(adf)
        assert "- Item 1" in text
        assert "- Item 2" in text

    def test_ordered_list(self):
        """Ordered list is converted to text."""
        adf = create_adf_doc([create_ordered_list(["First", "Second"])])
        text = adf_to_text(adf)
        assert "- First" in text
        assert "- Second" in text

    def test_code_block(self):
        """Code block is converted to text."""
        adf = create_adf_doc([create_code_block("print('hello')", language="python")])
        text = adf_to_text(adf)
        assert "print('hello')" in text

    def test_blockquote(self):
        """Blockquote is converted to text."""
        adf = create_adf_doc([create_blockquote("Quote text")])
        text = adf_to_text(adf)
        assert "> Quote text" in text

    def test_table(self):
        """Table is converted to text."""
        adf = create_adf_doc([create_table([["A", "B"], ["C", "D"]])])
        text = adf_to_text(adf)
        assert "A" in text
        assert "B" in text

    def test_horizontal_rule(self):
        """Horizontal rule node exists but returns empty (no text content)."""
        adf = create_adf_doc([create_rule()])
        text = adf_to_text(adf)
        # Rule nodes have no text content, so they return empty
        assert text == ""

    def test_hard_break(self):
        """Hard break node is handled."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 1"},
                        {"type": "hardBreak"},
                        {"type": "text", "text": "Line 2"},
                    ],
                }
            ],
        }
        text = adf_to_text(adf)
        assert "Line 1" in text
        assert "Line 2" in text


class TestAdfToMarkdownExtended:
    """Extended tests for adf_to_markdown covering more cases."""

    def test_empty_adf(self):
        """Empty ADF returns empty string."""
        assert adf_to_markdown({}) == ""
        assert adf_to_markdown(None) == ""

    def test_italic_mark(self):
        """Italic mark is converted to markdown."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "italic", "marks": [{"type": "em"}]}
                    ],
                }
            ],
        }
        md = adf_to_markdown(adf)
        assert "*italic*" in md

    def test_code_mark(self):
        """Code mark is converted to markdown."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "code", "marks": [{"type": "code"}]}
                    ],
                }
            ],
        }
        md = adf_to_markdown(adf)
        assert "`code`" in md

    def test_link_mark(self):
        """Link mark is converted to markdown."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "click",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {"href": "https://example.com"},
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        md = adf_to_markdown(adf)
        assert "[click](https://example.com)" in md

    def test_strike_mark(self):
        """Strikethrough mark is converted to markdown."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "deleted",
                            "marks": [{"type": "strike"}],
                        }
                    ],
                }
            ],
        }
        md = adf_to_markdown(adf)
        assert "~~deleted~~" in md

    def test_ordered_list(self):
        """Ordered list is converted to markdown."""
        adf = create_adf_doc([create_ordered_list(["First", "Second"], start=1)])
        md = adf_to_markdown(adf)
        assert "1. First" in md
        assert "2. Second" in md

    def test_ordered_list_custom_start(self):
        """Ordered list with custom start is converted correctly."""
        adf = create_adf_doc([create_ordered_list(["Item"], start=5)])
        md = adf_to_markdown(adf)
        assert "5. Item" in md

    def test_blockquote(self):
        """Blockquote is converted to markdown."""
        adf = create_adf_doc([create_blockquote("Quote text")])
        md = adf_to_markdown(adf)
        assert "> Quote text" in md

    def test_horizontal_rule(self):
        """Horizontal rule is converted to markdown."""
        adf = create_adf_doc([create_rule()])
        md = adf_to_markdown(adf)
        assert "---" in md

    def test_table(self):
        """Table is converted to markdown."""
        adf = create_adf_doc([create_table([["H1", "H2"], ["V1", "V2"]])])
        md = adf_to_markdown(adf)
        assert "| H1 | H2 |" in md
        assert "| --- | --- |" in md
        assert "| V1 | V2 |" in md

    def test_hard_break(self):
        """Hard break is converted to markdown line break."""
        adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Line 1"},
                        {"type": "hardBreak"},
                        {"type": "text", "text": "Line 2"},
                    ],
                }
            ],
        }
        md = adf_to_markdown(adf)
        assert "Line 1" in md
        assert "Line 2" in md
