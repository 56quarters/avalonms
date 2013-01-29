(function() {

    'use strict';

    var QUERY_MIN_LENGTH = 3,
        MAX_ITEMS = 15,
        SORT_FIELD = 'name';

    $('.typeahead').each(function(index, elm) {
        $(elm).typeahead({
            items: MAX_ITEMS,
            minLength: QUERY_MIN_LENGTH,
            source: function(query, process) {
                return $.get('/avalon/songs', {query: query, order: SORT_FIELD}, function(data) {
                    if (data.is_error) {
                        console.log('Error fetching results ' + data.error_name + ': ' + data.error_msg);
                        return;
                    }

                    var allResults = {},
                        suggestResults = [],
                        suggestion = null;

                    for (var i = 0; i < data.results.length; i++) {
                        suggestion = data.results[i];
                        allResults[suggestion.id] = suggestion;
                        suggestResults.push(suggestion.artist + ' - ' + suggestion.name);
                    }

                    $(elm).data('results', allResults);
                    return process(suggestResults);
                });
            },
            updater: function(item) {

                return item;
            },

            matcher: function(item) {
                // Matching is done by the endpoint
                return true;
            }
        });
    });
})();



