$(function(){

  function limitPostView()
  {
    var total_posts = $('#post-list').data('posttotal');
    console.log(total_posts);

    var page_index = $('#post-list').data('pageindex');

    //if pageindex -1 show all posts
    if (page_index === -1){
      console.log("limitPostView - show all");
      $('.list-group-item').hide().toggle();
    }

    //hide all posts
    $('.list-group-item').hide();

    var post_begin = (page_index * 10) + 1;
    var post_end = post_begin + 10;

    console.log("post_begin " + post_begin);
    console.log("post_end " + post_end);

    //show only those within current page range
    for( var i = post_begin; i < post_end; i++){
      var curr_post = $('.list-group-item[data-postindex="'+(i)+'"]');
      curr_post.show();
    }

    //correct prev/next button
    if (post_begin === 1){
      $('#post-page-prev').addClass('disabled');
    }
    else{
      $('#post-page-prev').removeClass('disabled');
    }

    if(post_end >= total_posts){
     $('#post-page-next').addClass('disabled');
    }
    else{
      $('#post-page-next').removeClass('disabled');
    }

  }

  $('#post-page-prev').on("click", function(){
    var currpage = $('#post-list').data('pageindex');
    var newpage = currpage - 1;
    $('#post-list').data('pageindex', newpage);
    limitPostView();
  });

  $('#post-page-next').on("click", function(){
    var currpage = $('#post-list').data('pageindex');
    var newpage = currpage + 1;
    $('#post-list').data('pageindex', newpage);
    limitPostView();
  });

  limitPostView();

});
