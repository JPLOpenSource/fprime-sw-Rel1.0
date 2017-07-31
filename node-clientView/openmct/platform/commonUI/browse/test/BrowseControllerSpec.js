/*****************************************************************************
 * Open MCT, Copyright (c) 2014-2017, United States Government
 * as represented by the Administrator of the National Aeronautics and Space
 * Administration. All rights reserved.
 *
 * Open MCT is licensed under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Open MCT includes source code licensed under additional open source
 * licenses. See the Open Source Licenses file (LICENSES.md) included with
 * this source code distribution or the Licensing information page available
 * at runtime from the About dialog for additional information.
 *****************************************************************************/

/**
 * MCTRepresentationSpec. Created by vwoeltje on 11/6/14.
 */
define(
    [
        "../src/BrowseController",
        "../src/navigation/NavigationService"
    ],
    function (
        BrowseController,
        NavigationService
    ) {

        describe("The browse controller", function () {
            var mockScope,
                mockRoute,
                mockLocation,
                mockObjectService,
                mockNavigationService,
                mockRootObject,
                mockUrlService,
                mockDefaultRootObject,
                mockOtherDomainObject,
                mockNextObject,
                testDefaultRoot,
                controller;

            function waitsForNavigation() {
                var calls = mockNavigationService.setNavigation.calls.length;
                waitsFor(function () {
                    return mockNavigationService.setNavigation.calls.length > calls;
                });
            }

            function instantiateController() {
                controller = new BrowseController(
                    mockScope,
                    mockRoute,
                    mockLocation,
                    mockObjectService,
                    mockNavigationService,
                    mockUrlService,
                    testDefaultRoot
                );
            }

            beforeEach(function () {
                testDefaultRoot = "some-root-level-domain-object";

                mockScope = jasmine.createSpyObj(
                    "$scope",
                    ["$on", "$watch"]
                );
                mockRoute = { current: { params: {}, pathParams: {} } };
                mockUrlService = jasmine.createSpyObj(
                    "urlService",
                    ["urlForLocation"]
                );
                mockUrlService.urlForLocation.andCallFake(function (mode, object) {
                    if (object === mockDefaultRootObject) {
                        return [mode, testDefaultRoot].join('/');
                    }
                    if (object === mockOtherDomainObject) {
                        return [mode, 'other'].join('/');
                    }
                    if (object === mockNextObject) {
                        return [mode, testDefaultRoot, 'next'].join('/');
                    }
                    throw new Error('Tried to get url for unexpected object');
                });
                mockLocation = jasmine.createSpyObj(
                    "$location",
                    ["path"]
                );
                mockObjectService = jasmine.createSpyObj(
                    "objectService",
                    ["getObjects"]
                );
                mockNavigationService = new NavigationService({});
                [
                    "getNavigation",
                    "setNavigation",
                    "addListener",
                    "removeListener"
                ].forEach(function (method) {
                    spyOn(mockNavigationService, method)
                        .andCallThrough();
                });
                mockRootObject = jasmine.createSpyObj(
                    "rootObjectContainer",
                    ["getId", "getCapability", "getModel", "useCapability", "hasCapability"]
                );
                mockDefaultRootObject = jasmine.createSpyObj(
                    "defaultRootObject",
                    ["getId", "getCapability", "getModel", "useCapability", "hasCapability"]
                );
                mockOtherDomainObject = jasmine.createSpyObj(
                    "otherDomainObject",
                    ["getId", "getCapability", "getModel", "useCapability", "hasCapability"]
                );
                mockNextObject = jasmine.createSpyObj(
                    "nestedDomainObject",
                    ["getId", "getCapability", "getModel", "useCapability", "hasCapability"]
                );
                mockObjectService.getObjects.andReturn(Promise.resolve({
                    ROOT: mockRootObject
                }));
                mockRootObject.useCapability.andReturn(Promise.resolve([
                    mockOtherDomainObject,
                    mockDefaultRootObject
                ]));
                mockRootObject.hasCapability.andReturn(true);
                mockDefaultRootObject.useCapability.andReturn(Promise.resolve([
                    mockNextObject
                ]));
                mockDefaultRootObject.hasCapability.andReturn(true);
                mockOtherDomainObject.hasCapability.andReturn(false);
                mockNextObject.useCapability.andReturn(undefined);
                mockNextObject.hasCapability.andReturn(false);
                mockNextObject.getId.andReturn("next");
                mockDefaultRootObject.getId.andReturn(testDefaultRoot);

                instantiateController();
                waitsForNavigation();
            });

            it("uses composition to set the navigated object, if there is none", function () {
                instantiateController();
                waitsForNavigation();
                runs(function () {
                    expect(mockNavigationService.setNavigation)
                        .toHaveBeenCalledWith(mockDefaultRootObject);
                });
            });

            it("navigates to a root-level object, even when default path is not found", function () {
                mockDefaultRootObject.getId
                    .andReturn("something-other-than-the-" + testDefaultRoot);
                instantiateController();

                waitsForNavigation();
                runs(function () {
                    expect(mockNavigationService.setNavigation)
                        .toHaveBeenCalledWith(mockDefaultRootObject);
                });

            });
            //
            it("does not try to override navigation", function () {
                mockNavigationService.getNavigation.andReturn(mockDefaultRootObject);
                instantiateController();
                waitsForNavigation();
                expect(mockScope.navigatedObject).toBe(mockDefaultRootObject);
            });
            //
            it("updates scope when navigated object changes", function () {
                // Should have registered a listener - call it
                mockNavigationService.addListener.mostRecentCall.args[0](
                    mockOtherDomainObject
                );
                expect(mockScope.navigatedObject).toEqual(mockOtherDomainObject);
            });


            it("releases its navigation listener when its scope is destroyed", function () {
                expect(mockScope.$on).toHaveBeenCalledWith(
                    "$destroy",
                    jasmine.any(Function)
                );
                mockScope.$on.mostRecentCall.args[1]();

                // Should remove the listener it added earlier
                expect(mockNavigationService.removeListener).toHaveBeenCalledWith(
                    mockNavigationService.addListener.mostRecentCall.args[0]
                );
            });

            it("uses route parameters to choose initially-navigated object", function () {
                mockRoute.current.params.ids = testDefaultRoot + "/next";
                instantiateController();
                waitsForNavigation();
                runs(function () {
                    expect(mockScope.navigatedObject).toBe(mockNextObject);
                    expect(mockNavigationService.setNavigation)
                        .toHaveBeenCalledWith(mockNextObject);
                });
            });

            it("handles invalid IDs by going as far as possible", function () {
                // Idea here is that if we get a bad path of IDs,
                // browse controller should traverse down it until
                // it hits an invalid ID.
                mockRoute.current.params.ids = testDefaultRoot + "/junk";
                instantiateController();
                waitsForNavigation();
                runs(function () {
                    expect(mockScope.navigatedObject).toBe(mockDefaultRootObject);
                    expect(mockNavigationService.setNavigation)
                        .toHaveBeenCalledWith(mockDefaultRootObject);

                });
            });

            it("handles compositionless objects by going as far as possible", function () {
                // Idea here is that if we get a path which passes
                // through an object without a composition, browse controller
                // should stop at it since remaining IDs cannot be loaded.
                mockRoute.current.params.ids = testDefaultRoot + "/next/junk";
                instantiateController();
                waitsForNavigation();
                runs(function () {
                    expect(mockScope.navigatedObject).toBe(mockNextObject);
                    expect(mockNavigationService.setNavigation)
                        .toHaveBeenCalledWith(mockNextObject);
                });
            });

            it("updates the displayed route to reflect current navigation", function () {
                // In order to trigger a route update and not a route change,
                // the current route must be updated before location.path is
                // called.
                expect(mockRoute.current.pathParams.ids)
                    .not
                    .toBe(testDefaultRoot + '/next');
                mockLocation.path.andCallFake(function () {
                    expect(mockRoute.current.pathParams.ids)
                        .toBe(testDefaultRoot + '/next');
                });
                mockNavigationService.addListener.mostRecentCall.args[0](
                    mockNextObject
                );
                expect(mockLocation.path).toHaveBeenCalledWith(
                    '/browse/' + testDefaultRoot + '/next'
                );
            });

        });
    }
);
