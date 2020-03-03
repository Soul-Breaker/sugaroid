"""
sugaroid by srevinsaju
Get it on : https://github.com/srevinsaju/guiscrcpy
Licensed under GNU Public License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import logging
import time
from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from sugaroid.brain.ooo import Emotion
from sugaroid.gui.ui.main import Ui_MainWindow
import threading


"""
class SleepRequests:
    def __init__(self, parent):
        self.parent = parent
        self.sleeping = True

    def set_sleeping(self, boo):
        self.sleeping = boo

    def run(self):
        while self.sleeping:
            if self.parent.sleep <= 20:
                time.sleep(1)
                self.parent.sleep += 1

            else:
                self.parent.label.setPixmap(QPixmap(":/home/sugaroid_sleep.png"))
                break
"""

emotion = \
    {
        Emotion.neutral: "sugaroid",
        Emotion.negative: "sugaroid_cry",
        Emotion.angry: "sugaroid_anger",
        Emotion.non_expressive: "sugaroid_non_expressive",
        Emotion.positive: "sugaroid_smile",
        Emotion.wink: "sugaroid_wink_left",
        Emotion.non_expressive_left: "sugaroid_non_expressive_left",
        Emotion.angry_non_expressive: "sugaroid_extreme_anger",
        Emotion.cry: "sugaroid_cry",
        Emotion.dead: "sugaroid_dead",
        Emotion.lol: "sugaroid_lol",
        Emotion.cry_overflow: "sugaroid_depressed",
        Emotion.adorable: "sugaroid_adorable",
        Emotion.github: "sugaroid_github",
        Emotion.angel: "sugaroid_angel",
        Emotion.rich: "sugaroid_rich",
        Emotion.seriously: "sugaroid_seriously",
        Emotion.fun: "sugaroid_wink_right",
        Emotion.blush: "sugaroid_blush",
        Emotion.depressed: "sugaroid_depressed",
        Emotion.o: "sugaroid_o",
        Emotion.smirking: "sugaroid_wink_left",
        Emotion.vomit: "sugaroid_dead"
    }


class AudioRequests:
    def __init__(self, parent, ress):

        self.parent = parent
        self.response = ress

    def run(self):
        self.parent.parent.tts.speak(self.response)


class EmotionRequests(QThread):
    def __init__(self, parent, emo):
        QThread.__init__(self, parent)
        self.parent = parent
        self.emotion = emo

    def run(self):
        self.parent.label.setPixmap(
            QPixmap(":/home/{}.png".format(emotion[self.emotion])))
        time.sleep(5)
        self.parent.label.setPixmap(QPixmap(":/home/sugaroid.png"))


class BotRequests(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent

    def run(self):
        text = self.parent.chatbox.text()
        self.parent.conv.addItem("you: {}".format(text))
        self.parent.chatbox.setText("")
        self.parent.conv.scrollToBottom()
        response = self.parent.parent.parse(text)

        self.parent.conv.addItem("sugaroid: {}".format(str(response)))
        time.sleep(0.1)

        if response.emotion != 0:
            # print(response.emotion, emotion[response.emotion])
            # em = EmotionRequests(self.parent, response.emotion)
            # em.start()
            self.parent.label.setPixmap(
                QPixmap(":/home/{}.png".format(emotion[response.emotion])))
            self.parent.conv.scrollToBottom()
            time.sleep(5)

        self.parent.label.setPixmap(QPixmap(":/home/sugaroid.png"))
        self.parent.conv.scrollToBottom()

        if self.parent.parent.audio:
            aud = AudioRequests(self.parent, str(response))
            y = threading.Thread(target=aud.run)
            y.start()


class InterfaceSugaroidQt(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.sleep = 0

        self.sleep_enabled = True
        if parent is None:
            from sugaroid.sugaroid import Sugaroid
            sg = Sugaroid()
            self.parent = sg
        else:
            self.parent = parent

    def init(self):
        self.push.pressed.connect(self.refresh)
        self.chatbox.returnPressed.connect(self.refresh)
        self.conv.clear()
        self.show()

        self.chatbox.setFocus()

    def refresh(self):
        # if self.sleep_enabled:
        #    if self.sl_thread.is_alive():
        #        self.sl.set_sleeping(False)
        #        self.sl_thread.join()
        #        print("THREAD IS SLEEPING", not self.sl_thread.is_alive())

        # self.sleep = 0
        # if self.sleep_enabled:
        #    if not self.sl_thread.is_alive():
        #        self.sl_thread = threading.Thread(target=self.sl.run)
        #        self.sl_thread.start()

        if str(self.chatbox.text()).isspace():
            return
        movie = QtGui.QMovie(":/home/sugaroid_thinking3.gif")
        self.label.setMovie(movie)
        movie.start()

        bot = BotRequests(self)
        bot.start()
