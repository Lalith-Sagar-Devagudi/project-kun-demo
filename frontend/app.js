var app = angular.module('myApp', ['ngRoute']);

app.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/', {
      templateUrl: 'templates/login.html',
      controller: 'LoginController'
    })
    .when('/landing', {
      templateUrl: 'templates/landing.html',
      controller: 'LandingController'
    })
    .when('/upload', {
      templateUrl: 'templates/upload.html',
      controller: 'UploadController'
    })
    .otherwise({
      redirectTo: '/'
    });
}]);
