function signInCallback(authResult) {
  if (authResult['code']) {
    // Send the one-time-use code to the server,
    // if the server responds, write a 'login successful'
    // message to the web page and then redirect back to the
    // main page
    $.ajax({
      type: 'POST',
      url: '/gconnect?state=' + STATE,
      processData: false,
      data: authResult['code'],
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
          // Handle or verify the server response if necessary.
          if (result) {
              $('.login-choice').hide()
              $('.flash').html('Login Successful! Redirecting...')
              $('#result').html(result)
              setTimeout(function() {
                  window.location.href = RETURN_URL;
              }, 4000);
          } else if (authResult['error']) {
              console.log('There was an error: ' + authResult['error']);
              } else {
                    $('#result').html('Failed to make a server-side call.\
                                      Check your configuration and console.');
                     }
      }
  }); } }
      // END GOOGLE PLUS SIGN IN

$(document).ready(function(){
    // constants
    window.STATE = $("input[name='state']").val();
    window.RETURN_URL = $("input[name='return_url']").val();

   // FACEBOOK SIGN IN
    window.fbAsyncInit = function() {
    FB.init({
      appId      : '846524132078825',
      cookie     : true,  // enable cookies to allow the server to access
                          // the session
      xfbml      : true,  // parse social plugins on this page
      version    : 'v2.2' // use version 2.2
    });

    };

    // Load the SDK asynchronously
    (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/en_US/sdk.js";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));

    // Here we run a very simple test of the Graph API after login is
    // successful.  See statusChangeCallback() for when this call is made.
    function sendTokenToServer() {
      var access_token = FB.getAuthResponse()['accessToken'];
      console.log(access_token)
      console.log('Welcome!  Fetching your information.... ');
      FB.api('/me', function(response) {
        console.log('Successful login for: ' + response.name);
       $.ajax({
        type: 'POST',
        url: '/fbconnect?state=' + STATE,
        processData: false,
        data: access_token,
        contentType: 'application/octet-stream; charset=utf-8',
        success: function(result) {
          // Handle or verify the server response if necessary.
          if (result) {
              $('.login-choice').hide()
            $('#result').html('Login Successful!</br>'+ result +
                              '</br>Redirecting...')
           setTimeout(function() {
            window.location.href = RETURN_URL;
           }, 4000);


        } else {
          $('#result').html('Failed to make a server-side call.\
                            Check your configuration and console.');
           }

        }

    });


      });
    }
});
