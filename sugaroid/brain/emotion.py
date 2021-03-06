from random import randint
from chatterbot.logic import LogicAdapter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sugaroid.brain.constants import GRATIFY, CONSOLATION, SIT_AND_SMILE, APPRECIATION
from sugaroid.brain.ooo import Emotion
from sugaroid.brain.postprocessor import reverse, random_response, any_in
from sugaroid.brain.preprocessors import tokenize
from sugaroid.sugaroid import SugaroidStatement


class EmotionAdapter(LogicAdapter):
    """
    Handles positive and negative emotional statements
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.sia = SentimentIntensityAnalyzer()

    def can_process(self, statement):
        a = self.sia.polarity_scores(str(statement))
        # do not enable emotion adapter when
        # we are playing akinator
        if self.chatbot.globals["akinator"]["enabled"]:
            return False
        elif a["neu"] < 0.5:
            return True
        else:
            return False

    def process(self, statement, additional_response_selection_parameters=None):
        # parsed = str(statement).lower().strip()
        raw_statement = str(statement)
        parsed = tokenize(str(statement))
        emotion = Emotion.neutral
        a = self.sia.polarity_scores(raw_statement)
        response = ":)"
        confidence = a["pos"] + a["neg"]
        if (("love" in parsed) or ("hate" in parsed)) and (
            ("you" in parsed) or ("myself" in parsed)
        ):
            if a["pos"] >= a["neg"]:
                response = "I love you too"
                emotion = Emotion.blush
            else:
                response = "But still, I love you"
                emotion = Emotion.lol
        else:
            if a["pos"] > a["neg"]:
                if "you" in parsed:
                    response = GRATIFY[randint(0, len(GRATIFY) - 1)]
                    emotion = Emotion.blush
                else:
                    if "stop" in parsed:
                        if (
                            ("dont" in parsed)
                            or ("do" in parsed and "not" in parsed)
                            or ("don't" in parsed)
                        ):
                            response = "I am here to continue my adventure forever"
                            emotion = Emotion.positive
                        else:
                            # optimize series of or statement
                            if (
                                ("fun" in parsed)
                                or ("repeat" in parsed)
                                or ("imitation" in parsed)
                                or ("repetition" in parsed)
                                or ("irritate" in parsed)
                                or ("irritation" in parsed)
                            ):
                                response = (
                                    "Ok! I will switch off my fun mode for sometime"
                                )
                                emotion = Emotion.neutral
                                self.chatbot.globals["fun"] = False
                            else:
                                response = "I am depressed. Is there anything which I hurt you? I apologize for that"
                                emotion = Emotion.depressed
                    else:
                        if any_in(APPRECIATION, parsed):
                            response = random_response(GRATIFY)
                            emotion = Emotion.angel
                            confidence = 0.8
                        else:
                            # FIXME : Make it more smart
                            response = random_response(SIT_AND_SMILE)
                            emotion = Emotion.lol
                            if confidence > 0.8:
                                confidence -= 0.2
            else:
                if "i" in parsed:
                    response = "Its ok,  {}.".format(
                        CONSOLATION[randint(0, len(CONSOLATION) - 1)]
                    )
                    emotion = Emotion.positive
                elif "dead" in parsed:
                    if "everyone" in parsed or "every" in parsed:
                        if ("except" in parsed or "apart" in parsed) and "me" in parsed:
                            response = (
                                "So sad. Its a great feeling that only"
                                " me and you are the only person alive "
                                "on the face of this world."
                            )
                        else:
                            response = "So, am I speaking to you in heaven?"
                        emotion = Emotion.dead
                    else:
                        responses = (
                            "I hope you are not dead too. I am sorry.",
                            "My 💐 for them",
                            "My condolences...",
                            "So sad. I want to cry 😭",
                            "At least you are there for me!",
                        )
                        response = random_response(responses)
                        emotion = Emotion.lol
                else:

                    # well, I don't want to say ( I don't know )
                    # FIXME : Use a better algorithm to detect sentences
                    reversed = reverse(parsed)
                    response = "Why do you think {}?".format(" ".join(reversed))
                    emotion = Emotion.dead

        selected_statement = SugaroidStatement(response, chatbot=True)
        selected_statement.confidence = confidence
        selected_statement.emotion = emotion
        return selected_statement
