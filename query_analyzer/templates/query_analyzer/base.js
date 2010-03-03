function getModels(success, error) {
    return $.ajax({
        dataType: "json",
        url: "{% url query_analyzer.views.model_select %}",
        success: success,
        error: error || function () {}
    });
}

function getModelDetails(appLabel, modelName, success, error) {
    return $.ajax({
        dataType: "json",
        url: "{% url query_analyzer.views.model_details '_LABEL' '_MODEL' %}"
            .replace("_LABEL", appLabel).replace("_MODEL", modelName),
        success: success,
        error: error || function () {}
    });
}

$(document).ready(function () {

});