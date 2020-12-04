function renderCardLink(image, name) {
    console.log('rendering');
    var el = document.createElement('div');
    var content = [
        '<div class="arcanabox">',
        '<a href="https://archonarcana.com/Jargogle?ref=',
        encodeURIComponent(window.location.href),
        '">',
        '<img src="'+image+'" width=40 height=60>'+name+', from Archon Arcana',
        '</a>',
        '</div>'
    ];
    el.innerHTML = content.join('');
    document.getElementById('archonCardWidget').append(el);
}
