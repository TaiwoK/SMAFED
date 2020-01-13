import jamspell


class SpellCheckerWrapper:
    """
    Wrapper over jamspell spell checker
    https://github.com/bakwc/JamSpell#python
    """
    def __init__(self, model_path):
        """
        :param model_path: path to model file
        """
        self.corrector = jamspell.TSpellCorrector()
        self.corrector.LoadLangModel(model_path)

    def correct(self, text):
        """
        text correction method
        :param text: text to be corrected
        Return corrected text
        """
        return self.corrector.FixFragment(text)
