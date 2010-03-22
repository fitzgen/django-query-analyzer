from query_analyzer.decorators import json_view, html_view
from query_analyzer.forms import FieldsForm, PythonForm
from query_analyzer.shortcuts import AnalyzePython, list_models, detail_model, get_model

from django.db import transaction

@html_view("query_analyzer/basic_analyze.html")
@transaction.commit_manually
def basic_analyze(request):
    form = PythonForm(request.POST or None, initial={"python":"all"})
    result = None
    data = { "form": form, }
    if form.is_valid():
        clean = form.cleaned_data
        if clean.get("python"):
            try:
                analyzer = AnalyzePython(
                    model=get_model(clean.get("model")),
                    python=clean.get("python")
                    )
                data.update(analyzer())
            except SyntaxError:
                form._errors["python"] = ["There is an error with that code",]

    transaction.rollback()
    return data

@json_view
def model_select(request):
    return list_models()

@json_view
def model_details(request, app_label, model_name):
    return detail_model(app_label, model_name)