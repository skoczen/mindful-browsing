$(function(){
    $(".home_buttons .button.readers").click(function(){
        // Maaaan this brings me back to 2006-style.
        $(".home_buttons .button").removeClass("current");
        $(this).addClass("current");
        $(".detail_section").hide();
        $(".detail_section.for_readers").show();
        return false;
    });
    $(".home_buttons .button.writers").click(function(){
        $(".home_buttons .button").removeClass("current");
        $(this).addClass("current");
        $(".detail_section").hide();
        $(".detail_section.for_writers").show();
        return false;
    });
    $(".home_buttons .button.manifesto").click(function(){
        $(".home_buttons .button").removeClass("current");
        $(this).addClass("current");
        $(".detail_section").hide();
        $(".detail_section.the_manifesto").show();
        return false;
    });
    $(".home_buttons .button.faq").click(function(){
        $(".home_buttons .button").removeClass("current");
        $(this).addClass("current");
        $(".detail_section").hide();
        $(".detail_section.the_faq").show();
        return false;
    });
});
