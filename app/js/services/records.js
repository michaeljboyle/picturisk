app.factory('Records', ['$resource', function($resource) {
  return $resource('/api/records/:id', { id: '@key' }, {
    update: {
      method: 'PUT' // this method issues a PUT request
    }
  });
}]);