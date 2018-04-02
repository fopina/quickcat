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
						$('.review_number', card).text(data[i].reviews || 0);
					  	$('img', card).attr('src', data[i].url);
					  	$('button', card).data('url', data[i].url);
					  	break;
					}
				}
				card.unblock();
			}
		);
	})

	$.getJSON( "/api/more", function( data ) {
	  for (i=0; i<data.length; i++) {
	  	$('#id_image_' + i + ' .review_number').text(data[i].reviews || 0);
	  	$('#id_image_' + i + ' img').attr('src', data[i].url);
	  	$('#id_image_' + i + ' button').data('url', data[i].url);
	  }
	});
});