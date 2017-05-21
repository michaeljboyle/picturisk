
app.controller('NewCtrl', ['$scope', '$rootScope', '$location', '$http',
               '$window', 'Records', 
               function($scope, $rootScope, $location, $http,
                        $window, Records) {

  $scope.categories = ['Medical', 'Miscellaneous', 'Sports'];

  $scope.shapes = ['square', 'circle', 'person', 'person_rect'];

  $scope.types = ['png', 'svg'];

  // Additional optional params defined in the view
  $scope.imgParams = {
    'shape': 'person_rect',
    'color1': 'red',
    'color2': 'black',
    'index': 0.0,
    'type': 'svg'
  };

  $scope.save = false;
  
  $scope.record = new Records();

  function getImage() {
    var params = [];
    for (var param in $scope.imgParams) {
      if ($scope.imgParams[param] !== null) {
        params.push(param + '=' + $scope.imgParams[param]);
      }
    }
    params.push('odds=' + $scope.record.odds);
    var paramString = params.join('&');
    $rootScope.imgSrc = '/api/draw?' + paramString;
    $window.location.href = 'http://odds-view.appspot.com' + $rootScope.imgSrc;
  }

  $scope.loading = false;

  $scope.submit = function() {
    $scope.loading = true;
    // Deactivate button and animate to page where image is shown
    // Show image loading icon
    if ($scope.save) {
      $scope.record.$save();
    }
    getImage();
  };
}]);