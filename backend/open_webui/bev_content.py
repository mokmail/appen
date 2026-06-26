"""BEV-specific content overlay.

Holds BEV customisation data that would otherwise be inlined into
upstream files (e.g. default prompt suggestions).  Keeping it here means
upstream ``config.py`` can be refreshed wholesale on upgrade without
losing the BEV prompt set.
"""

BEV_PROMPT_SUGGESTIONS = [
    {
        'title': ['Organisation des BEV', 'Wie ist das BEV aufgebaut?'],
        'content': 'Wie ist das Bundesamt für Eich- und Vermessungswesen organisatorisch aufgebaut? Beschreibe die Gruppen und Hauptabteilungen.',
    },
    {
        'title': ['Aufgaben des Eichwesens', 'Was macht die Gruppe Eichwesen?'],
        'content': 'Welche Aufgaben hat die Gruppe Eichwesen des BEV? Erkläre die Rolle als nationales Metrologie-Institut und Eichbehörde.',
    },
    {
        'title': ['Geoinformation & Kataster', 'Wofür ist die Gruppe Grundlagen und Geoinformation zuständig?'],
        'content': 'Wofür ist die Gruppe Grundlagen und Geoinformation beim BEV zuständig? Nenne die Abteilungen und ihre Kernaufgaben.',
    },
    {
        'title': ['Marktüberwachung', 'Was sind die Aufgaben der Marktüberwachung?'],
        'content': 'Welche Aufgaben übernimmt die Gruppe Marktüberwachung des BEV? Erkläre die Funktionsweise und die Fachbereiche.',
    },
    {
        'title': ['IT-Strategie & CIO', 'Wie ist die IT am BEV organisiert?'],
        'content': 'Wie ist die IT-Organisation am BEV aufgebaut? Beschreibe die Stabsabteilung IT-Strategie und Steuerung sowie die IT-Infrastruktur.',
    },
]

__all__ = ['BEV_PROMPT_SUGGESTIONS']