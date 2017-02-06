
app.controller('NewCtrl', ['$scope', '$rootScope', '$location', '$http', 'Records',
               function($scope, $rootScope, $location, $http, Records) {

  $scope.categories = ['Medical', 'Miscellaneous', 'Sports'];

  $scope.shapes = ['square', 'circle', 'person', 'person_rect'];

  $scope.imgParams = {
    'shape': 'person_rect',
    'color1': 'red',
    'color2': 'black',
    'index': 0.75,
    'right': false
  };

  $scope.save = false;
  
  $scope.record = new Records();

  function getImage() {
    var params = [];
    for (var param in $scope.imgParams) {
      params.push(param + '=' + $scope.imgParams[param]);
    }
    params.push('odds=' + $scope.record.odds);
    var paramString = params.join('&');
    $rootScope.imgSrc = '/api/draw?' + paramString;
    $location.path('/image');
    /*
    $http({
      method: 'GET',
      url: '/api/draw?' + paramString
    }).then(function successCallback(response) {
      $rootScope.imgSrc = response.data;
      $location.path('/image');
    }, function errorCallback(response) {
      // called asynchronously if an error occurs
      // or server returns response with an error status.
    }); */
  }

  $scope.submit = function() {
    // Deactivate button and animate to page where image is shown
    // Show image loading icon
    if ($scope.save) {
      $scope.record.$save();
    }
    getImage();
  }
}]);