app.controller('ImageCtrl', function ($scope, $rootScope, $location) {
    $scope.imgSrc = $rootScope.imgSrc
    console.log($rootScope.imgSrc);
});