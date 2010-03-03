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

function log(msg) {
    if (window.console && window.console.log) {
        return console.log(msg);
    } else {
        return alert(msg);
    }
}

function initModelSelect(selectElem) {
    return getModels(
        function (data, textStatus, xhr) {
            var appName = function (model) {
                return model[0];
            };
            var modelName = function (model) {
                return model[1];
            };
            $.each(data.models, function (i, model) {
                console.log(model); // REMOVE
                console.log(appName(model));
                console.log(modelName(model));
                selectElem.tempest(
                    "append",
                    "modelOption",
                    {
                        model: appName(model) + "." + modelName(model)
                    }
                );
            });
        },
        function () {
            log("Failure fetching models.");
        }
    );
}

$(document).ready(function () {
    var modelSelect = $("dl dd #model-select");

    initModelSelect(modelSelect);
});