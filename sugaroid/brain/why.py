from chatterbot.logic import LogicAdapter
from sugaroid.brain.wiki import WikiAdapter

from sugaroid.brain.preprocessors import normalize, spac_token

from sugaroid.brain.postprocessor import random_response

from sugaroid.brain.constants import (
    WHY_IDK,
    HOW_DO_YOU_FEEL,
    WHERE_LIVE,
    DONT_KNOW_WHERE,
)
from sugaroid.brain.ooo import Emotion
from sugaroid.sugaroid import SugaroidStatement


class WhyWhenAdapter(LogicAdapter):
    """
    Processes wh-adverbs
    """

    def __init__(self, chatbot, **kwargs):
        # FIXME Add Language support
        super().__init__(chatbot, **kwargs)
        self.tokenized = None
        self.normalized = None

    def can_process(self, statement):
        self.tokenized = spac_token(statement, chatbot=self.chatbot)
        self.normalized = normalize(str(statement))
        for i in self.tokenized:
            if i.tag_ == "WRB":
                return True
        else:
            return False

    def process(self, statement, additional_response_selection_parameters=None):
        """

        :param statement:
        :param additional_response_selection_parameters:
        :return:
        """
        emotion = Emotion.neutral
        if "when" in self.normalized:
            if "you" in self.normalized or "your" in self.normalized:
                response = "When did you what?"
                confidence = 0.6
                for i in ["creator", "author", "developer"]:
                    if i in self.normalized:
                        response = "Let's say, its TOP SECRET!!"
                        confidence = 0.8
                        emotion = Emotion.lol
                        break
                for i in [
                    "birthday",
                    "b'day",
                    "bday",
                    "born",
                    "birth",
                    "bear",
                    "create",
                    "manufactured",
                ]:
                    if i in self.normalized:
                        # the person is asking my birthday
                        response = "I was born on Tue Feb 11 14:58:38 2020 +0300"
                        confidence = 0.8
                        emotion = Emotion.blush
                        break
            else:
                # search in wikipedia
                return WikiAdapter(self.chatbot).process(statement)
        elif "why" in self.normalized:
            # say idk
            response = random_response(WHY_IDK)
            confidence = 0.2
            emotion = Emotion.cry_overflow
        elif (
            "how" in self.normalized
            and "you" in self.normalized
            and "be" in self.normalized
        ):
            # possibly the person asked
            # 'how are you'
            response = random_response(HOW_DO_YOU_FEEL)
            confidence = 0.75
        elif "where" in self.normalized:
            if "you" in self.normalized:
                if "live" in self.normalized or "stay" in self.normalized:
                    # the person is asking something like
                    # "where do you live"
                    response = random_response(WHERE_LIVE)
                    confidence = 0.75
                else:
                    response = random_response(DONT_KNOW_WHERE)
                    confidence = 0.65
            else:
                # the person is asking something like
                # where is india
                return WikiAdapter(self.chatbot).process(statement)
        else:
            # say idk
            response = ":)"
            confidence = 0.15
        selected_statement = SugaroidStatement(response, chatbot=True)
        selected_statement.confidence = confidence
        selected_statement.emotion = emotion

        return selected_statement
