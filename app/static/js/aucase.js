// Map the actors object to HTML option
function mapActors(actors) {
    var res = "";
    actors.forEach(function (actor){
        var id_ = actor['id'];
        var first_name = actor['first_name'];
        var last_name = actor['last_name'];
        res += '<option value="'+ id_ + '">' + (first_name === "" ? "" : first_name + " ") + last_name + "</option>\n";
    });
    return res;
}

var AUCASE = {
    searchXhR: null,
    params: null,
    // Initialize all the form items
    init: function() {
        // Throttle prevents research spamming when typing
        $('#objectsearch').keyup(jQuery.throttle(400, function() {
            AUCASE.search(!0);
        }));
        $('#sectioncategorysearch').keyup(jQuery.throttle(400, function() {
            AUCASE.search(!0);
        }));
        $('#sectionauthorsearch').keyup(jQuery.throttle(400, function() {
            AUCASE.search(!0);
        }));

        // Initialize the pagination
        $('#resultspages-top,#resultspages-bottom').pagination({
            items: 0,
            itemsOnPage: 20,
            displayedPages: 5,
            edges:1,
            useAnchors: false,
            prevText: "&laquo",
            nextText: "&raquo",
            listStyle: 'pagination',
            onPageClick: function() {
                AUCASE.search(!0);
            }
        });

        // Populate the experts dropdown
        $.ajax({
            method: "POST",
            url: "/api?experts",
            contentType: 'application/json',
            beforeSend: function (e,t) {
                $("#expertsdropdown").prop("disabled", true);
            }
        }).done(function (data) {
            $('#expertsdropdown').prop("disabled", false);
            $('#expertsdropdown').html(
                mapActors(data)
            );
            $('#expertsdropdown').selectpicker('refresh');
            $('#expertsdropdown').on('change', function() {
                AUCASE.search(!0);
            });
        }).fail(function(e) {
            console.log("Error", e);
        });

        // Populate the commissaires dropdown
        $.ajax({
            method: "POST",
            url: "/api?commissaires",
            contentType: 'application/json',
            beforeSend: function (e,t) {
                $("#commissairesdropdown").prop("disabled", true);
            }
        }).done(function (data) {
            $('#commissairesdropdown').prop("disabled", false);
            $('#commissairesdropdown').html(
                mapActors(data)
            );
            $('#commissairesdropdown').selectpicker('refresh');
            $('#commissairesdropdown').on('change', function() {
                AUCASE.search(!0);
            });
        }).fail(function(e) {
            console.log("Error", e);
        });

        // Initialize the start date picker
        $('#datetimepicker1').datepicker({
            autoclose: true,
            format: 'dd/mm/yyyy',
            startDate: '01/01/1939',
            endDate: '31/12/1945',
            clearBtn: true,
            defaultViewDate: '01/01/1939',
            disableTouchKeyboard: true,
            maxViewMode: "decade",
            language: 'fr'
        });

        // Initialize the end date picker
        $('#datetimepicker2').datepicker({
            autoclose: true,
            format: 'dd/mm/yyyy',
            startDate: '01/01/1939',
            endDate: '31/12/1945',
            clearBtn: true,
            defaultViewDate: '31/12/1945',
            disableTouchKeyboard: true,
            maxViewMode: "decade",
            language: 'fr'
        });

        // Logic to make the start and end date interact nicely
        $('#datetimepicker1').datepicker().on('changeDate', function(e){
            $("#datetimepicker2").datepicker('setStartDate', e.date);
            AUCASE.search(!0);
        });
        $('#datetimepicker1').datepicker().on('clearDate', function(e){
            $("#datetimepicker2").datepicker('setStartDate', '01/01/1939');
        });
        $('#datetimepicker2').datepicker().on('changeDate', function(e){
            $("#datetimepicker1").datepicker('setEndDate', e.date);
            AUCASE.search(!0);
        });
        $('#datetimepicker2').datepicker().on('clearDate', function(e){
            $("#datetimepicker1").datepicker('setEndDate', '31/12/1945');
        });

        // Callback when the sort-order changes
        $('#sortorder').on('change', function() {
            AUCASE.search(!0);
        });

        AUCASE.search(!0);
    },
    // Search function that calls the API
    search: function(e) {
        // Initalize the request params and make sure that no other ajax query
        // is currently running, if yes abort it.
        e && AUCASE.initRequestParams(),
        AUCASE.searchXhR && 4 != AUCASE.searchXhR.readystate && AUCASE.searchXhR.abort(),
        // Make the POST query to the API
        AUCASE.searchXhR = $.ajax({
            method: "POST",
            url: '/api?search',
            data: JSON.stringify(AUCASE.params),
            contentType: 'application/json',
            dataType: 'json',
            beforeSend: function (e, t) {
                // Show that the results are loading.
                $('#results-spinner').css({"display": ""});
                $('#no-results').css({"display": "none"});
                $('#resultcontainer').html("");
                $("#resultspages-top, #resultspages-bottom").css({"display": "none"});
            }
        }).done(function (data) {
            // Display the results, the API directly returns the necessary HTML
            $('#results-spinner').css({"display": "none"});
            $('#resultcontainer').html(data['html']);
            var results_count = data['results_count'] ? data['results_count'] : 0;
            $("#resultspages-top, #resultspages-bottom").pagination("updateItems", results_count);
            if (results_count == 0) {
                $('#resultsCount').html("");
                $('#no-results').css({"display": ""});
            } else {
                $('#no-results').css({"display": "none"});
                $("#resultspages-top, #resultspages-bottom").css({"display": ""});
                if (results_count == 1){
                    $('#resultsCount').html("1 objet trouvé");
                } else {
                    $('#resultsCount').html(results_count.toString() + " objets trouvés");
                }
            }
        }).fail(function(e) {
            console.log("Error", e);
        });
    },
    // Grab from the different form items the search parameters
    initRequestParams: function() {
        return AUCASE.params = {
            actors: Array.from(new Set($("#expertsdropdown").val().concat($("#commissairesdropdown").val()))).map(numStr => parseInt(numStr)),
            startdate: $("#datetimepicker1").datepicker('getDate'),
            enddate: $("#datetimepicker2").datepicker('getDate'),
            objectsearch: $('input#objectsearch').val(),
            sectionauthorsearch: $('input#sectionauthorsearch').val(),
            sectioncategorysearch: $('input#sectioncategorysearch').val(),
            sortingorder: $('#sortorder').val(),
            page: $("#resultspages-top").pagination('getCurrentPage'),
        },
        AUCASE.params;
    }
};
window.onload = function() {
    AUCASE.init();
};
