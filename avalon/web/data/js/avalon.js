(function() {

    var QUERY_MIN_LENGTH = 3;

    $('.typeahead').each(function(index, elm) {
        $(elm).typeahead({
            minLength: QUERY_MIN_LENGTH,
            source: function(query, process) {
                return $.get('/avalon/songs', {query: query}, function(data) {
                    if (data.is_error) {
                        console.log('Error fetching results ' + data.error_name + ': ' + data.error_msg);
                        return;
                    }

                    var results = [];
                    for (var i = 0; i < data.results.length; i++) {
                        results.push(data.results[i].name);
                    }

                    return process(results);
                });
            },
            updater: function(item) {
                return item;
            }
        });
    });
})();



