hqDefine("app_manager/js/summary/utils", function() {
    var translateName = function(names, targetLang, langs, fallback) {
        fallback = fallback ? fallback : '[unknown]';
        var langs = [targetLang].concat(langs),
            firstLang = _(langs).find(function(lang) {
                return names[lang];
            });
        if (!firstLang) {
            return fallback;
        }
        return names[firstLang] + (firstLang === targetLang ? '' : ' [' + firstLang + ']');
    };

    var formIcon = function(form) {
        var formIcon = 'fa fa-file-o appnav-primary-icon';
        if (form.action_type === 'open') {
            formIcon = 'fcc fcc-app-createform appnav-primary-icon appnav-primary-icon-lg';
        } else if (form.action_type === 'close') {
            formIcon = 'fcc fcc-app-completeform appnav-primary-icon appnav-primary-icon-lg';
        } else if (form.action_type === 'update') {
            formIcon = 'fcc fcc-app-updateform appnav-primary-icon appnav-primary-icon-lg';
        }
        return formIcon;
    };

    var moduleIcon = function(module) {
        var moduleIcon = 'fa fa-folder-open appnav-primary-icon';
        if (module.module_type === 'advanced') {
            moduleIcon = 'fa fa-flask appnav-primary-icon';
        } else if (module.module_type === 'report') {
            moduleIcon = 'fa fa-bar-chart appnav-primary-icon';
        } else if (module.module_type === 'shadow') {
            moduleIcon = 'fa fa-folder-open-o appnav-primary-icon';
        } else if (!module.is_surveys) {
            moduleIcon = 'fa fa-bars appnav-primary-icon';
        }
        return moduleIcon;
    };

    return {
        formIcon: formIcon,
        moduleIcon: moduleIcon,
        translateName: translateName,
    };
});