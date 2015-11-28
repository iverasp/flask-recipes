active_tags = []
var RECIPES_PER_PAGE = 3
var number_of_recipes = 0
var page = 0
$(window).on('load', function () {
  //$('#prev-button > a').attr('disabled', true)
  update_frontpage(page)
  $('#tag-group > label > input:checkbox').change( function() {
    if ($(this).prop('checked')) {
      var tag = $(this).attr('id');
      active_tags.push(tag)
    } else {
      active_tags.splice( $.inArray(tag, active_tags), 1);
    }
    page = 0
    update_frontpage(page, active_tags)
  })
});

var update_frontpage = function(page, tags) {
  if (tags == undefined) { search_tags = [] }
  else { search_tags = tags }
  console.log(search_tags)
  var params = {
    start: page * RECIPES_PER_PAGE,
    end: RECIPES_PER_PAGE * (page + 1),
    tags: search_tags
  }
  $.ajax({
    url: '/cook/api/recipe',
    data: $.param(params, true),
    success: function(data) {
      console.log(data)
      $('#recipes-group').empty()
      number_of_recipes = data.length
      $('#recipe-count').html(number_of_recipes)
      $.each(data.result, function(index, value) {
        console.log(value)
        var html = ''
        html += '<h2><a href="/cook/recipe/' + value.id + '">' + value.name + '</a></h2>'
        html += '<small>Added:' + value.date + '</small>'
        html += '<h5>Ingredients</h5>'
        html += '<p style="white-space:pre-wrap;">' + value.ingredients + '</p>'
        html += '<h5>Instructions</h5>'
        html += '<p style="white-space: pre-wrap;">' + value.instructions + '</p>'
        $('<div></div>')
        .addClass('col-md-4 col-md-height')
        .html(html)
        .appendTo('#recipes-group');
      })
    }
  })
}

var number_of_pages = function() {
  return Math.ceil(number_of_recipes / RECIPES_PER_PAGE)
}

var update_page = function(n) {
  if (n == -1 && page == 0) {
    return
  }
  if (page + n < number_of_pages()) {
    page += n
    update_frontpage(page, active_tags)
  }

  /**
  // update button states
  if (page == 0) {
    $('#prev-button > a').attr('disabled', true)
  } else {
    $('#prev-button > a').attr('disabled', false)
  }
  console.log('page', page, 'total', number_of_pages())
  if (page -1  == number_of_pages()) {
    $('#next-button > a').attr('disabled', true)
  } else {
    $('#next-button > a').attr('disabled', false)

  }
  **/

}
