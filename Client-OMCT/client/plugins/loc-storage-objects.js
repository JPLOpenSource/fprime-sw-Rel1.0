// Load views from saved-views dict

function LoadViews() {
    function getViews() {
        // Needs directory of localstorage
        return http.get('/server/res/demo-views.json').then(function (result) {
            return result.data;
        });
    }

    // Demo
    getViews().then(function (v) {

        localStorage.setItem('mct', JSON.stringify(v));
        
    });
}

// function DefaultViews() {
//     return function install(openmct) {
//         openmct.objects.addRoot({
//             namespace: 'isf.default',
//             key: 'root'
//         });

//         openmct.objects.addProvider('isf.default', {
//             get: function(identifier) {
//                 return http.get('/server/res/demo-views.json').then(function (result) {
//                     return result.data;
//                 }).then(function (data) {
//                     return data[identifier.key];
//                 });
//             }
//         })
//     }
// }