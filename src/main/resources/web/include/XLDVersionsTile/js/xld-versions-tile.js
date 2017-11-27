/*
 * Copyright 2017 XEBIALABS
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
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
            var config;
            // old style pre 7.0
            if (tile.properties == null) {
                config = tile.configurationProperties;
            } else {
                // new style since 7.0
                config = tile.properties;
            }
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
            var columnDefs = [
                {
                    displayName: "Application",
                    field: "application",
                    cellTemplate: "static/@project.version@/include/XLDVersionsTile/grid/application.html",
                    filterHeaderTemplate: "static/@project.version@/include/XLDVersionsTile/grid/name-filter-template.html",
                    enableColumnMenu: false,
                    width: '50%'
                },
                {
                    displayName: "Version",
                    field: "version",
                    cellTemplate: "static/@project.version@/include/XLDVersionsTile/grid/version.html",
                    filterHeaderTemplate: "static/@project.version@/include/XLDVersionsTile/grid/name-filter-template.html",
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
