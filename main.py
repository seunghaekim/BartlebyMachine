import os
import pypandoc
import json
import yaml
import re
import datetime
from .config import Config
from pypandoc.pandoc_download import download_pandoc
from pylatex import Document, Description
from pylatex.section import Chapter
from pylatex.utils import *

class Cover:
    artist = None
    title = None
    year = None
    medium = None
    musium = None
    location = None
    license = None
    # Goya, Francisco. The Family of Charles IV. 1800, oil on canvas, Museo del Prado, Madrid.
    def __init__(self, cover):
        for dic in cover:
            key = list(dic.keys())[0]
            try:
                setattr(self, key, dic[key])
            except:
                print('error', key)

        return

    def export_citation(self):
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
    title = None
    layout = None
    latex = None
    type = 'mainmatter'
    filename = None
    endnote = None
    sample = False

    def __init__(self, content):
        for key in content:
            try:
                setattr(self, key, content[key])
            except:
                print(key)

        self.latex = self.convert_latex()
        return


    def convert_latex(self):
        filepath = os.path.join(Config().manuscript_dir, self.filename+'.md')
        return pypandoc.convert_file( filepath, 'latex', extra_args=[
                '--data-dir='+os.path.join(os.getcwd(), 'BartlebyMachine', '.pandoc'),
                '--wrap=none',
                '--variable',
                'documentclass=book',
        ])

    def write_latex(self):
        output_path = os.path.join(Config().manuscript_dir, 'tex', self.filename) + '.tex';

        f = open(output_path, 'w', encoding='utf-8')
        f.write(self.latex)
        f.close()


class TableOfContent:

    title = None
    author = None
    dateOfPublished = None
    cover = None
    license = None
    content = []
    sample = False

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


    def export_content(self):
        concat = []
        for content in self.content:
            if self.sample == True and content.sample == False:
                continue
            
            if content.type == 'mainmatter':
                str = '\\\\begin{{{layout}}}\n{latex}\n\end{{{layout}}}'.format(latex=content.latex.replace('\\\r\n', '\\\\\n'), layout=content.layout);
                concat.append(str)

        return '\n'.join(concat)


    def export_preface(self):
        if self.sample == True:
            prefaces = list(filter(lambda x: x.type == 'preface' and x.sample == True, self.content))
        else:
            prefaces = list(filter(lambda x: x.type == 'preface', self.content))
        return '\n'.join(list(map(lambda x: x.latex, prefaces)))


    def export_endpaper(self):
        options = ['itemsep=1pt', 'parsep=1pt']
        book = Description(options=options)
        book.add_item('제목', self.title)
        book.add_item('저자', self.author)
        book.add_item('편집', '미루')
        book.add_item('디자인', '써드엔지니어링카르텔')
        book.add_item('출간일', '2018-06-01')

        publisher = Description(options=options)
        publisher.add_item('출판', '금치산자레시피')
        publisher.add_item('웹사이트', 'http://gtszrcp.com')

        cover = Description(options=options)
        cover.add_item('표지', NoEscape(self.cover.export_citation()))
        cover.add_item('표지 그림 저작권', self.cover.license)

        license = Description(options=options)
        license.add_item('저작권', NoEscape('이 책에 수록된 저작물 중 별도로 표기되지 않은 모든 저작물의 저작권은 저자에게 있습니다. %s에 의해 이용할 수 있습니다.'%italic(self.license)))
        license.add_item('', '이 책은 BartlebyMachine으로 제작되었습니다.')

        endpaper = map(lambda x: x.dumps().replace('\\', '\\\\'), [
            book, publisher, cover, license
        ])
        return '\n'.join(list(endpaper))

    def export_appendix(self):
        appendix = []
        appendix.append(Chapter('참조'))
        content = Description()
        endnotes = list(filter(lambda x: x.endnote != None, self.content))
        for note in endnotes:
            content.add_item(note.title, note.endnote)

        appendix.append(content)
        appendix = list(map(lambda x: x.dumps().replace('\\', '\\\\'), appendix))
        return '\n'.join(appendix)


class Bartleby:

    toc = None
    manuscripts = None
    overcite = None
    orphan = None
    config = None
    sample = False

    def __init__(self):
        self.manuscripts = list(filter(
            lambda x: os.path.isdir(os.path.join(Config().manuscript_dir, x)) == False,
            os.listdir(Config().manuscript_dir)
        ))
        self.toc = [];


    def write_latex(self):
        latex = self.replace_template()
        filename = 'ggded.tex' 
        if self.sample == True:
            filename = 'ggded.sample.tex'
        f = open(filename, 'w', encoding='utf-8')
        f.write(latex)
        f.close()
        return


    def replace_template(self):
        template = Config().template
        book = []
        if self.sample == True:
            self.toc.sample = True
            self.toc.title = self.toc.title + ' 샘플북'
        
        replaces = [
            (re.compile('<<content>>'), self.toc.export_content()),
            (re.compile('<<author>>'), self.toc.author),
            (re.compile('<<title>>'), self.toc.title),
            (re.compile('<<date>>'), datetime.datetime.strptime(self.toc.dateOfPublished, '%Y-%m-%d').strftime('%Y')),
            (re.compile('<<preface>>'), self.toc.export_preface()),
            (re.compile('<<endpaper>>'), self.toc.export_endpaper()),
            (re.compile('<<endnotes>>'), self.toc.export_appendix()),
        ]

        for replace in replaces:
            if replace[0].findall(template):
                template = replace[0].sub(replace[1], template)

        return template

    def md_to_latex(self):
        result = False

        for content in self.toc.content:
            content.write_latex()

        return result


    def add_toc(self, filename):
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
