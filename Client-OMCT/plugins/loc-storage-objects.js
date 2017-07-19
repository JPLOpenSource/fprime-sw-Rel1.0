// Load views from saved-views dict

function LoadViews() {
    function getViews() {
        // Needs directory of localstorage
        return http.get('/server/res/save-views.json').then(function (result) {
            return result.data;
        });
    }

    getViews().then(function (v) {

        localStorage.setItem('mct', JSON.stringify(v));
        
    });
}