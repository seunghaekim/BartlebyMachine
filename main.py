import os, pypandoc, json, yaml
from pypandoc.pandoc_download import download_pandoc

_MANUSCRIPT_DIR = os.path.join(os.getcwd(), 'manuscript')
_LATEX_DIR      = os.path.join(_MANUSCRIPT_DIR, 'tex')
os.makedirs(_LATEX_DIR, exist_ok=True)

class Content:
    title = ''
    layout = ''
    filename = ''
    latex = ''

    def __init__(self, content):
        for key in content:
            try:
                setattr(self, key, content[key])
            except:
                print(key)

        self.latex = self.convertLatex()
        return


    def convertLatex(self):
        filepath = os.path.join(_MANUSCRIPT_DIR, self.filename+'.md')
        return pypandoc.convert_file( filepath, 'latex', extra_args=[
                '--data-dir='+os.path.join(os.getcwd(), 'BartlebyMachine', '.pandoc'),
                '--wrap=none',
                '--variable',
                'documentclass=book',
        ])

    def writeLatex(self):
        output_path = os.path.join(_MANUSCRIPT_DIR, 'tex', self.filename) + '.tex';

        f = open(output_path, 'w', encoding='utf-8')
        f.write(self.latex)
        f.close()

        print('%s converted tex file written'%self.filename)


class TableOfContent:

    title = ''
    author = ''
    dateOfPublished = ''
    content = []

    def __init__(self, toc):
        self.title = toc['title']
        self.author = toc['author']
        self.dateOfPublished = toc['dateOfPublished']

        for content in toc['content']:
             self.content.append(Content(content))


class Bartleby:

    toc = None
    manuscripts = None
    overcite = None
    orphan = None

    def __init__(self):
        self.manuscripts = list(filter(
            lambda x: os.path.isdir(os.path.join(_MANUSCRIPT_DIR, x)) == False,
            os.listdir(_MANUSCRIPT_DIR)
        ))
        _LATEX_DIR = os.path.join(_MANUSCRIPT_DIR, 'tex')
        self.toc = [];


    def markdownToLatex(self):
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
            toc = yaml.load(toc_file)
            result = True

        self.toc = TableOfContent(toc)

        return result

    def manuscriptCount(self):
        result = False
        cite = {}
        entries = []
        if self.toc == None:
            return result

        for toc in self.toc:
            for entry in toc.content:
                entries.append(entry.filename)

        for script in self.manuscripts:
            needle = script.split('.')[0]
            cite[needle] = entries.count(needle)

        return cite


    def manuscriptStatus(self):
        self.orphan = []
        self.overcite = []

        for script in self.manuscripts:
            cnt = list(
                map(lambda x: '%s.md'%x.filename, self.toc.content)
            ).count(script)
            if(cnt < 1):
                self.orphan.append(script)
            if(cnt > 1):
                self.overcite.append(script)

        return True
