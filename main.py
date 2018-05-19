import os, pypandoc, json
from pypandoc.pandoc_download import download_pandoc

_MANUSCRIPT_DIR = os.path.join(os.getcwd(), 'manuscript')
_LATEX_DIR      = os.path.join(_MANUSCRIPT_DIR, 'latex')
os.makedirs(_LATEX_DIR, exist_ok=True)

class Content:
    title = ''
    layout = ''
    filename = ''
    latex = ''

    def __init__(self, content):
      self.title = content['title']
      self.layout = content['layout']
      self.filename = content['filename']
      self.latex = self.convertLatex()


    def convertLatex(self):
        filepath = os.path.join(_MANUSCRIPT_DIR, self.filename+'.md')
        return pypandoc.convert_file( filepath, 'latex', extra_args=[
                '--data-dir='+os.path.join(os.getcwd(), 'BartlebyMachine', '.pandoc'),
                '--wrap=none',
                '--variable',
                'documentclass=book',
        ])

    def writeLatex(self):
        output_path = os.path.join(_MANUSCRIPT_DIR, 'latex', self.filename) + '.tex';

        f = open(output_path, 'w', encoding='utf-8')
        f.write(self.latex)
        f.close()

        print('{filename} converted tex file written'.format(filename=self.filename))


class TableOfContent:

    title = ''
    author = ''
    date = ''
    content = []

    def __init__(self, toc):
        self.title = toc['title']
        self.author = toc['author']
        self.date = toc['date']

        for content in toc['content']:
             self.content.append(Content(content))


class Bartleby:

    def __init__(self):
        self.manuscripts = list(filter(
            lambda x: os.path.isdir(os.path.join(_MANUSCRIPT_DIR, x)) == False,
            os.listdir(_MANUSCRIPT_DIR)
        ))
        _LATEX_DIR = os.path.join(_MANUSCRIPT_DIR, 'latex')
        self.toc = [];


    def markdowntolatex(self):
        result = False

        for content in self.toc.content:
            content.writeLatex()

        return result


    def addTableOfContent(self, filename):
        result = False
        file = os.path.join(os.getcwd(), filename)

        if os.path.exists(file) == False:
            return result

        with open(file, encoding='utf-8') as toc_file:
            toc = json.load(toc_file)
            result = True

        self.toc = TableOfContent(toc)

        return result


    def manuscriptCount(self):
        result = False
        cite = {}
        entries = []
        if len(self.toc) < 1:
            return result

        for toc in self.toc:
            for entry in toc.content:
                entries.append(entry.filename)

        for script in self.manuscripts:
            needle = script.split('.')[0]
            cite[needle] = entries.count(needle)

        return cite


    def findOrphan(self):
        cite = self.manuscriptCount();
        return list(filter(lambda x: cite[x] < 1, cite.keys()))


    def findOverCite(self):
        cite = self.manuscriptCount();
        return list(filter(lambda x: cite[x] > 1, cite.keys()))
