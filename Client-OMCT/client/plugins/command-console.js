openmct.mainViews.addProvider({
    name: 'my view',
    canView: function (d) {
        return d.type === 'folder' && 150;
    },
    view: function (domainObject) {
        return {
            show: function (container) {
                container.innerHTML = '<div> Congratulations, this is a view of: ' + domainObject.name + '</div>';
            },
            destroy: function (container) {

            }
        }
    }
});
