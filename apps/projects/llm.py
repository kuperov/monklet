from apps.projects import models


def description_for_rec(rec: models.Record) -> str:
    """Use Gemini to make a 1-sentence description for rec"""
    return f"Description for {rec}"


def description_for_case(case: models.Case) -> str:
    """Use Gemini to make a 1-sentence description for case"""
    return f"Description for {case}"
