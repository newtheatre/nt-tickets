// AJAX for posting
function create_post() {
  console.log("create post is working!") // sanity check before AJAX
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
    success : function(data) {
      // Reset sale form
      $("#sale-form")[0].reset();
      // Update sale overview
      $('#sale-update').html($('#div-1', data).html());
      $('#sale-final').html($('#div-2', data).html());
      console.log("success"); // sanity check after AJAX
      console.log(data);
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });
};