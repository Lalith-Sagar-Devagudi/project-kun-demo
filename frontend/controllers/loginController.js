app.controller('LoginController', ['$scope', '$http', '$location', function($scope, $http, $location) {
    $scope.error = false;
  
    $scope.login = function() {
      $http.post('http://localhost:8000/login', {
        username: $scope.username,
        password: $scope.password
      })
      .then(function(response) {
        // Store credentials securely (consider using cookies or session storage)
        localStorage.setItem('username', $scope.username);
        localStorage.setItem('password', $scope.password);
        // Redirect to landing page
        $location.path('/landing');
      })
      .catch(function(error) {
        $scope.error = true;
        $scope.errorMessage = 'Invalid credentials. Please try again.';
      });
    };
  }]);