import os
import docx
import pathlib
from argparse import ArgumentParser

import markdown2
from bs4 import BeautifulSoup
from markdown_pdf import MarkdownPdf, Section
from Markdown2docx import Markdown2docx, find_page_width, _read_in_markdown

class MarkdownConverter:
    _output_extension = None
    _output_prefix = ""
    _input_file_name = None

    def __init__(self, output_location: pathlib.Path):
        if not output_location.exists():
            output_location.mkdir(parents=True)
        self.output_location = output_location

    @property
    def output_extension(self) -> str:
        if self._output_extension is None:
            raise ValueError("Set _output_extension value")
        return self._output_extension
    
    @property
    def output_prefix(self) -> str:
        if self._output_prefix is None:
            return ""
        return self._output_prefix
    
    @property
    def input_file_name(self) -> str:
        if self._input_file_name:
            return self._input_file_name
        else:
            return ""

    @property
    def output_file_name(self) -> str:
        if self.input_file_name != "":
            name = self.input_file_name.split(".")[0]
        else:
            name = ""
        file_name = f"{self.output_prefix} - {name}{self.output_extension}"
        return os.path.join(os.getcwd(), self.output_location, file_name)

    def read_input_file(self, input_file) -> str:
        if not input_file.exists():
            raise FileNotFoundError(f"File {input_file} does not exist.")
        self._input_file_name = str(input_file)
        return input_file.read_text()

    def convert(self, input_file: pathlib.Path):
        raise NotImplementedError


class MarkdownToPdfConverter(MarkdownConverter):
    _output_extension = ".pdf"
    _title = None
    _author = None

    def convert(self, input_file: pathlib.Path):
        markdown = self.read_input_file(input_file)
        pdf = MarkdownPdf(toc_level=6)
        pdf.add_section(Section(markdown, paper_size="A4-L"))
        if self._title is not None:
            pdf.meta['title'] = self._title
        if self._author is not None:
            pdf.meta['author'] = self._author
        pdf.save(f"{self.output_file_name}")


class MarkdownToDocxConverter(MarkdownConverter):
    _output_extension = ".docx"

    class CustomMarkdown2docx(Markdown2docx):
        def __init__(self, input_file, output_file, markdown=None):
            self.infile = input_file_name
            self.outfile = output_file
            self.html_out_file = '.'.join([output_file, 'html'])
            self.project = input_file
            self.doc = docx.Document()
            self.page_width_inches = find_page_width(self.doc)
            # self.html = markdown.markdown(_read_in_markdown(self.infile), extensions=['tables'])
            if isinstance(markdown, list):
                self.markdown = '\n'.join(markdown)
            else:
                self.markdown = _read_in_markdown(self.infile)
            self.html = markdown2.markdown(self.markdown, extras=[
                'fenced-code-blocks',
                'code-friendly',
                'wiki-tables',
                'tables'
            ])
            self.soup = BeautifulSoup(self.html, 'html.parser')

    def convert(self, input_file: pathlib.Path):
        self._input_file_name = str(input_file)
        project = MarkdownToDocxConverter.CustomMarkdown2docx(input_file, self.output_file_name)
        project.infile = str(input_file)
        project.outfile = self.output_file_name
        project.eat_soup()
        project.save()


FORMAT_CONVERTER_MAPPINGS = {
    "pdf": [MarkdownToPdfConverter],
    "docx": [MarkdownToDocxConverter],
    "all": [MarkdownToPdfConverter, MarkdownToDocxConverter]
}


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                    help="Input file name", required=True)
    parser.add_argument("-o", "--dir", dest="output_directory",
                    help="Directory to store output in",
                    required=True)
    parser.add_argument("--format", dest="output_format",
                        choices=FORMAT_CONVERTER_MAPPINGS.keys(),
                        required=False, default="all")

    args = parser.parse_args()
    input_file_name = pathlib.Path(args.filename)
    output_directory = pathlib.Path(args.output_directory)
    output_format = args.output_format

    converters = FORMAT_CONVERTER_MAPPINGS[output_format]

    for converter_class in converters:
        converter = converter_class(output_directory)
        converter.convert(input_file_name)
        print(f"Converted {input_file_name} to {converter.output_file_name}")
    print("Done!")