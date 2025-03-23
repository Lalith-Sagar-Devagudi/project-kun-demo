app.controller('LoginController', ['$scope', '$http', '$location', function($scope, $http, $location) {
    $scope.error = false;
  
    $scope.login = function() {
      $http.post('/login', {
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
  
  app.controller('LandingController', ['$scope', '$location', function($scope, $location) {
    $scope.goToUpload = function() {
      $location.path('/upload');
    };
    // Implement other button functions as needed
  }]);
  
  app.controller('UploadController', ['$scope', '$http', function($scope, $http) {
    $scope.pdf1 = null;
    $scope.pdf2 = null;
    $scope.pdf1Name = '';
    $scope.pdf2Name = '';
    $scope.results = null;
  
    $scope.setFile = function(element, fileVar) {
      $scope.$apply(function() {
        if (fileVar === 'pdf1') {
          $scope.pdf1 = element.files[0];
          $scope.pdf1Name = $scope.pdf1.name;
        } else if (fileVar === 'pdf2') {
          $scope.pdf2 = element.files[0];
          $scope.pdf2Name = $scope.pdf2.name;
        }
      });
    };
  
    $scope.uploadFiles = function() {
      const username = localStorage.getItem('username');
      const password = localStorage.getItem('password');
  
      if (!username || !password) {
        alert('You are not logged in.');
        window.location.href = '#!/';
        return;
      }
  
      const formData = new FormData();
      formData.append('files', $scope.pdf1);
      formData.append('files', $scope.pdf2);
  
      // First, upload the PDFs
      $http.post('/upload-pdfs', formData, {
        headers: {
          'Content-Type': undefined,
          'X-Username': username,
          'X-Password': password
        },
        transformRequest: angular.identity
      })
      .then(function(response) {
        // Then, call /process-pdfs
        return $http.post('/process-pdfs', {}, {
          headers: {
            'X-Username': username,
            'X-Password': password
          }
        });
      })
      .then(function(response) {
        // Display results
        $scope.results = response.data;
      })
      .catch(function(error) {
        console.error('Error:', error);
        alert('An error occurred: ' + (error.data.detail || error.statusText));
      });
    };
  }]);
  