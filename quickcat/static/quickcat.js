function update_image(card, data) {
	$('.review_number', card).text(data.reviews || 0);
  	$('img', card).attr('src', data.url);
  	$('button', card).data('url', data.url);
}

$(function() {
	$('div.card button').click(function () {
		card = $(this).parents('div.card');
		card.block({message: 'Processing...'}); 
		$.post(
			'api/vote',
			{
				'url': $(this).data('url'),
				'category': $(this).data('category'),
			},
			function(data) {
				$('#counter_left').text(data['left']);
				existing = $('div.card img').map(function(e, v){return v.src});
				image_id = $(this).data('image');
		  		for (i=0; i<data['pics'].length; i++) {
		  			if ($.inArray(data['pics'][i].url, existing) < 0) {
		  				update_image(card, data['pics'][i]);
					  	break;
					}
				}
				card.unblock();
			}
		);
	})

	$.getJSON( '/api/more', function( data ) {
		$('#counter_left').text(data['left']);
	  	for (i=0; i<data['pics'].length; i++) {
	  		update_image($('#id_image_' + i), data['pics'][i]);
	  	}
	});
});