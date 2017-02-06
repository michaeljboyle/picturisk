app.controller('NavCtrl', function ($scope, $timeout, $mdSidenav, $location) {
    $scope.toggleSidenav = buildToggler('sidenav');

    function buildToggler(componentId) {
      return function() {
        $mdSidenav(componentId).toggle();
      };
    }

    $scope.new = function() { $location.path('/new'); }

    $scope.home = function() { $location.path('/')}
  });