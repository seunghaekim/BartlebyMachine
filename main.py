import os, pypandoc, json, yaml, re
from pypandoc.pandoc_download import download_pandoc

_MANUSCRIPT_DIR = os.path.join(os.getcwd(), 'manuscript')
_LATEX_DIR      = os.path.join(_MANUSCRIPT_DIR, 'tex')
os.makedirs(_LATEX_DIR, exist_ok=True)


class Config:
    config_file = 'config.yaml'
    template = None

    def __init__(self, config_file):
        config_file = os.path.join(os.getcwd(), config_file)
        config = self.readConfig()

        for key in config:
            if key == 'template':
                config[key] = os.path.join(os.getcwd(), 'BartlebyMachine', config[key]) + '.tex'
                f = open(config[key], mode='r', encoding='utf-8')
                template = f.read()
                f.close()
                config[key] = template

            setattr(self, key, config[key])


        return


    def readConfig(self):
        result = False

        try:
            with open(self.config_file, encoding='utf-8') as config:
                config = yaml.load(config)
        except:
            return False

        return config


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

    def contentConcat(self):
        concat = []
        for content in self.content:
            str = '\\\\begin{{{layout}}}\n{latex}\n\end{{{layout}}}'.format(latex=content.latex.replace('\\\r\n', '\\\\\r\n'), layout=content.layout);
            concat.append(str)

        return '\n'.join(concat)


class Bartleby:

    toc = None
    manuscripts = None
    overcite = None
    orphan = None
    config = None

    def __init__(self, Config):
        self.config = Config
        self.manuscripts = list(filter(
            lambda x: os.path.isdir(os.path.join(_MANUSCRIPT_DIR, x)) == False,
            os.listdir(_MANUSCRIPT_DIR)
        ))
        _LATEX_DIR = os.path.join(_MANUSCRIPT_DIR, 'tex')
        self.toc = [];


    def writeLatex(self):
        latex = self.replaceTemplate()
        f = open('ggded.tex', 'w', encoding='utf-8')
        f.write(latex)
        f.close()
        return


    def replaceTemplate(self):
        template = self.config.template
        book = []
        replaces = [
            (re.compile('<<content>>'), self.toc.contentConcat()),
            (re.compile('<<author>>'), self.toc.author),
            (re.compile('<<title>>'), self.toc.title),
            (re.compile('<<dateOfPublished>>'), self.toc.dateOfPublished),
        ]

        for replace in replaces:
            if replace[0].findall(template):
                template = replace[0].sub(replace[1], template)

        return template

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
