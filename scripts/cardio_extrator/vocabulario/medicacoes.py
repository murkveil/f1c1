"""Expressões regulares pré-compiladas para detecção de medicações cardiovasculares."""

import re

EXPRESSOES_MEDICACOES: dict[str, list[re.Pattern[str]]] = {
    "anti_hipertensivo": [
        re.compile(r"losartana"), re.compile(r"enalapril"),
        re.compile(r"amlodipina"), re.compile(r"atenolol"),
        re.compile(r"captopril"), re.compile(r"valsartana"),
        re.compile(r"nifedipina"), re.compile(r"metoprolol"),
        re.compile(r"propranolol"), re.compile(r"carvedilol"),
        re.compile(r"hidralazina"),
        re.compile(r"remédio\s+(?:\w+\s+){0,2}pressão"),
    ],
    "anticoagulante": [
        re.compile(r"varfarina"), re.compile(r"rivaroxabana"),
        re.compile(r"apixabana"), re.compile(r"dabigatrana"),
        re.compile(r"edoxabana"), re.compile(r"heparina"),
        re.compile(r"marevan"), re.compile(r"xarelto"),
        re.compile(r"eliquis"),
    ],
    "antiplaquetario": [
        re.compile(r"\baas\b"), re.compile(r"aspirina"),
        re.compile(r"clopidogrel"), re.compile(r"ticagrelor"),
        re.compile(r"prasugrel"),
    ],
    "estatina": [
        re.compile(r"sinvastatina"), re.compile(r"atorvastatina"),
        re.compile(r"rosuvastatina"), re.compile(r"pravastatina"),
        re.compile(r"fluvastatina"),
        re.compile(r"remédio\s+(?:\w+\s+){0,2}colesterol"),
    ],
    "diuretico": [
        re.compile(r"furosemida"), re.compile(r"hidroclorotiazida"),
        re.compile(r"espironolactona"), re.compile(r"indapamida"),
        re.compile(r"clortalidona"), re.compile(r"lasix"),
    ],
    "antidiabetico": [
        re.compile(r"metformina"), re.compile(r"glibenclamida"),
        re.compile(r"gliclazida"), re.compile(r"insulina"),
        re.compile(r"glargina"), re.compile(r"dapagliflozina"),
        re.compile(r"empagliflozina"), re.compile(r"sitagliptina"),
        re.compile(r"remédio\s+(?:\w+\s+){0,2}(?:diabetes|açúcar|glicemia)"),
    ],
    "antiarritmico": [
        re.compile(r"amiodarona"), re.compile(r"sotalol"),
        re.compile(r"propafenona"), re.compile(r"flecainida"),
        re.compile(r"digoxina"),
    ],
}
