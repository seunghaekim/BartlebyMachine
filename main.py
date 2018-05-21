import os, pypandoc, json, yaml, re
import datetime
from .config import Config
from pypandoc.pandoc_download import download_pandoc
from pylatex import Itemize, Enumerate, Description, NoEscape
from pylatex.utils import italic

class Cover:
    artist  = None
    title   = None
    year    = None
    medium  = None
    musium  = None
    location = None
    # Goya, Francisco. The Family of Charles IV. 1800, oil on canvas, Museo del Prado, Madrid.
    def __init__(self, cover):
        for dic in cover:
            key = list(dic.keys())[0]
            try:
                setattr(self, key, dic[key])
            except:
                print('error', key)

        return

    def exportCitation(self):
        firstname = self.artist.split(' ')[0]
        lastname = ' '.join(self.artist.split(' ')[1:])
        name = ', '.join([firstname, lastname])
        return '{name}. {title}, {year}, {medium}, {musium}, {location}'.format(
            name    = name,
            title   = '\\textit{%s}'%self.title,
            year    = self.year,
            medium  = self.medium,
            musium  = self.musium,
            location= self.location
        )


class Content:
    title   = None
    layout  = None
    latex   = None
    type    = 'mainmatter'
    filename = None

    def __init__(self, content):
        for key in content:
            try:
                setattr(self, key, content[key])
            except:
                print(key)

        self.latex = self.convertLatex()
        return


    def convertLatex(self):
        filepath = os.path.join(Config().manuscript_dir, self.filename+'.md')
        return pypandoc.convert_file( filepath, 'latex', extra_args=[
                '--data-dir='+os.path.join(os.getcwd(), 'BartlebyMachine', '.pandoc'),
                '--wrap=none',
                '--variable',
                'documentclass=book',
        ])

    def writeLatex(self):
        output_path = os.path.join(Config().manuscript_dir, 'tex', self.filename) + '.tex';

        f = open(output_path, 'w', encoding='utf-8')
        f.write(self.latex)
        f.close()


class TableOfContent:

    title = None
    author = None
    dateOfPublished = None
    cover = None
    content = []

    def __init__(self, toc):
        for key in toc:
            try:
                if(key == 'content'):
                    content = list(map(lambda x: Content(x), toc[key]))
                    toc[key] = content

                if(key == 'cover'):
                    toc[key] = Cover(toc[key])

                setattr(self, key, toc[key])

            except:
                print(key)


    def exportContent(self):
        concat = []
        for content in self.content:
            if content.type == 'mainmatter':
                str = '\\\\begin{{{layout}}}\n{latex}\n\end{{{layout}}}'.format(latex=content.latex.replace('\\\r\n', '\\\\\n'), layout=content.layout);
                concat.append(str)

        return '\n'.join(concat)


    def exportPreface(self):
        prefaces = list(filter(lambda x: x.type == 'preface', self.content))
        return '\n'.join(list(map(lambda x: x.latex, prefaces)))


    def exportEndpaper(self):
        item = Description()
        item.add_item('제목', self.title)
        item.add_item('저자', self.author)
        item.add_item('편집', '미루')
        item.add_item('디자인', '써드엔지니어링카르텔')
        item.add_item('표지', NoEscape(self.cover.exportCitation()))
        item.add_item('출간일', '2018-06-01')
        item.add_item('출판', '금치산자레시피')
        item.add_item('웹사이트', 'https://gtszrcp.github.io')
        item.add_item('저작권', '이 책에 수록된 저작물 중 별도로 표기되지 않은 모든 저작물은 금치산자레시피와 저자의 자산으로 크리에이티브커먼즈 저작자표시-동일조건변경허락 4.0 국제 라이센스에 의해 이용할 수 있습니다.')
        item.add_item('이 책은 BartlebyMachine으로 제작되었습니다.')
        return item.dumps().replace('\\', '\\\\')


class Bartleby:

    toc = None
    manuscripts = None
    overcite = None
    orphan = None
    config = None

    def __init__(self):
        self.manuscripts = list(filter(
            lambda x: os.path.isdir(os.path.join(Config().manuscript_dir, x)) == False,
            os.listdir(Config().manuscript_dir)
        ))
        self.toc = [];


    def writeLatex(self):
        latex = self.replaceTemplate()
        f = open('ggded.tex', 'w', encoding='utf-8')
        f.write(latex)
        f.close()
        return


    def replaceTemplate(self):
        template = Config().template
        book = []
        replaces = [
            (re.compile('<<content>>'), self.toc.exportContent()),
            (re.compile('<<author>>'), self.toc.author),
            (re.compile('<<title>>'), self.toc.title),
            (re.compile('<<date>>'), datetime.datetime.strptime(self.toc.dateOfPublished, '%Y-%m-%d').strftime('%Y')),
            (re.compile('<<preface>>'), self.toc.exportPreface()),
            (re.compile('<<endpaper>>'), self.toc.exportEndpaper()),
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
