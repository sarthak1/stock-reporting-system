// app.js
var app = angular.module('StockApp', []);

app.controller('StockController', function ($scope, $http) {
  $scope.transaction = {};
  $scope.summary = {};

  $scope.recordTransaction = function () {
    $http.post('/record-transaction/', $scope.transaction).then(
      function (response) {
        alert(response.data.message);
      },
      function (error) {
        alert('Error recording transaction');
      }
    );
  };

  $scope.calculateSummary = function () {
    $http.post('/calculate-daily-summary/', $scope.summary).then(
      function (response) {
        alert(response.data.message);
      },
      function (error) {
        alert('Error calculating summary');
      }
    );
  };
});

