function mapActors(actors) {
    var res = "";
    actors.forEach(function (actor){
        var first_name = actor[0];
        var last_name = actor[1];
        res += '<option value="'+ first_name+ '/'+ last_name +'">' + (first_name === "" ? "" : first_name + " ") + last_name + "</option>\n";
    });
    return res;
}

var AUCASE = {
    searchXhR: null,
    params: null,
    init: function() {
        $('#objectsearch').keyup(jQuery.throttle(400, function() {
            AUCASE.search(!0);
        }));
        $('#sectionsearch').keyup(jQuery.throttle(400, function() {
            AUCASE.search(!0);
        }));
        $('#resultspages-top,#resultspages-bottom').pagination({
            items: 0,
            itemsOnPage: 20,
            displayedPages: 5,
            edges:1,
            prevText: "&laquo",
            nextText: "&raquo",
            listStyle: 'pagination',
            onPageClick: function() {
                AUCASE.search(!0);
            }
        });
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
        $('#sortorder').on('change', function() {
            AUCASE.search(!0);
        });

        AUCASE.search(!0);
    },
    search: function(e) {
        e && AUCASE.initRequestParams(),
        AUCASE.searchXhR && 4 != AUCASE.searchXhR.readystate && AUCASE.searchXhR.abort(),
        AUCASE.searchXhR = $.ajax({
            method: "POST",
            url: '/search',
            data: JSON.stringify(AUCASE.params),
            contentType: 'application/json',
            dataType: 'json',
            beforeSend: function (e, t) {
                $('#results-spinner').css({"display": ""});
                $('#no-results').css({"display": "none"});
                $('#resultcontainer').html("");
                $("#resultspages-top, #resultspages-bottom").css({"display": "none"});
            }
        }).done(function (data) {
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
            //AUCASE.loadImages();
        }).fail(function(e) {
            console.log("Error", e);
        })
    },
    //loadImages: function() {
    //    $(".object-image").each(function (){
    //        var objectImage = $(this);
    //        console.log(objectImage);
    //        var width = Math.round(objectImage.width());
    //        var url = objectImage.data('url-prefix');
    //        url = url + '/' + width + ',/0/default.jpg';
    //        objectImage.replaceWith('<img src="' + url + '" class="card-img-top">');
    //    });
    //},
    initRequestParams: function() {
        return AUCASE.params = {
            experts: $("#expertsdropdown").val(),
            commissaires: $("#commissairesdropdown").val(),
            startdate: $("#datetimepicker1").datepicker('getDate'),
            enddate: $("#datetimepicker2").datepicker('getDate'),
            objectsearch: $('input#objectsearch').val(),
            sectionsearch: $('input#sectionsearch').val(),
            sortingorder: $('#sortorder').val(),
            page: $("#resultspages-top").pagination('getCurrentPage'),
        },
        AUCASE.params
    }
};
window.onload = function() {
    AUCASE.init();
};
