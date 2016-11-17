/*
 * THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
 * FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
 */


'use strict';

(function () {

    var XLDVersionsTileViewController = function ($scope, XLDVersionsService, XlrTileHelper) {
        var vm = this;
        var tile;

        if ($scope.xlrTile) {
            // summary mode
            tile = $scope.xlrTile.tile;
        } else {
            // details mode
            tile = $scope.xlrTileDetailsCtrl.tile;
        }

        function tileConfigurationIsPopulated() {
            var config = tile.configurationProperties;
            return !_.isEmpty(config.xldeployServer) && !_.isEmpty(config.environment);
        }

        function getColor(value) {
            if (predefinedColors[value]) return predefinedColors[value];
            return colorPool.pop();
        }

        function getTitle(){
            if(vm.issuesSummaryData.total > 1){
                return "tickets";
            }
            else{
                return "ticket";
            }
        }

        vm.chartOptions = {
            topTitleText: function (data) {
                return data.total;
            },
            bottomTitleText: getTitle,
            series: function (data) {
                var series = {
                    name: 'State',
                    data: []
                };
                series.data = _.map(data.data, function (value) {
                    return {y: value.counter, name: value.state, color: value.color};
                });
                return [ series ];
            },
            showLegend: false,
            donutThickness: '60%'
        };

        function load(config) {
            if (tileConfigurationIsPopulated()) {
                vm.loading = true;
                XLDVersionsService.executeQuery(tile.id, config).then(
                    function (response) {
                        var versions = response.data.data;
                        if(versions[0] === "Invalid environment name"){
                            vm.invalidEnvironment = true;
                        }
                        else{
                            var xldeployData = [];
                            vm.invalidEnvironment = false;
                            for (var app in versions) {
                                xldeployData.push(versions[app])
                            }
                            vm.deployedAppsCounter = xldeployData.length;
                            vm.summaryGridOptions = createSummaryGridOptions(xldeployData);
                        }
                    }
                ).finally(function () {
                    vm.loading = false;

                });
            }
        }

        function createSummaryGridOptions(xldeployData) {
            var filterHeaderTemplate = "<div data-ng-include=\"'partials/releases/grid/templates/name-filter-template.html'\"></div>";
            var columnDefs = [
                {
                    displayName: "Application",
                    field: "application",
                    cellTemplate: "static/@project.version@/include/XLDVersionsTile/grid/application.html",
                    filterHeaderTemplate: filterHeaderTemplate,
                    enableColumnMenu: false,
                    width: '50%'
                },
                {
                    displayName: "Version",
                    field: "version",
                    cellTemplate: "static/@project.version@/include/XLDVersionsTile/grid/version.html",
                    filterHeaderTemplate: filterHeaderTemplate,
                    enableColumnMenu: false,
                    width: '50%'
                }
            ];
            return XlrTileHelper.getGridOptions(xldeployData, columnDefs);
        }

        function refresh() {
            load({params: {refresh: true}});
        }

        load();

        vm.refresh = refresh;
    };

    XLDVersionsTileViewController.$inject = ['$scope', 'xlrelease.xldeploy.XLDVersionsService', 'XlrTileHelper'];

    var XLDVersionsService = function (Backend) {

        function executeQuery(tileId, config) {
            return Backend.get("/tiles/" + tileId + "/data", config);
        }
        return {
            executeQuery: executeQuery
        };
    };

    XLDVersionsService.$inject = ['Backend'];

    angular.module('xlrelease.XLDVersions.tile', []);
    angular.module('xlrelease.XLDVersions.tile').service('xlrelease.xldeploy.XLDVersionsService', XLDVersionsService);
    angular.module('xlrelease.XLDVersions.tile').controller('xldeploy.XLDVersionsTileViewController', XLDVersionsTileViewController);

})();
