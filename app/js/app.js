var app = angular.module('SeeTheOddsApp', ['ngMaterial', 
                         'ngRoute', 'ngResource']);

app.config(function($mdThemingProvider, $routeProvider) {
  $mdThemingProvider.theme('default')
    .primaryPalette('purple', {
      'default': '500',
      'hue-1': '700',
      'hue-2': '800',
      'hue-3': '300'
    })
    .accentPalette('green', {'default': 'A200'});

    $routeProvider.when('/', {
      controller: 'MainCtrl',
      templateUrl: 'views/main.html'
    }).when('/new', {
      controller: 'NewCtrl',
      templateUrl: 'views/new.html'
    }).when('/image', {
      controller: 'ImageCtrl',
      templateUrl: 'views/image.html'
    }).otherwise({
      redirectTo: '/'
    });
});
  
/*
app.factory('myHttpInterceptor', function($rootScope, $q) {
  return {
    'requestError': function(config) {
      $rootScope.status = 'HTTP REQUEST ERROR ' + config;
      return config || $q.when(config);
    },
    'responseError': function(rejection) {
      $rootScope.status = 'HTTP RESPONSE ERROR ' + rejection.status + '\n' +
                          rejection.data;
      return $q.reject(rejection);
    },
  };
});

app.config(function($httpProvider) {
  $httpProvider.interceptors.push('myHttpInterceptor');
});
*/