import os

from pylatex.base_classes import Environment, CommandBase, Arguments, Options, Command
from pylatex.package import Package
from pylatex import Document, Section, UnsafeCommand


class Book:

    def __init__(self):
        doc = Document()
        doc.Command(Package('fullpage', options=Options('cm')))

        print(doc.dumps())
