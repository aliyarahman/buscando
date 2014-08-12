function readURL(input)
{
	if (input.files && input.files[0])
  {
    var reader = new FileReader();
    reader.onload = function (e)
    {
      $('#logo')
      .attr('src',e.target.result)
      .width(200)
      .show()
    };
   reader.readAsDataURL(input.files[0]);
   }
}

$('.add-row').click(function() {
  return addForm(this, 'form');
});
$('.delete-row').click(function() {
  return deleteForm(this, 'form');
})

function updateElementIndex(el, prefix, ndx) {
  var id_regex = new RegExp('(' + prefix + '-\\d+)');
  var replacement = prefix + '-' + ndx;
  if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
  if (el.id) el.id = el.id.replace(id_regex, replacement);
  if (el.name) el.name = el.name.replace(id_regex, replacement);
}
 
function addForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('.dynamic-form:first').clone(true).get(0);
    $(row)
      .removeAttr('id')
      .attr('id','form-'+formCount+'-row')
      .insertAfter($('.dynamic-form:last'))
      .children('.hidden').removeClass('hidden'); // show remove link
    $(row).find('input').each(function() {
      updateElementIndex(this, prefix, formCount); // formCount should be the newest ID
      $(this).val('');
    });
    $(row).find('label').each(function() {
      updateElementIndex(this, prefix, formCount); // formCount should be the newest ID
    });
    $(row).find('.delete-row').click(function() {
      deleteForm(this, prefix);
    });
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    return false;
}

function deleteForm(btn, prefix) {
    $(btn).parents('.dynamic-form').remove();
    var forms = $('.dynamic-form');
    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
    for (var i=0, formCount=forms.length; i<formCount; i++) {
      $(forms.get(i)).children().not(':last').children().each(function() {
          updateElementIndex(this, prefix, i);
      });
    }
    return false;
}

$('.landing--need').chosen({ width: '100%', disable_search_threshold: 20 });
$('.resource-form--need')
    .chosen({ width: '100%', disable_search_threshold: 20 })
    .change(function () {
        if ($('.resource-form--panel #location').val() != '') {
            $('form').submit();
        }
    });

$(document).on('change', '.resource-form--panel #location', function () {
    if ($('.resource-form--need').val() != '') {
        $('form').submit();
    }
});

$('.resource-form--panel #location').keypress(function (e) {
    if (e.which == 13) {
        $('form').submit();
    }
});

$('.landing--location').tooltip({});
$('#location').tooltip({});