hqDefine("telerivet/js/telerivet_setup", function() {
    'use strict';
    var initialPageData = hqImport("hqwebapp/js/initial_page_data").get,
        telerivetSetupApp = window.angular.module('telerivetSetupApp', ['ngRoute', 'ng.django.rmi']);

    var globalApiKey = '';
    var globalProjectId = '';
    var globalPhoneId = '';
    var globalTestPhoneNumber = '';
    var globalTestSMSSent = false;

    telerivetSetupApp.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.defaults.headers.common["X-CSRFToken"] = $("#csrfTokenContainer").val();
    }]);

    telerivetSetupApp.config(function(djangoRMIProvider) {
        djangoRMIProvider.configure(initialPageData('djng_current_rmi'));
    });

    telerivetSetupApp.config(function($routeProvider) {
        $routeProvider
            .when('/start', {templateUrl: 'start.tpl'})
            .when('/step1', {templateUrl: 'step1.tpl'})
            .when('/step2', {templateUrl: 'step2.tpl'})
            .when('/step3', {templateUrl: 'step3.tpl'})
            .when('/finish', {templateUrl: 'finish.tpl'})
            .otherwise({redirectTo: '/start'});
    });

    telerivetSetupApp.controller('TelerivetSetupController', function($scope, djangoRMI) {
        // model attributes
        $scope.apiKey = globalApiKey;
        $scope.projectId = globalProjectId;
        $scope.phoneId = globalPhoneId;
        $scope.testPhoneNumber = globalTestPhoneNumber;
        $scope.name = initialPageData('form_name');
        $scope.setAsDefault = initialPageData('form_set_as_default');

        // error messages
        $scope.apiKeyError = null;
        $scope.projectIdError = null;
        $scope.phoneIdError = null;
        $scope.testPhoneNumberError = null;
        $scope.nameError = null;
        $scope.setAsDefaultError = null;

        // screenshot toggles
        $scope.showApiKeyGeneration = false;
        $scope.showApiInfoLocation = false;
        $scope.showAddWebookNavigation = false;
        $scope.showWebhookDetails = false;

        // control flow variables
        $scope.showOutboundTroubleshoot = false;
        $scope.showInboundTroubleshoot = false;
        $scope.testSMSSent = globalTestSMSSent;
        $scope.pollForInboundSMS = false;
        $scope.pollingErrorOccurred = false;
        $scope.inboundSMSReceived = false;
        $scope.inboundWaitTimedOut = false;
        $scope.setupComplete = false;

        $scope.toggleApiInfoLocation = function() {
            $scope.showApiInfoLocation = !$scope.showApiInfoLocation;
        };

        $scope.toggleApiKeyGeneration = function() {
            $scope.showApiKeyGeneration = !$scope.showApiKeyGeneration;
        };

        $scope.toggleAddWebookNavigation = function() {
            $scope.showAddWebookNavigation = !$scope.showAddWebookNavigation;
        };

        $scope.toggleWebhookDetails = function() {
            $scope.showWebhookDetails = !$scope.showWebhookDetails;
        };

        $scope.sendTestSMS = function() {
            djangoRMI.send_sample_sms({
                api_key: $scope.apiKey,
                project_id: $scope.projectId,
                phone_id: $scope.phoneId,
                test_phone_number: $scope.testPhoneNumber,
                request_token: initialPageData('request_token'),
            })
            .success(function(data) {
                $('#id_send_sms_button')
                .text(gettext("Send"));
                $scope.apiKeyError = data.api_key_error;
                $scope.projectIdError = data.project_id_error;
                $scope.phoneIdError = data.phone_id_error;
                $scope.testPhoneNumberError = data.unexpected_error || data.test_phone_number_error;
                $scope.testSMSSent = data.success;
            })
            .error(function() {
                $('#id_send_sms_button')
                .text(gettext("Server error. Try again..."));
            });
        };

        $scope.createBackend = function() {
            $('#id_create_backend').prop('disabled', true);
            djangoRMI.create_backend({
                name: $scope.name,
                api_key: $scope.apiKey,
                project_id: $scope.projectId,
                phone_id: $scope.phoneId,
                request_token: initialPageData('request_token'),
                set_as_default: $scope.setAsDefault
            })
            .success(function(data) {
                if(data.success) {
                    $scope.setupComplete = true;
                    setTimeout(function() {
                        window.location.href = initialPageData('gateway_list_url')
                    }, 2000);
                } else {
                    $scope.nameError = data.unexpected_error || data.name_error;
                    if(data.name_error) {
                        $('#id_create_backend')
                        .prop('disabled', false)
                        .text(gettext("Complete"));
                    }
                }
            })
            .error(function() {
                $('#id_create_backend')
                .prop('disabled', false)
                .text(gettext("Server error. Try again..."));
            });
        };

        $scope.getLastInboundSMS = function() {
            djangoRMI.get_last_inbound_sms({
                request_token: initialPageData('request_token'),
            })
            .success(function(data) {
                if(data.success) {
                    if(data.found) {
                        $scope.inboundSMSReceived = true;
                    } else {
                        setTimeout($scope.getLastInboundSMS, 10000);
                    }
                } else {
                    $scope.pollingErrorOccurred = true;
                }
            })
            .error(function() {
                // This is just an http error, for example, rather than
                // something like a missing request token, so just retry it.
                setTimeout($scope.getLastInboundSMS, 10000);
            });
        };

        $scope.startInboundPolling = function() {
            $scope.pollForInboundSMS = true;
            $scope.inboundWaitTimedOut = false;
            setTimeout(function() {
                $scope.inboundWaitTimedOut = true;
            }, 30000);
            $scope.getLastInboundSMS();
        };

        // TODO: Figure out if there's a better way to deal with these scope issues
        $scope.$watch('apiKey', function(newValue, oldValue) {
            globalApiKey = newValue;
            $scope.testSMSSent = false;
        });
        $scope.$watch('projectId', function(newValue, oldValue) {
            globalProjectId = newValue;
            $scope.testSMSSent = false;
        });
        $scope.$watch('phoneId', function(newValue, oldValue) {
            globalPhoneId = newValue;
            $scope.testSMSSent = false;
        });
        $scope.$watch('testPhoneNumber', function(newValue, oldValue) {
            globalTestPhoneNumber = newValue;
        });
        $scope.$watch('testSMSSent', function(newValue, oldValue) {
            globalTestSMSSent = newValue;
        });
    });
});
