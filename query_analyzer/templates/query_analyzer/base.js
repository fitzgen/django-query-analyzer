function log(msg) {
    if (window.console && window.console.log) {
        return console.log(msg);
    } else {
        return alert(msg);
    }
}

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

var appName = function (model) {
    return model[0];
};
var modelName = function (model) {
    return model[1];
};

function initModelSelect(selectElem, models) {
    return $.each(models, function (i, model) {
        selectElem.tempest(
            "append",
            "modelOption",
            {
                model: appName(model) + "." + modelName(model)
            }
        );
    });
}

function getAllModelDetails(models, detailsObj) {
    var ensureApp = function (appName) {
        if (typeof detailsObj[appName] === "undefined") {
            detailsObj[appName] = {};
        }
    };
    var ensureModel = function (appName, modelName) {
        if (typeof detailsObj[appName][modelName] === "undefined") {
            detailsObj[appName][modelName] = {
                managers: [],
                fields: [],
                relatedFields: []
            };
        }
    };
    var makeAdder = function (type) {
        return function (appName, modelName, value) {
            detailsObj[appName][modelName][type].push(value);
        };
    };
    var addManager = makeAdder("managers");
    var addField = makeAdder("fields");
    var addRelatedField = makeAdder("relatedFields");

    return $.each(models, function (i, model) {
        var app = appName(model);
        var thisModel = modelName(model);

        ensureApp(app);
        ensureModel(app, thisModel);

        getModelDetails(
            app,
            thisModel,
            function (data, textStatus, xhr) {
                $.each(data.managers, function (i, manager) {
                    addManager(app, thisModel, manager);
                });
                $.each(data.fields, function (i, field) {
                    addField(app, thisModel, field);
                });
                $.each(data.related_fields, function (i, relField) {
                    addRelatedField(app, thisModel, relField);
                });
            },
            function () {
                log("Error retreiving model info.");
            }
        );
    });
}

$(document).ready(function () {
    var modelSelect = $("dl dd #model-select");
    var modelsObj = {};
    window.models = modelsObj; // REMOVE

    getModels(
        function (data,textStatus, XHR) {
            initModelSelect(modelSelect, data.models);
            getAllModelDetails(data.models, modelsObj);
        },
        function () {
            log("Failure fetching models.");
        }
    );

});