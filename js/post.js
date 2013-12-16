$(function(){

  $("a[href$='.png'], a[href$='.jpg'], a[href$='.tiff'], a[href$='.gif']").each(function() {
    var img = $('<img>',{src: this.href});
    img.height(128);
    img.width(128);
    $(this).replaceWith(img);
  });

  //ggpht is for live, _ah is for dev
  $("a[href*='ggpht'], a[href*='_ah/img/']").each(function() {
    console.log("hello");
    var img = $('<img>',{src: this.href});
    $(this).replaceWith(img);
  });

});
