/*
    Using the widget

    // Put this script somewhere on yourpage
    <script type="text/javascript" src="https://archonarcana.com/MediaWiki:cardwidget.js?action=raw&ctype=text/javascript"></script>
    
    // Put this script where you want to embed Jargogle
    <script type="text/javascript">
            renderCardLink("https://archonarcana.com/images/thumb/2/2c/452-153.png/300px-452-153.png", "Jargogle");
    </script>
    <div id="renderCardWidget_Jargogle"></div>
*/

function ShowDiv(evt, title) {
    // SHOW THE DIV WITH DESCRIPTIONS NEXT TO THE SELECTED GRIDVIEW ROW.

    var id = 'floating'+title;

    document.getElementById(id).style.display = 'block';
    document.getElementById(id).innerHTML = "";
    document.getElementById(id).style.top = evt.pageY + 'px';
    document.getElementById(id).style.left = evt.pageX + 50 + 'px';
    document.getElementById(id).style.backgroundColor = 'rgb(255,255,255)';
    document.getElementById(id).style.padding = '4px';
    document.getElementById(id).style.borderStyle = 'solid';
    document.getElementById(id).style.borderWidth = '1px';
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            document.getElementById(id).innerHTML = '\
<div style="float:left;width:250px">' + json['query']['pages'][0]['extract'] + '</div>\
<div style="float:left"><img alt="'+title+'" src="\
'+json['query']['pages'][0]['thumbnail']['source']+'" \
width="'+json['query']['pages'][0]['thumbnail']['width']+'" \
height="'+json['query']['pages'][0]['thumbnail']['height']+'"></div>';
        }
    };
    req.open('GET', 'https://archonarcana.com/api.php?action=query&format=json&\
origin='+window.location.origin+'&\
prop=info|extracts|pageimages|revisions|info&\
formatversion=2&redirects=true&exintro=true&exchars=525&\
explaintext=true&piprop=thumbnail&pithumbsize=320&pilicense=any&\
rvprop=timestamp&inprop=url&titles='+title+'&\
smaxage=300&maxage=300&uselang=content');
    //req.withCredentials = true;
    req.send();
}

function HideDiv(evt, title) { 
    var id = 'floating'+title;
    document.getElementById(id).style.display = 'none'; 
}

function renderCardLink(image, name) {
    var root = document.currentScript.parentElement;
    var el = document.createElement('div');
    var content = [
        '<div class="arcanabox">',
        '<a href="https://archonarcana.com/'+name+'?ref=',
        encodeURIComponent(window.location.href),
        '" onmouseenter="ShowDiv(event, \''+name+'\')"',
        ' onmouseleave="HideDiv(event, \''+name+'\')">',
        '<img src="'+image+'" width=40 height=60>'+name+', from Archon Arcana',
        '</a>',
        '<div id="floating'+name+'" class="floatingArcanaBox" ',
        'style="display:none;float:left;position:absolute">',
        "text",
        '</div></div>'
    ];
    el.innerHTML = content.join('');
    root.textContent = '';
    root.append(el);
}