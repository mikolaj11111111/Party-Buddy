from dataclasses import dataclass


@dataclass(frozen=True)
class TtsTemplate:
    id: str
    text: str


COMMENT_TEMPLATES: tuple[TtsTemplate, ...] = (
    TtsTemplate("intro_001", "Witamy w Party Buddy. Zaczynamy pierwszą rundę."),
    TtsTemplate("correct_001", "Dobra odpowiedź. Punkt trafia na konto."),
    TtsTemplate("correct_002", "Tak jest. To była poprawna odpowiedź."),
    TtsTemplate("correct_003", "Zgadza się. Lecimy dalej."),
    TtsTemplate("correct_004", "Poprawnie. Bardzo dobry wybór."),
    TtsTemplate("correct_005", "Jest punkt. Odpowiedź była dobra."),
    TtsTemplate("correct_006", "Dokładnie tak. Wynik idzie w górę."),
    TtsTemplate("correct_007", "Trafione. Następne pytanie za moment."),
    TtsTemplate("correct_008", "To jest dobra odpowiedź."),
    TtsTemplate("correct_009", "Zaliczone. Punkt zostaje dopisany."),
    TtsTemplate("correct_010", "Brawo. Odpowiedź jest poprawna."),
    TtsTemplate("wrong_001", "Niestety, to nie ta odpowiedź."),
    TtsTemplate("wrong_002", "Pudło. Poprawna odpowiedź była inna."),
    TtsTemplate("wrong_003", "Tym razem bez punktu."),
    TtsTemplate("wrong_004", "Nie zgadza się. Gramy dalej."),
    TtsTemplate("wrong_005", "Blisko albo daleko, ale punktu nie ma."),
    TtsTemplate("wrong_006", "To była błędna odpowiedź."),
    TtsTemplate("wrong_007", "Nie tym razem. Następne pytanie."),
    TtsTemplate("wrong_008", "Odpowiedź nie jest poprawna."),
    TtsTemplate("wrong_009", "Zero punktów za to pytanie."),
    TtsTemplate("wrong_010", "Nie trafione. Szansa na odrobienie strat za chwilę."),
    TtsTemplate("partial_001", "Rozpoznałem odpowiedź, ale wynik jest niepewny."),
    TtsTemplate(
        "partial_002", "To brzmi blisko, ale potrzebuję jaśniejszej odpowiedzi."
    ),
    TtsTemplate("partial_003", "Odpowiedź wymaga potwierdzenia."),
    TtsTemplate("partial_004", "Nie jestem pewien dopasowania tej odpowiedzi."),
    TtsTemplate("partial_005", "Możemy to sprawdzić jeszcze raz."),
    TtsTemplate("outro_001", "Koniec rundy. Za chwilę zobaczysz wyniki."),
)


def iter_tts_templates() -> tuple[TtsTemplate, ...]:
    return COMMENT_TEMPLATES
