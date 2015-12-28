// AJAX for posting
function create_post() {
    console.log("create post is working!") // sanity check
    $.ajax({
        url : "sale/", // the endpoint
        type : "POST", // http method
        data : { 
          number_member : $('#member').val(),
          number_concession : $('#concession').val(),
          number_public : $('#public').val(),
          number_fringe : $('#fringe').val(),
          number_matinee_freshers : $('#matinee_freshers').val(),
          number_matinee_freshers_nnt : $('#matinee_freshers_nnt').val(),
          number_season : $('#season').val(),
          number_fellow : $('#fellow').val(),
          number_season_sales : $('#season_sales').val(),
          unique_ticket : $('#unique_ticket').val(),
          reservation: $('#reservation').val()
          }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            // remove the value from the input
            $('#member').val('0');
            $('#concession').val('0');
            $('#public').val('0');
            $('#fringe').val('0');
            $('#matinee_freshers').val('0');
            $('#matinee_freshers_nnt').val('0');
            $('#season').val('0');
            $('#fellow').val('0');
            $('#season_sales').val('0');
            $('#unique_ticket').val('0');
            $('#reservation').val('None');
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};