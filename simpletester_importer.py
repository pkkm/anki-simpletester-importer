# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
import string

import anki
from anki.importing.noteimp import NoteImporter, ForeignNote
from anki.lang import _

class Question:
    """A question with answers from a SimpleTester database."""

    def __init__(self, question=None, answers=None, iCorrectAnswer=None):
        self.question = question
        self.answers = answers
        self.iCorrectAnswer = iCorrectAnswer

class SimpleTesterLinesParser:
    """Gets a list of lines from a SimpleTester database and turns it
    into a list of Question objects."""

    def __init__(self, lines):
        self.lines = lines
        self.iNextLine = 0

    def nextLine(self):
        line = self.lines[self.iNextLine]
        self.iNextLine += 1
        return line

    def nextQuestion(self):
        result = Question()

        result.question = self.nextLine()

        nAnswers = int(self.nextLine())
        result.answers = []
        for iAnswer in xrange(nAnswers):
            result.answers.append(self.nextLine())

        result.iCorrectAnswer = int(self.nextLine()) - 1

        return result

    def allQuestions(self):
        fileFormatVersion = self.nextLine() # Not used.

        questions = []
        while self.iNextLine < len(self.lines):
            questions.append(self.nextQuestion())

        return questions

class SimpleTesterImporter(NoteImporter):
    def __init__(self, *args):
        NoteImporter.__init__(self, *args)
        self.fileOpen = None

    def foreignNotes(self):
        """Read notes from the open file."""

        self.open()
        lines = [line.rstrip() for line in self.fileOpen]
        self.fileOpen.close()

        parser = SimpleTesterLinesParser(lines)
        questions = parser.allQuestions()
        notes = [self.questionToNote(question) for question in questions]
        return notes

    def open(self):
        """Open the selected file (if it's not already open)."""
        if self.fileOpen is None:
            self.fileOpen = io.open(
                self.file, mode="r", encoding="windows-1250")

    def fields(self):
        """Return the number of fields in the notes we create."""
        return 2

    def questionToNote(self, question):
        """Convert a Question object to a ForeignNote."""

        displayedAnswers = []
        for letter, answer in zip(string.lowercase, question.answers):
            displayedAnswers.append(letter + ") " + answer)

        questionField = question.question + "\n\n" + "\n".join(displayedAnswers)
        answerField = displayedAnswers[question.iCorrectAnswer]

        note = ForeignNote()
        note.fields = [questionField, answerField]
        return note

anki.importing.Importers += (
    # The trailing comma is important!
    (_("SimpleTester File (*.dat *.txt)"), SimpleTesterImporter),)
