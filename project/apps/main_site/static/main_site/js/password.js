$(function(){
    $("#show_password").click(function(){
        if ($(".password input:first").attr("type") == "text") {
            $(".password input[type=text]").attr("type", "password");
        } else {
            $(".password input[type=password]").attr("type", "text");
        }
    });
});
