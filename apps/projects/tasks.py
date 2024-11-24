from celery import shared_task

from apps.projects import models
from apps.projects import llm


@shared_task
def update_data_descriptions(project_id: str, force=False):
    project = models.Project.objects.get(pk=project_id)
    for case in project.current_cases():
        rec_updated = False
        for rec in case.current_records():
            if force or not rec.description:
                print(f"Processing {rec}")
                rec.description = llm.description_for_rec(rec)
                rec.save()
                rec_updated = True
        if force or rec_updated or not case.description:
            print(f"Processing {case}")
            case.description = llm.description_for_case(case)
            case.save()


@shared_task
def get_themes(project_id: str):
    project = models.Project.objects.get(pk=project_id)
    NUM_THEMES = 30
    project.themes = [
        {
            "ThemeName": "Themes regenerating",
            "Description": "Refresh the page in a moment",
            "Quotes": [],
            "Participants": 0,
        }
    ]
    project.save()
    # blocking, takes a while
    project.themes = llm.get_themes(project, NUM_THEMES)
    project.save()
