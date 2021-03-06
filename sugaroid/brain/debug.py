from chatterbot.logic import LogicAdapter
from nltk import word_tokenize, pos_tag

from sugaroid.brain.constants import BYE, ANNOYED
from sugaroid.brain.myname import MyNameAdapter
from sugaroid.brain.ooo import Emotion
from sugaroid.brain.postprocessor import random_response
from sugaroid.brain.preprocessors import normalize
from sugaroid.sugaroid import SugaroidStatement


class DebugAdapter(LogicAdapter):
    """
    Internal Admin feature to debug Sugaroid statements
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.normalized = None
        self.intersect = None
        self.tokenized = None
        self.commands = {
            "list": [self.track, 1, "List the last number of conversation"],
            "num": [self.gen_num, 0, "Show the number of conversations"],
            "help": [self.help, 0, "Show the help for using debugger"],
        }

    def can_process(self, statement):
        self.normalized = normalize(str(statement))

        if "debug" in self.normalized:
            return True
        else:
            return False

    def process(self, statement, additional_response_selection_parameters=None):
        emotion = Emotion.seriously
        confidence = 9

        if len(self.normalized) > 4:
            response = "Debugger: Invalid command"
        else:
            if len(self.normalized) > 3:
                response = self.commands[self.normalized[1]][0](
                    int(self.normalized[2], int(self.normalized[3]))
                )
            elif len(self.normalized) > 2:
                response = self.commands[self.normalized[1]][0](int(self.normalized[2]))
            else:
                response = self.commands[self.normalized[1]][0]()

        selected_statement = SugaroidStatement(response, chatbot=True)
        selected_statement.confidence = confidence
        selected_statement.emotion = emotion
        selected_statement.adapter = None
        return selected_statement

    def track(self, number, number_out=None):
        if number_out is not None:
            if number_out > number:
                return _(
                    [
                        self.chatbot.globals["DEBUG"][x]
                        for x in range(number, number_out)
                    ]
                )
            else:
                return _(
                    [
                        self.chatbot.globals["DEBUG"][x]
                        for x in range(number_out, number)
                    ]
                )
        else:
            return _([self.chatbot.globals["DEBUG"][number]])

    def gen_num(self):
        return self.chatbot.globals["DEBUG"]["number_of_conversations"]

    def help(self):
        response = []
        for i in self.commands:
            response.append("{}:\t {}".format(i, self.commands[i][-1]))
        return "Sugaroid Debugger.\n" + " \n".join(response)


def _(ls):
    """
    prettify
    :param ls:
    :return:
    """
    response = []
    for dictionary in ls:
        response_per_dictionary = []
        for key in dictionary:
            response_per_dictionary.append("{}\t {}\n".format(key, dictionary[key]))
        response.append(" ".join(response_per_dictionary))
    return "\n".join(response)
