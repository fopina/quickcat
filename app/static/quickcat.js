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
			"api/vote",
			{
				"url": $(this).data('url'),
				"category": $(this).data('category'),
			},
			function(data) {
				existing = $('div.card img').map(function(e, v){return v.src});
				image_id = $(this).data('image');
		  		for (i=0; i<data.length; i++) {
		  			if ($.inArray(data[i].url, existing) < 0) {
		  				update_image(card, data[i]);
					  	break;
					}
				}
				card.unblock();
			}
		);
	})

	$.getJSON( "/api/more", function( data ) {
	  for (i=0; i<data.length; i++) {
	  	update_image($('#id_image_' + i), data[i]);
	  }
	});
});