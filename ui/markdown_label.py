# ui/markdown_label.py
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from markdown import markdown
import re

KV_CODE = """
<MarkdownLabel>:
    markup: True
    text_size: self.width, None
    valign: 'top'
"""

class MarkdownLabel(MDLabel):
    source_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Don't call _render_markdown() here - on_source_text will handle it

    def on_source_text(self, instance, value):
        self._render_markdown()

    def _render_markdown(self):
        if not self.source_text:
            self.text = ""
            return

        try:
            # Convert markdown to HTML
            html = markdown(self.source_text)

            # Convert HTML to Kivy markup
            kivy_markup = self._html_to_kivy_markup(html)
            self.text = kivy_markup
        except Exception as e:
            # Fallback to plain text if conversion fails
            self.text = self.source_text

    def _html_to_kivy_markup(self, html: str) -> str:
        """Simple HTML to Kivy markup conversion"""
        result = html

        # Handle line breaks first
        result = re.sub(r'<br\s*/?>', '\n', result)

        # Code blocks
        result = re.sub(r'<pre><code>(.*?)</code></pre>', r'[color=#2d2d2d][b]\1[/b][/color]', result, flags=re.DOTALL)

        # Inline code
        result = re.sub(r'<code>(.*?)</code>', r'[color=#2d2d2d][font=RobotoMono]\1[/font][/color]', result)

        # Bold
        result = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', result)

        # Italic
        result = re.sub(r'<em>(.*?)</em>', r'[i]\1[/i]', result)

        # Links
        result = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[ref=\1][color=#2196F3][u]\2[/u][/color][/ref]', result)

        # Remove other HTML tags
        result = re.sub(r'<[^>]+>', '', result)

        return result

Builder.load_string(KV_CODE)
