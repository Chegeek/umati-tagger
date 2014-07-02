function createTagSession() {

	if ($('#tag-question').val() == '') {
		return;
	}

	var count = $('#taggers-table tbody tr').length;
	console.log(count)

	if (count < 1) {
		return;
	}

	var TAGGERS = {'tag_qid': 1,
					'tag_qst': $('#tag-question').val(),
					'key_options': {'y': 'YES', 'n': 'NO', 'm': 'Maybe'},
					'taggers': []
				}
	
	$('#taggers-table tbody tr').each(function(){
		TAGGERS['taggers'].push({'user_to_tag': $(this).children('.tname')[0].innerText, 'user_email': $(this).children('.temail')[0].innerText, 'number_to_tag': parseInt($(this).children('.tnum')[0].innerText)})
	});


	console.log(TAGGERS)
	var sessionsData = {'sessionsObject' : JSON.stringify({'taggers_info': TAGGERS})}
	
	// $.ajax({
	// 	url: 'create',
	// 	type: 'POST',
	// 	data: sessionsData,
	// 	dataType: "json"
	// }).success(function (data) {
	// 	console.log(data);
	// });
}

function addUser() {

	var textBox;
	console.log('Tapinda v2')
	$('#create-taggers .reqText').each(function(){
	    if ($(this).val() == '') {
	      // Get the current textBox
	      textBox = $(this)
	      // Exit loop we
	      return false;
	
	    }
	})

	// Check to see if this we have an empty textBox. 
	if (textBox) {
	  // Give focus to the empty textBox.
	  textBox.focus();
	  // document.getElementById(currentDiv+'Lbl').style.display='block'
	  return;
	}

	$('#taggers-table').append('<tr id="tagger_row"><td class ="edit-tagger tname">'+ $('#tagger-name').val() +'</td><td class ="edit-tag temail">' 
		+ $('#tagger-email').val() +'</td><td class ="edit-tag tnum">' + $('#number-to-tag').val() +'</td></tr>');	

}
