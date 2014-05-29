
var runningTorrentPollFreq = 5; //	secs

function torrentSortFunc(a, b) {
	var a_sort = a && a.start_time || -1,
    	b_sort = b && b.start_time || -1;
	return a_sort - b_sort;
};

function createRowForTorrent(tKey) {
	var r = $('<tr id="row_' + tKey + '" class="torrent_row" data-key="' + tKey + '">' +
			'<td id="delete_' + tKey + '"><a href="#" onclick="deleteTorrent(\'' + tKey + '\'); return false;"><img src="' +
	    		sbRoot + '/images/cancel.png" style="width: 16px; height: 16px" title="Cancel/Delete this torrent" /></a></td>' +
		    '<td id="name_' + tKey + '"></td>' +
		    '<td id="status_' + tKey + '" class="nowrap" align="center"></td>' +
		    '<td id="size_' + tKey + '" align="right"></td>' +
		    '<td><div id="progress_container_' + tKey + '" class="torrent_progress">' +
		    	'<div id="progress_' + tKey + '" class="torrent_progress_bar"></div>' +
		    	'<div id="progress_text_' + tKey + '" class="torrent_progress_text"></div></div></td>' +
		    '<td id="ratio_' + tKey + '" align="right"></td>' +
		    '<td id="speeds_' + tKey + '" align="center"></td>' +
		  '</tr>');
	$('#downloadsTableBody').append(r);
	return r;
}

function deleteTorrent(tKey) {
	var torrentInfo = null;
	for (var i=0; i<displayedDownloads.length; i++) {
	    if (displayedDownloads[i]['key'] == tKey) torrentInfo = displayedDownloads[i];
	}
	if (torrentInfo && confirm('Delete the torrent "' + torrentInfo['name'] + '"?')) {
		$('#row_' + tKey).remove();
		$.ajax({ 
				url: sbRoot + '/downloads/deleteTorrent',
				data: { key: tKey }
		}).done(function ( data ) {
			if (data.error) {
				alert(data.errorMessage);
			} else {
				$('#row_' + tKey).remove();
			}
		});
	}
}

function addTorrent() {
    var tag = $("#dialogHolder");
    if(!tag.length)
        tag = $("<div id='dialogHolder'></div>");
	$.ajax({
		url: sbRoot + '/downloads/dlgAddTorrent',
		type: 'GET',
		beforeSend: function() {},
		error: function() {},
		complete: function() {},
		success: function(data, textStatus, jqXHR) {
			tag.html(data).dialog({
				modal: true, 
				resizable: false,
				width: 500,
				title: 'Add Torrent',
				buttons: {
					'Add Torrent': function() {
						doAddTorrent(this);
					},
					'Cancel': function() { $(this).dialog('close'); }
				},
			});
		}
	});
}

var displayedDownloads = null;

(function updateRunningTorrents() {
    $.ajax({
        url: sbRoot + '/downloads/getRunningTorrents',
        type: "GET",
        success: function(data) {
        	//console.log(data);
        	runningTorrentPollFreq = data.length ? 5 : 15;	// every 5 secs while downloading, 15 secs otherwise
        	if (data.length > 1) data.sort(torrentSortFunc);
        	
        	displayedDownloads = data;
        	
        	var displayedKeys = [];
        	$('.torrent_row').each(function(i, r) { displayedKeys.push($(r).attr('data-key')); });
        	
        	$.each(data, function(i, t) {
        		//console.log(t);
        		
        		if (!$('#row_' + t['key']).length) {
        			createRowForTorrent(t['key']);
        		} else {
        			displayedKeys.splice($.inArray(t['key'], displayedKeys), 1);
        		}
        		
        		var possible_statuses = ['added', 'checking_resume_data', 'queued_for_checking',
        		                         'checking_files', 'downloading_metadata',
        		                         'downloading', 'finished',
        		                         'seeding', 'allocating'];
        		

        		var combined_status = t['paused'] ? t['status'] + ' (Paused)' : t['status'];
        		
        		var not_statuses = [];
        		for (var i=0; i<possible_statuses.length; i++) {
        		    if (possible_statuses[i] != t['status']) not_statuses.push(possible_statuses[i]);
        		}
        		
        		$('#name_' + t['key']).text(t['name']);
        		$('#status_' + t['key']).text(combined_status);
        		$('#size_' + t['key']).text((t['total_size'] / (1024 * 1024)).toFixed(1) + ' MB');
        		if (t['progress'] >= 0.0) {
        			$('#progress_text_' + t['key']).text((t['progress'] * 100.0).toFixed(1) + '%')
	        		$('#progress_' + t['key'])
	        			.removeClass(not_statuses.join(' ')).addClass(t['status'])
	        			.css('width', (t['progress'] * 100.0) + '%');
        		} else {
        			$('#progress_text_' + t['key']).text('Unknown')
        			$('#progress_' + t['key'])
        				.removeClass(possible_statuses.join(' '))
        				.css('width', '100%');
        		}
        		$('#ratio_' + t['key']).text(t['ratio'].toFixed(3));
        		var rate_up = (t['rate_up'] >= 0) ? (t['rate_up']/1024).toFixed(1) + 'kB' : '???';
        		var rate_down = (t['rate_down'] >= 0) ? (t['rate_down']/1024).toFixed(1) + 'kB' : '???';
        		$('#speeds_' + t['key']).html('&darr;' + rate_down + '&nbsp;&nbsp;&uarr;' + rate_up);
        	});
        	
        	//	remove any torrents that we no longer have
        	$.each(displayedKeys, function(i, k) {
        		$('#row_' + k).remove();
        	});
        	
        	//	Update the number in the menu
        	$('#NAVdownloads > a').text('Downloads' + (data.length > 0 ? ' (' + data.length + ')' : ''));
        },
        dataType: "json",
        complete: setTimeout(updateRunningTorrents, runningTorrentPollFreq * 1000),
        timeout: 2000
    });
})();





