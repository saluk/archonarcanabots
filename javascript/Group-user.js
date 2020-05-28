//Edit Card Data
if($('.cardEntry').length>0) {
    var link = mw.config.values.wgPageName
    var link = '/CardData:'+link+'?action=edit'
    $('#p-cactions .menu').append('<li id="ca-carddata-link"><a href="'+link+'">Edit CardData</a></li>')
}

//Edit a template's CSS
if(mw.config.values.wgPageName.search('Template:')==0){
    var link = mw.config.values.wgPageName
    var link = '/'+link+'/styles.css?action=edit'
    $('#p-cactions .menu').append('<li id="ca-template-styles"><a href="'+link+'">Template Style</a></li>')
}

//Edit links for templates referenced in an edit box
var textbox = $('#wpTextbox1')
if(textbox.length>0){
    var text = textbox[0].value
    text.split('\n').map(function(line){
        var regtname = /\{\{\w(.\*?)(\||$|\}\})/
        var tname = line.match(regtname)
        if(tname){
          tname = tname[1]
          var link = '/Template:'+tname+'?action=edit'
          $('#p-cactions .menu').append('<li id="ca-template-edit"><a href="'+link+'">Edit Template '+tname+'</a></li>')
        }

        var regtname = /\|template=(.*)/
        var tname = line.match(regtname)
        if(tname){
          tname = tname[1]
          var link = '/Template:'+tname+'?action=edit'
          $('#p-cactions .menu').append('<li id="ca-template-edit"><a href="'+link+'">Edit Template '+tname+'</a></li>')
        }
    })
}