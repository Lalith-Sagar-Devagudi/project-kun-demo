app.controller('LandingController', ['$scope', '$location', function($scope, $location) {
    $scope.goToUpload = function() {
      $location.path('/upload');
    };
    // Implement other button functions as needed
  }]);