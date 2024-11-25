from apps.projects import tasks
from apps.projects import models, forms

from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import aget_object_or_404, get_object_or_404, render, redirect
from django.contrib.auth import aget_user
from django.utils.timezone import now

from apps.projects.llm import DEFAULT_GEMINI_PARAMS, genai
from apps.projects.views.util import get_editable_project, get_viewable_project


ANALYZE_SYSTEM_PROMPT = (
    "You are a helpful research assistant. Your task is to analyze a set of research interviews, "
    "given in markdown format. You always carefully check your work and never make facts up. "
    "If necessary, ask clarifying questions before proceeding."
)

@login_required
def themes(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk)
    return render(request, "analysis/themes.html", {"project": project})


@login_required
def regenerate_themes(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk)
    tasks.get_themes.delay(str(project.pk))
    messages.success(request, "Themes regenerating. Refresh the page in a few seconds.")
    return render(request, "analysis/_themes.html", {"project": project})


@login_required
def new_query(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk)
    aimodels = [(m.pk, m.name) for m in models.AIModel.objects.filter(deleted_at=None)]
    if request.method == "POST":
        form = forms.NewQueryForm(aimodels, request.POST)
        if form.is_valid():
            am = models.AIModel.objects.get(pk=int(form.cleaned_data["ai_model"]))
            params = {
                "temperature": float(form.cleaned_data["temperature"]),
                "top_p": float(form.cleaned_data["top_p"]),
                "top_k": form.cleaned_data["top_k"],
                "max_output_tokens": form.cleaned_data["max_output_tokens"],
                "response_mime_type": "text/plain",
            }
            q = models.Query.objects.create(
                project=project,
                ai_model=am,
                parameters=params,
                created_by=request.user
            )
            return redirect(q.get_absolute_url())
    else:
        initial = {
            'ai_model': models.AIModel.objects.first().pk,
            'temperature': DEFAULT_GEMINI_PARAMS['temperature'],
            'top_p': DEFAULT_GEMINI_PARAMS['top_p'],
            'top_k': DEFAULT_GEMINI_PARAMS['top_k'],
            'max_output_tokens': DEFAULT_GEMINI_PARAMS['max_output_tokens'],
        }
        form = forms.NewQueryForm(aimodels, initial=initial)
    ctx = {"project": project, "form": form}
    return render(request, "analysis/new_query.html", ctx)


@login_required
def query(request: HttpRequest, pk: str) -> HttpResponse:
    query = get_object_or_404(models.Query, pk=pk)
    project = query.project
    if query.deleted_at is not None:
        messages.warning(request, "The requested query has been deleted.")
        return redirect('new-query', pk=project.pk)
    form = forms.QueryMessageForm()
    ctx = {"project": project, "query": query, "form": form}
    return render(request, "analysis/query.html", ctx)


@login_required
async def query_update(request: HttpRequest, pk: str) -> HttpResponse:
    query = await aget_object_or_404(models.Query, pk=pk)
    project = await models.Project.objects.aget(pk=query.project_id)
    user = await aget_user(request)
    # TODO: check edit rights
    form = forms.QueryMessageForm(request.POST)
    if form.is_valid():
        prompt = form.cleaned_data["message"]
        if not isinstance(query.content, list):
            query.content = []
        ai_model = await models.AIModel.objects.aget(pk=query.ai_model_id)
        model = genai.GenerativeModel(
            model_name=ai_model.api_name,
            generation_config=query.parameters,
            system_instruction=ANALYZE_SYSTEM_PROMPT,
        )
        hist = await sync_to_async(query.get_history)()
        chat_session = model.start_chat(history=hist)
        trigger_describe = False
        if len(hist) == 0:
            markdown = await sync_to_async(project.get_markdown)()
            response = await chat_session.send_message_async([prompt, markdown])
            trigger_describe = True
        else:
            response = await chat_session.send_message_async(prompt)
        await query.astore_interaction(user, prompt, response)
        if trigger_describe:
            tasks.describe_query.apply_async((str(query.pk),))
        # reset form
        form = forms.QueryMessageForm()
    ctx = {"query": query, "form": form}
    return render(request, 'analysis/_query_contents.html', ctx)


@login_required
def query_delete(request: HttpRequest, pk: str) -> HttpResponse:
    query = get_object_or_404(models.Query, pk=pk)
    project = query.project
    query.deleted_at = now()
    query.save()
    messages.success(request, "Query deleted")
    return redirect('new-query', pk=project.pk)
