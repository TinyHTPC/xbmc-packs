$(document).ready(function(){

    $.fn.showHideProviders = function() {
        $('.providerDiv').each(function(){
            var providerName = $(this).attr('id');
            var selectedProvider = $('#editAProvider :selected').val();

            if (selectedProvider+'Div' == providerName)
                $(this).show();
            else
                $(this).hide();

        });
    } 

    $.fn.addProvider = function (id, name, url, key, isDefault) {

        if (url.match('/$') == null)
            url = url + '/'

        var newData = [isDefault, [name, url, key]];
        newznabProviders[id] = newData;

        if (!isDefault)
        {
            $('#editANewznabProvider').addOption(id, name);
            $(this).populateNewznabSection();
        }

        if ($('#providerOrderList > #'+id).length == 0) {
            var toAdd = '<li class="ui-state-default" id="'+id+'"> <input type="checkbox" id="enable_'+id+'" class="provider_enabler" CHECKED> <a href="'+url+'" class="imgLink" target="_new"><img src="'+sbRoot+'/images/providers/newznab.gif" alt="'+name+'" width="16" height="16"></a> '+name+'</li>'

            $('#providerOrderList').append(toAdd);
            $('#providerOrderList').sortable("refresh");
        }

        $(this).makeNewznabProviderString();

    }
    
    $.fn.addAnyRssProvider = function (id, name, url) {

        var newData = [name, url];
        anyrssProviders[id] = newData;

        $('#editAAnyRssProvider').addOption(id, name);
        $(this).populateAnyRssSection();

        if ($('#providerOrderList > #'+id).length == 0) {
            var toAdd = '<li class="ui-state-default" id="'+id+'"> <input type="checkbox" id="enable_'+id+'" class="provider_enabler" CHECKED> <a href="'+url+'" class="imgLink" target="_new"><img src="'+sbRoot+'/images/providers/anyrss.png" alt="'+name+'" width="16" height="16"></a> '+name+'</li>'

            $('#providerOrderList').append(toAdd);
            $('#providerOrderList').sortable("refresh");
        }

        $(this).makeAnyRssProviderString();

    }

    $.fn.updateProvider = function (id, url, key) {

        newznabProviders[id][1][1] = url;
        newznabProviders[id][1][2] = key;

        $(this).populateNewznabSection();

        $(this).makeNewznabProviderString();
    
    }

    $.fn.deleteProvider = function (id) {
    
        $('#editANewznabProvider').removeOption(id);
        delete newznabProviders[id];
        $(this).populateNewznabSection();

        $('#providerOrderList > #'+id).remove();

        $(this).makeNewznabProviderString();

    }
    
    $.fn.updateAnyRssProvider = function (id, url) {
        anyrssProviders[id][1] = url;
        $(this).populateAnyRssSection();
        $(this).makeAnyRssProviderString();
    }

    $.fn.deleteAnyRssProvider = function (id) {
        $('#editAAnyRssProvider').removeOption(id);
        delete anyrssProviders[id];
        $(this).populateAnyRssSection();
        $('#providerOrderList > #'+id).remove();
        $(this).makeAnyRssProviderString();
    }

    $.fn.populateNewznabSection = function() {

        var selectedProvider = $('#editANewznabProvider :selected').val();

        if (selectedProvider == 'addNewznab') {
            var data = ['','',''];
            var isDefault = 0;
            $('#newznab_add_div').show();
            $('#newznab_update_div').hide();
        } else {
            var data = newznabProviders[selectedProvider][1];
            var isDefault = newznabProviders[selectedProvider][0];
            $('#newznab_add_div').hide();
            $('#newznab_update_div').show();
        }

        $('#newznab_name').val(data[0]);
        $('#newznab_url').val(data[1]);
        $('#newznab_key').val(data[2]);
        
        if (selectedProvider == 'addNewznab') {
            $('#newznab_name').removeAttr("disabled");
            $('#newznab_url').removeAttr("disabled");
        } else {

            $('#newznab_name').attr("disabled", "disabled");

            if (isDefault) {
                $('#newznab_url').attr("disabled", "disabled");
                $('#newznab_delete').attr("disabled", "disabled");
            } else {
                $('#newznab_url').removeAttr("disabled");
                $('#newznab_delete').removeAttr("disabled");
            }
        }

    }
    
    $.fn.makeNewznabProviderString = function() {

        var provStrings = new Array();
        
        for (var id in newznabProviders) {
            provStrings.push(newznabProviders[id][1].join('|'));
        }

        $('#newznab_string').val(provStrings.join('!!!'))

    }
    
    
    $.fn.populateAnyRssSection = function() {

        var selectedProvider = $('#editAAnyRssProvider :selected').val();

        if (selectedProvider == 'addAnyRss') {
            var data = ['',''];
            $('#anyrss_add_div').show();
            $('#anyrss_update_div').hide();
        } else {
            var data = anyrssProviders[selectedProvider];
            $('#anyrss_add_div').hide();
            $('#anyrss_update_div').show();
        }

        $('#anyrss_name').val(data[0]);
        $('#anyrss_url').val(data[1]);
        
        if (selectedProvider == 'addAnyRss') {
            $('#anyrss_name').removeAttr("disabled");
            $('#anyrss_url').removeAttr("disabled");
        } else {
            $('#anyrss_name').attr("disabled", "disabled");
            $('#anyrss_url').removeAttr("disabled");
            $('#anyrss_delete').removeAttr("disabled");
        }

    }
    
    $.fn.makeAnyRssProviderString = function() {

        var provStrings = new Array();
        
        for (var id in anyrssProviders) {
            provStrings.push(anyrssProviders[id].join('|||'));
        }

        $('#anyrss_string').val(provStrings.join('!!!'))

    }
    
    $.fn.refreshProviderList = function() {
            var idArr = $("#providerOrderList").sortable('toArray');
            var finalArr = new Array();
            $.each(idArr, function(key, val) {
                    var checked = + $('#enable_'+val).prop('checked') ? '1' : '0';
                    finalArr.push(val + ':' + checked);
            });

            $("#provider_order").val(finalArr.join(' '));
    }

    var newznabProviders = new Array();
    var anyrssProviders = new Array();

    $('.newznab_key').change(function(){

        var provider_id = $(this).attr('id');
        provider_id = provider_id.substring(0, provider_id.length-'_hash'.length);

        var url = $('#'+provider_id+'_url').val();
        var key = $(this).val();

        $(this).updateProvider(provider_id, url, key);

    });
    
    $('#newznab_key,#newznab_url').change(function(){
        
        var selectedProvider = $('#editANewznabProvider :selected').val();

		if (selectedProvider == "addNewznab")
			return;

        var url = $('#newznab_url').val();
        var key = $('#newznab_key').val();
        
        $(this).updateProvider(selectedProvider, url, key);
        
    });
    
    $('#anyrss_url').change(function(){
        
        var selectedProvider = $('#editAAnyRssProvider :selected').val();

		if (selectedProvider == "addAnyRss")
			return;

        var url = $('#anyrss_url').val();
        
        $(this).updateAnyRssProvider(selectedProvider, url);
    });
    
    $('#editAProvider').change(function(){
        $(this).showHideProviders();
    });

    $('#editANewznabProvider').change(function(){
        $(this).populateNewznabSection();
    });

    $('#editAAnyRssProvider').change(function(){
        $(this).populateAnyRssSection();
    });
    
    $('.provider_enabler').live('click', function(){
        $(this).refreshProviderList();
    }); 
    

    $('#newznab_add').click(function(){
        
        var selectedProvider = $('#editANewznabProvider :selected').val();
        
        var name = $('#newznab_name').val();
        var url = $('#newznab_url').val();
        var key = $('#newznab_key').val();
        
        var params = { name: name }
        
        // send to the form with ajax, get a return value
        $.getJSON(sbRoot + '/config/providers/canAddNewznabProvider', params,
            function(data){
                if (data.error != undefined) {
                    alert(data.error);
                    return;
                }

                $(this).addProvider(data.success, name, url, key, 0);
        });


    });

    $('.newznab_delete').click(function(){
    
        var selectedProvider = $('#editANewznabProvider :selected').val();

        $(this).deleteProvider(selectedProvider);

    });
    
    
    $('#anyrss_add').click(function(){
        var selectedProvider = $('#editAANyRssProvider :selected').val();
        
        var name = $('#anyrss_name').val();
        var url = $('#anyrss_url').val();
        var params = { name: name, url: url }
        
        // send to the form with ajax, get a return value
        $.getJSON(sbRoot + '/config/providers/canAddAnyRssProvider', params,
            function(data){
                if (data.error != undefined) {
                    alert(data.error);
                    return;
                }

                $(this).addAnyRssProvider(data.success, name, url);
        });
    });

    $('.anyrss_delete').click(function(){
    
        var selectedProvider = $('#editAAnyRssProvider :selected').val();
        $(this).deleteAnyRssProvider(selectedProvider);
    });

    // initialization stuff

    $(this).showHideProviders();

    $("#providerOrderList").sortable({
        placeholder: 'ui-state-highlight',
        update: function (event, ui) {
            $(this).refreshProviderList();
        }
    });

    $("#providerOrderList").disableSelection();

});