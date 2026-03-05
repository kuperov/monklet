from asgiref.sync import sync_to_async

from playwright.sync_api import Page
from apps.projects import models
from apps.users.models import User


from django.shortcuts import resolve_url


OWNER_EMAIL, OWNER_PASSWORD = "a@b.com", "secret"

INTERVIEW_CONTENT = [
    {
        "uuid": "5ebfa8c7-abd7-4428-8354-1d6c0ad53bf6",
        "sender": "model",
        "message": "Hello Alex, my name is Elsa. I am a research bot conducting interviews about the use of AI in research. Would you be willing to answer a few questions about your experiences?",
        "sent_at": "2024-11-13T22:58:41.855563Z",
        "prompt_token_count": 374,
        "total_token_count": 410,
        "candidates_token_count": 36,
    },
    {
        "uuid": "c10199eb-002e-4a78-aafc-24b26fed91da",
        "sender": "user",
        "message": "yeah",
        "sent_at": "2024-11-13T22:58:45.037914Z",
    },
    {
        "uuid": "da4e398d-f8fa-4225-a1fb-e64b44d61ca0",
        "sender": "model",
        "message": "Great! To start, what kind of research do you do? Do you mostly use qualitative, quantitative, or mixed methods?",
        "sent_at": "2024-11-13T22:58:46.565827Z",
        "prompt_token_count": 413,
        "total_token_count": 438,
        "candidates_token_count": 25,
    },
    {
        "uuid": "00570206-4bf2-42c9-860b-93dd4436b4c7",
        "sender": "user",
        "message": "qual",
        "sent_at": "2024-11-13T22:58:49.311597Z",
    },
    {
        "uuid": "fbb04520-b0de-44e9-aca7-531c1b7fee52",
        "sender": "model",
        "message": "Okay, so you mainly use qualitative methods. That's interesting. Can you tell me more about what kind of qualitative research you do?",
        "sent_at": "2024-11-13T22:58:50.836412Z",
        "prompt_token_count": 441,
        "total_token_count": 469,
        "candidates_token_count": 28,
    },
    {
        "uuid": "855c327e-da5d-4da5-a559-fd4410f1b948",
        "sender": "user",
        "message": "I interview people about their use of household devices",
        "sent_at": "2024-11-13T22:59:02.259957Z",
    },
    {
        "uuid": "43ea4f35-99b8-49c6-ab04-0ba29e0c7039",
        "sender": "model",
        "message": "That's very interesting!  Have you ever used AI tools for any part of your research?",
        "sent_at": "2024-11-13T22:59:03.636456Z",
        "prompt_token_count": 488,
        "total_token_count": 508,
        "candidates_token_count": 20,
    },
    {
        "uuid": "8ebebd96-e7cb-45f7-8f35-6b0d606558ea",
        "sender": "user",
        "message": "No, never",
        "sent_at": "2024-11-13T22:59:06.932710Z",
    },
    {
        "uuid": "a313b19f-c3d3-43a8-ac98-7800f4e6ff1e",
        "sender": "model",
        "message": "Okay. Have you ever considered using AI for qualitative analysis?",
        "sent_at": "2024-11-13T22:59:08.454952Z",
        "prompt_token_count": 507,
        "total_token_count": 519,
        "candidates_token_count": 12,
    },
    {
        "uuid": "123a5f16-fd63-45e6-bd0b-a988fe780f59",
        "sender": "user",
        "message": "thought about it, but don't know where to start",
        "sent_at": "2024-11-13T22:59:29.525159Z",
    },
    {
        "uuid": "6792be48-99ab-47f0-bf9d-180349e16e14",
        "sender": "model",
        "message": "I understand. It can be challenging to figure out where to start with AI in research. What specific challenges in qualitative data analysis do you hope AI could address?",
        "sent_at": "2024-11-13T22:59:30.569559Z",
        "prompt_token_count": 542,
        "total_token_count": 574,
        "candidates_token_count": 32,
    },
    {
        "uuid": "dec39613-854c-4ed8-ba75-5b42b9b512c2",
        "sender": "user",
        "message": "not having to code transcripts would be nice",
        "sent_at": "2024-11-13T23:00:38.004355Z",
    },
    {
        "uuid": "5f460890-981a-4aae-8dea-227ce9dac92c",
        "sender": "model",
        "message": "That makes sense. It sounds like you're hoping AI could help with the time-consuming task of coding transcripts. How do you currently manage the coding and theming of your qualitative data?",
        "sent_at": "2024-11-13T23:00:40.068881Z",
        "prompt_token_count": 580,
        "total_token_count": 619,
        "candidates_token_count": 39,
    },
    {
        "uuid": "7a040b5d-d0fe-45e0-aa4b-c07119c8ad70",
        "sender": "user",
        "message": "currently do everything manually",
        "sent_at": "2024-11-13T23:00:49.717307Z",
    },
    {
        "uuid": "8a0618e9-ffc7-4dd4-bd5f-6c1f2833913f",
        "sender": "model",
        "message": "I see. So you are doing all of the coding and theming by hand. Do you think that AI tools could help you manage your data more efficiently?",
        "sent_at": "2024-11-13T23:00:51.597082Z",
        "prompt_token_count": 621,
        "total_token_count": 653,
        "candidates_token_count": 32,
    },
    {
        "uuid": "d48f8de0-fdd8-44f2-b7be-77a7e091d5d3",
        "sender": "user",
        "message": "i don't know, what do you think?",
        "sent_at": "2024-11-13T23:03:09.313530Z",
    },
    {
        "uuid": "ecf97eef-c01b-4c9e-bd29-a60edebb8aff",
        "sender": "model",
        "message": "That's a great question! I'm not able to offer opinions or advice. However, I can share some information about how AI is being used in qualitative research. Some researchers are using AI tools to help them identify themes and patterns in their data, and others are using AI to help them analyze large amounts of text data. It's a growing field.\n\nDo you have any ethical concerns about using AI in qualitative research?",
        "sent_at": "2024-11-13T23:03:10.864812Z",
        "prompt_token_count": 673,
        "total_token_count": 761,
        "candidates_token_count": 88,
    },
    {
        "uuid": "57a24ad9-a237-49ad-80d7-88df242024e0",
        "sender": "user",
        "message": "i don't see what ethics has to do with it",
        "sent_at": "2024-11-13T23:03:36.162325Z",
    },
    {
        "uuid": "017bcb34-2326-4a3b-ab99-3e235e4fe774",
        "sender": "model",
        "message": "That's a good point.  Some people might argue that using AI tools could lead to biases in the analysis, or that it could make it difficult to understand the nuances of human language. \n\nWhat do you think about these concerns?",
        "sent_at": "2024-11-13T23:03:37.821932Z",
        "prompt_token_count": 776,
        "total_token_count": 825,
        "candidates_token_count": 49,
    },
    {
        "uuid": "40377f60-8483-40ec-96d4-aa7e8babb16b",
        "sender": "user",
        "message": "that's up to the researcher, as usual",
        "sent_at": "2024-11-13T23:04:03.525124Z",
    },
    {
        "uuid": "07752b05-6842-4b97-b1e0-89c681f2cdb2",
        "sender": "model",
        "message": "That's true, the researcher always has the ultimate responsibility for the integrity of their work.  Do you think a researcher that uses AI tools is doing a substandard job, or cheating somehow?",
        "sent_at": "2024-11-13T23:04:05.462264Z",
        "prompt_token_count": 835,
        "total_token_count": 874,
        "candidates_token_count": 39,
    },
    {
        "uuid": "774e63e9-4d23-4802-9010-e17438a83aab",
        "sender": "user",
        "message": "what a stupid question",
        "sent_at": "2024-11-13T23:04:16.517327Z",
    },
    {
        "uuid": "e8792a89-b970-495c-b791-fa4bb31be61e",
        "sender": "model",
        "message": "I apologize if my question came across as offensive. I am a research bot, still under development, and I am learning how to best conduct interviews. My goal is to understand how researchers are using AI tools and the challenges they face.\n\nI understand that you might be frustrated with my question, and I appreciate your honesty.\n\nWould you be willing to answer a different question? \n\nPerhaps we could talk about how you think AI will change the landscape of qualitative research in the next five years?",
        "sent_at": "2024-11-13T23:04:18.631296Z",
        "prompt_token_count": 874,
        "total_token_count": 974,
        "candidates_token_count": 100,
    },
    {
        "uuid": "06b29020-d149-41fb-9e2b-f78f4d77d4a2",
        "sender": "user",
        "message": "ai tools are clearly the way of the future",
        "sent_at": "2024-11-13T23:04:38.336618Z",
    },
    {
        "uuid": "fbc42d67-2886-4d00-a29e-79f481932787",
        "sender": "model",
        "message": "That's an interesting point.  Can you tell me more about why you think AI tools are the future of qualitative research?",
        "sent_at": "2024-11-13T23:04:40.100261Z",
        "prompt_token_count": 990,
        "total_token_count": 1016,
        "candidates_token_count": 26,
    },
    {
        "uuid": "19608526-cb28-4b1b-af40-5cc3ed447162",
        "sender": "user",
        "message": "they are the best way to do\n text processing",
        "sent_at": "2024-11-13T23:04:58.680105Z",
    },
    {
        "uuid": "e96a51da-586b-4083-9c45-22f648a26662",
        "sender": "model",
        "message": "I see. You believe AI tools are the best way to handle text processing in qualitative research. That's an interesting perspective. Can you tell me more about what kind of text processing you're thinking of? \n\nFor example, are you thinking about tools that help with coding transcripts, identifying themes, or analyzing large datasets of text?",
        "sent_at": "2024-11-13T23:05:00.454606Z",
        "prompt_token_count": 1029,
        "total_token_count": 1098,
        "candidates_token_count": 69,
    },
    {
        "uuid": "57282d4d-550a-46c0-b574-88a8abb24115",
        "sender": "user",
        "message": "let's wrap this up",
        "sent_at": "2024-11-13T23:05:11.769783Z",
    },
    {
        "uuid": "45a50355-de4d-440b-814a-b0b6c04460c1",
        "sender": "model",
        "message": "Okay, thank you for your time, Alex. It was interesting to hear your thoughts on AI in qualitative research.",
        "sent_at": "2024-11-13T23:05:13.297299Z",
        "prompt_token_count": 1102,
        "total_token_count": 1130,
        "candidates_token_count": 28,
    },
]


