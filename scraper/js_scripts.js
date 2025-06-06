(function() {
    var polygons = [];
    if (typeof myMap === 'undefined') {
        return {error: 'myMap is not defined'};
    }
    myMap.geoObjects.each(function(geoObject) {
        if (geoObject.geometry && geoObject.geometry.getType() === 'Polygon') {
            polygons.push({
                name: geoObject.properties.get('name') || 'Без имени',
                coords: geoObject.geometry.getCoordinates()
            });
        }
    });
    return polygons;
})();