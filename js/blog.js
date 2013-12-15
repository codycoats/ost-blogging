$(function(){

  function limitPostView()
  {
    var total_posts = $('#post-list').data('posttotal');
    console.log(total_posts);

    var page_index = $('#post-list').data('pageindex');
    console.log(page_index);

    //hide all posts
    $('.list-group-item').hide();

    var post_max = page_index * 10 + 1;
    var post_min = post_max - 10;

    //show only those within current page range
    for( var i = post_min; i< post_max; i++)
    {
      var curr_post = $('.list-group-item[data-postindex="'+(i+1)+'"]');
      curr_post.show();
    }
  }

  $('#post-page-prev').bind("click", function(){
    var currpage = $('#post-list').data('pageindex');
    var newpage = currpage - 1;
    $('#post-list').data('pageindex', newpage);
    limitPostView();
  });

  $('#post-page-next').bind("click", function(){
    var currpage = $('#post-list').data('pageindex');
    var newpage = currpage + 1;
    $('#post-list').data('pageindex', newpage);
    limitPostView();
  });

  limitPostView();

});