def create_project():
    owner = User.objects.create_user(
        email=OWNER_EMAIL, password=OWNER_PASSWORD, name="Max Goose"
    )
    project = models.Project.objects.create(owner=owner, name="XYZ")
    proj_url = resolve_url(project)
    bot = models.Bot.objects.create(
        project=project, name="BBB", status="live", allow_public=True
    )
    return {
        "owner": owner,
        "project": project,
        "proj_url": proj_url,
        "bot": bot,
    }


async def acreate_project():
    owner = await sync_to_async(User.objects.create_user)(
        email=OWNER_EMAIL, password=OWNER_PASSWORD, name="Max Goose"
    )
    project = await models.Project.objects.acreate(owner=owner, name="XYZ")
    proj_url = resolve_url(project)
    bot = await models.Bot.objects.acreate(
        project=project,
        name="BBB",
        description="Big beautiful bot",
        prompt="You are a silly bot. Make silly conversation. At the end of the conversation output ENDOFINTERVIEW",
        aimodel="gemini-2.5-flash",
        status="live",
        allow_public=True,
    )
    return {
        "owner": owner,
        "project": project,
        "proj_url": proj_url,
        "bot": bot,
    }


async def acreate_interview(owner, project, proj_url, bot):
    interview = await models.Interview.objects.acreate(
        project=project,
        bot=bot,
        subject_email="user@here.com",
        subject_name="Alex",
        has_consented=True,
        followup_consented=True,
        # ignore a bunch of the fields copied from bot
        status="complete",
        attributes=[],
        content=INTERVIEW_CONTENT,
    )
    return {
        "owner": owner,
        "project": project,
        "proj_url": proj_url,
        "bot": bot,
        "interview": interview,
    }


