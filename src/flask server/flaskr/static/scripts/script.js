angular.module('app')

.controller('DashboardCtrl', ['$scope', '$timeout',
                              function($scope, $timeout) {
                              
                              
                              
                              $scope.gridsterOptions = {
                              margins: [0, 200],
                              columns: 6,
                              draggable: {
                              handle: 'h3'
                              }
                              };
                              
                              
                              $scope.dashboards = {
                              '1': {
                              id: '1',
                              name: 'Home',
                              widgets: sensors_list
                                  }
                              };
                              
                              $scope.clear = function() {
                              $scope.dashboard.widgets = [];
                              };
                              
                              $scope.addWidget = function() {
                              $scope.dashboard.widgets.push({
                                                            name: "New Widget",
                                                            sizeX: 6,
                                                            sizeY: 1
                                                            });
                              };
                              
                              $scope.$watch('selectedDashboardId', function(newVal, oldVal) {
                                            if (newVal !== oldVal) {
                                            $scope.dashboard = $scope.dashboards[newVal];
                                            } else {
                                            $scope.dashboard = $scope.dashboards[1];
                                            }
                                            });
                              
                              // init dashboard
                              $scope.selectedDashboardId = '1';
                              
                              }
                              ])

.controller('CustomWidgetCtrl', ['$scope', '$modal',
                                 function($scope, $modal) {
                                 
                                 $scope.remove = function(widget) {
                                 $scope.dashboard.widgets.splice($scope.dashboard.widgets.indexOf(widget), 1);
                                 };
                                 
                                 $scope.openSettings = function(widget) {
                                 $modal.open({
                                             scope: $scope,
                                             templateUrl: 'main/widget_settings',
                                             controller: 'WidgetSettingsCtrl',
                                             resolve: {
                                             widget: function() {
                                             return widget;
                                             }
                                             }
                                             });
                                 };
                                 
                                 }
                                 ])

.controller('WidgetSettingsCtrl', ['$scope', '$timeout', '$rootScope', '$modalInstance', 'widget',
                                   function($scope, $timeout, $rootScope, $modalInstance, widget) {
                                   $scope.widget = widget;
                                   
                                   $scope.form = {
                                   name: widget.name,
                                   sizeX: widget.sizeX,
                                   sizeY: widget.sizeY,
                                   col: widget.col,
                                   pin: widget.pin,
                                   row: widget.row
                                   };
                                   
                                   $scope.sizeOptions = [{
                                                         id: '1',
                                                         name: '1'
                                                         }, {
                                                         id: '2',
                                                         name: '2'
                                                         }, {
                                                         id: '3',
                                                         name: '3'
                                                         }, {
                                                         id: '4',
                                                         name: '4'
                                                         }];
                                   
                                   $scope.dismiss = function() {
                                   $modalInstance.dismiss();
                                   };
                                   
                                   $scope.remove = function() {
                                   $scope.dashboard.widgets.splice($scope.dashboard.widgets.indexOf(widget), 1);
                                   $modalInstance.close();
                                   };
                                   
                                   $scope.submit = function() {
                                   angular.extend(widget, $scope.form);
                                   
                                   $modalInstance.close(widget);
                                   };
                                   
                                   }
                                   ])

// helper code
.filter('object2Array', function() {
        return function(input) {
        var out = [];
        for (i in input) {
        out.push(input[i]);
        }
        return out;
        }
        });
