app.service('BackendService', function($http) {
    var username = '';
    var password = '';

    this.setCredentials = function(user, pass) {
        username = user;
        password = pass;
    };

    this.isAuthenticated = function() {
        return username && password;
    };

    this.getHeaders = function(isFormData) {
        var headers = {
            'X-Username': username,
            'X-Password': password
        };
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        return headers;
    };

    this.login = function(user, pass) {
        return $http.post('http://localhost:8000/login', {
            username: user,
            password: pass
        });
    };

    this.uploadPdfs = function(files) {
        var formData = new FormData();
        files.forEach(function(file) {
            formData.append('files', file);
        });

        return $http.post('http://localhost:8000/upload-pdfs', formData, {
            headers: this.getHeaders(true),
            transformRequest: angular.identity
        });
    };

    this.processPdfs = function() {
        return $http.post('http://localhost:8000/process-pdfs', {}, {
            headers: this.getHeaders()
        });
    };
});
