from celery import shared_task

from apps.projects import models
from apps.projects.llm import description_for_case, description_for_rec


@shared_task
def update_data_descriptions(project_id: str):
    project = models.Project.objects.get(pk=project_id)
    for case in project.current_cases():
        if not case.description:
            print(f"Processing {case}")
            case.description = description_for_case(case)
            case.save()
        for rec in case.current_records():
            if not rec.description:
                print(f"Processing {rec}")
                rec.description = description_for_rec(rec)
                rec.save()
