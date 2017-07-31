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

define(
    ["../../src/controllers/ListViewController"],
    function (ListViewController) {
        describe("The Controller for the ListView", function () {
            var scope,
                unlistenFunc,
                domainObject,
                childObject,
                controller,
                childModel,
                typeCapability,
                mutationCapability;
            beforeEach(function () {
                unlistenFunc = jasmine.createSpy("unlisten");

                mutationCapability = jasmine.createSpyObj(
                    "mutationCapability",
                    ["listen"]
                );
                mutationCapability.listen.andReturn(unlistenFunc);

                typeCapability = jasmine.createSpyObj(
                    "typeCapability",
                    ["getCssClass", "getName"]
                );
                typeCapability.getCssClass.andReturn("icon-folder");
                typeCapability.getName.andReturn("Folder");


                childModel = jasmine.createSpyObj(
                    "childModel",
                    ["persisted", "modified", "name"]
                );
                childModel.persisted = 1496867697303;
                childModel.modified = 1496867697303;
                childModel.name = "Battery Charge Status";

                childObject = jasmine.createSpyObj(
                    "childObject",
                    ["getModel", "getCapability"]
                );
                childObject.getModel.andReturn(
                    childModel
                );
                // childObject.getCapability.andReturn(
                //     typeCapability
                // );
                childObject.getCapability.andCallFake(function (arg) {
                    if (arg === 'location') {
                        return '';
                    } else if (arg === 'type') {
                        return typeCapability;
                    }
                });
                childObject.location = '';

                domainObject = jasmine.createSpyObj(
                    "domainObject",
                    ["getCapability", "useCapability"]
                );
                domainObject.useCapability.andReturn(
                    Promise.resolve([childObject])
                );
                domainObject.getCapability.andReturn(
                    mutationCapability
                );


                scope = jasmine.createSpyObj(
                    "$scope",
                    ["$on"]
                );
                scope.domainObject = domainObject;

                controller  = new ListViewController(scope);

                waitsFor(function () {
                    return scope.children;
                });
            });
            it("updates the view", function () {
                expect(scope.children[0]).toEqual(
                    {
                        icon: "icon-folder",
                        title: "Battery Charge Status",
                        type: "Folder",
                        persisted: "Wed, 07 Jun 2017 20:34:57 GMT",
                        modified: "Wed, 07 Jun 2017 20:34:57 GMT",
                        asDomainObject: childObject,
                        location: ''
                    }
                );
            });
            it("updates the scope when mutation occurs", function () {
                domainObject.useCapability.andReturn(
                    Promise.resolve([])
                );
                expect(mutationCapability.listen).toHaveBeenCalledWith(jasmine.any(Function));
                mutationCapability.listen.mostRecentCall.args[0]();
                waitsFor(function () {
                    return scope.children.length !== 1;
                });
                runs(function () {
                    expect(scope.children.length).toEqual(0);
                });
            });
            it("releases listeners on $destroy", function () {
                expect(scope.$on).toHaveBeenCalledWith('$destroy', jasmine.any(Function));
                scope.$on.mostRecentCall.args[1]();
                expect(unlistenFunc).toHaveBeenCalled();
            });


        });
    }
);
