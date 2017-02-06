app.controller('MainCtrl', ['$scope', '$rootScope', '$location', 'Records', 
               function ($scope, $rootScope, $location, Records) {
  $scope.categories = [
      {
        name: 'Popular',
        resultCount: 100
      },
      {
        name: 'Medical'
      },
      {
        name: 'Miscellaneous'
      },
      {
        name: 'Sports'
      }
    ];
  $scope.records = Records.query();
  console.log($scope.records);

  $scope.view = function(record) {
    var params = [];
    params.push('shape=person_rect');
    params.push('odds=' + record.odds);
    var paramString = params.join('&');
    $rootScope.imgSrc = '/api/draw?' + paramString;
    $location.path('/image');
  }
}]);