def create_ai_chat(**kwargs):
    interview = kwargs["interview"]
    kwargs["case"] = models.Case.from_chat(interview, "Tony")
    kwargs["chat"] = kwargs["case"].current_records().first()
    return kwargs


async def acreate_ai_chat(**kwargs):
    interview = kwargs["interview"]
    afrom_chat = sync_to_async(models.Case.from_chat)
    kwargs["case"] = await afrom_chat(interview, "Tony")
    return kwargs


def create_interview(owner, project, proj_url, bot):
    interview = models.Interview.objects.create(
        project=project,
        bot=bot,
        subject_email="user@here.com",
        subject_name="Alex",
        has_consented=True,
        followup_consented=True,
        # ignore a bunch of the fields copied from bot
        status="complete",
        attributes=[],
        content=INTERVIEW_CONTENT,
    )
    return {
        "owner": owner,
        "project": project,
        "proj_url": proj_url,
        "bot": bot,
        "interview": interview,
    }


def create_interview_fixture(test):
    fields = create_project()
    fields = create_interview(**fields)
    for name, val in fields.items():
        setattr(test, name, val)


async def acreate_interview_fixture(test):
    fields = await acreate_project()
    fields = await acreate_interview(**fields)
    for name, val in fields.items():
        setattr(test, name, val)


def create_ai_chat_fixture(test):
    fields = create_project()
    fields = create_interview(**fields)
    fields = create_ai_chat(**fields)
    for name, val in fields.items():
        setattr(test, name, val)


async def acreate_ai_chat_fixture(test):
    fields = await acreate_project()
    fields = await acreate_interview(**fields)
    fields = await acreate_ai_chat(**fields)
    for name, val in fields.items():
        setattr(test, name, val)


def create_project_fixture(test):
    fields = create_project()
    for name, val in fields.items():
        setattr(test, name, val)


async def acreate_project_fixture(test):
    fields = await acreate_project()
    for name, val in fields.items():
        setattr(test, name, val)


def playwright_login(live_server_url, page: Page):
    page.goto(f"{live_server_url}/accounts/login/")
    page.fill("#id_login", "a@b.com")
    page.fill("#id_password", "secret")
    page.click("#submit-id-signin")


async def aplaywright_login(live_server_url, page: Page):
    await page.goto(f"{live_server_url}/accounts/login/")
    await page.fill("#id_login", "a@b.com")
    await page.fill("#id_password", "secret")
    await page.click("#submit-id-signin")
