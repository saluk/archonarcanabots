/* share42.com | 22.08.2016 | (c) Dimox */
import * as $ from 'jquery';

function embedCode() {
    var title = $('#firstHeading')[0].textContent;
    var image = '';
    var imageel = $('.cardEntry .image img');
    if(imageel.length>0){
        var image = imageel[0].getAttribute('src');
    }
    var s = '\
    <div>\
    Using the widget<br>\
<br>\
    Put this script somewhere on yourpage:<br><br><br>\
    &amp;lt;div id=&quot;renderCardWidget_'+title+'&quot;&amp;gt;\
        &amp;lt;script type=&quot;text/javascript&quot; \
        src=&quot;https://archonarcana.com/MediaWiki:cardwidget.js?action=raw&ctype=text/javascript&quot;&amp;gt;\
        &amp;lt;/script&amp;gt;\
        &amp;lt;script type=&quot;text/javascript&quot;&amp;gt;\
            renderCardLink(&quot;https://archonarcana.com'+image+'&quot;, &quot;'+title+'&quot;);\
        &amp;lt;/script&amp;gt;\
    &amp;lt;/div&amp;gt;\
    </div>\
';
    return s;
}

var embedimg = ''
var imageel = $('.cardEntry .image img')
if(imageel.length>0){
    embedimg = '\
<a rel="nofollow" \
href="#"\
onclick="window.open(\'\',\
 \'_blank\', \
 \'scrollbars=0, resizable=1, menubar=0, left=100, top=100, width=550, height=440, toolbar=0, status=0\'\
 ).document.write(\
\''+embedCode()+'\');\
 return false" title="Embed" target="_blank">\
 <img id="embedme" class="share42-item" src="/images/8/85/EmbedIcon.png"/>\
 </a>';
}

(function($){$(function(){$('div.share42init').each(function(idx){var el=$(this),u=el.attr('data-url'),t=el.attr('data-title'),i=el.attr('data-image'),d=el.attr('data-description'),f=el.attr('data-path'),fn=el.attr('data-icons-file'),z=el.attr("data-zero-counter");if(!u)u=location.href;if(!fn)fn='icons.png';if(!z)z=0;function fb_count(url){var shares;$.getJSON('//graph.facebook.com/?fields=share&id='+url,function(data){shares=data.share.share_count||0;if(shares>0||z==1)el.find('a[data-count="fb"]').after('<span class="share42-counter">'+shares+'</span>')})}fb_count(u);function pin_count(url){var shares;$.getJSON('//api.pinterest.com/v1/urls/count.json?callback=?&url='+url,function(data){shares=data.count;if(shares>0||z==1)el.find('a[data-count="pin"]').after('<span class="share42-counter">'+shares+'</span>')})}pin_count(u);if(!f){function path(name){var sc=document.getElementsByTagName('script'),sr=new RegExp('^(.*/|)('+name+')([#?]|$)');for(var p=0,scL=sc.length;p<scL;p++){var m=String(sc[p].src).match(sr);if(m){if(m[1].match(/^((https?|file)\:\/{2,}|\w:[\/\\])/))return m[1];if(m[1].indexOf("/")==0)return m[1];b=document.getElementsByTagName('base');if(b[0]&&b[0].href)return b[0].href+m[1];else return document.location.pathname.match(/(.*[\/\\])/)[0]+m[1];}}return null;}f=path('share42.js');}if(!t)t=document.title;if(!d){var meta=$('meta[name="description"]').attr('content');if(meta!==undefined)d=meta;else d='';}u=encodeURIComponent(u);t=encodeURIComponent(t);t=t.replace(/\'/g,'%27');i=encodeURIComponent(i);d=encodeURIComponent(d);d=d.replace(/\'/g,'%27');var s=new Array('"#" data-count="fb" onclick="window.open(\'//www.facebook.com/sharer/sharer.php?u='+u+'\', \'_blank\', \'scrollbars=0, resizable=1, menubar=0, left=100, top=100, width=550, height=440, toolbar=0, status=0\');return false" title="Share on Facebook"','"#" data-count="pin" onclick="window.open(\'//pinterest.com/pin/create/button/?url='+u+'&media='+i+'&description='+t+'\', \'_blank\', \'scrollbars=0, resizable=1, menubar=0, left=100, top=100, width=600, height=300, toolbar=0, status=0\');return false" title="Pin It"','"//reddit.com/submit?url='+u+'&title='+t+'" title="Share on Reddit"','"#" onclick="window.open(\'//www.tumblr.com/share?v=3&u='+u+'&t='+t+'&s='+d+'\', \'_blank\', \'scrollbars=0, resizable=1, menubar=0, left=100, top=100, width=450, height=440, toolbar=0, status=0\');return false" title="Share on Tumblr"','"#" data-count="twi" onclick="window.open(\'//twitter.com/intent/tweet?text='+t+'&url='+u+'\', \'_blank\', \'scrollbars=0, resizable=1, menubar=0, left=100, top=100, width=550, height=440, toolbar=0, status=0\');return false" title="Share on Twitter"','"#" onclick="print();return false" title="Print"');var l=embedimg;for(var j=0;j<s.length;j++)l+='<span class="share42-item" style="display:inline-block;margin:0 6px 6px 0;height:24px;"><a rel="nofollow" style="display:inline-block;width:24px;height:24px;margin:0;padding:0;outline:none;background:url('+f+fn+') -'+24*j+'px 0 no-repeat" href='+s[j]+' target="_blank"></a></span>';el.html('<span id="share42">'+l+'</span>'+'<style>.share42-counter{display:inline-block;vertical-align:top;margin-left:9px;position:relative;background:#FFF;color:#666;} .share42-counter:before{content:"";position:absolute;top:0;left:-8px;width:8px;height:100%;} .share42-counter{height:24px;padding:0 7px 0 3px;font:12px/25px Arial,sans-serif;background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAYCAYAAAAMAljuAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAIxJREFUeNrs2rENgCAQQNHDyBBWDMFULmFjnMGlYAgKoy01BR5xB6H4P7mE+l7JmRBCFerdrXN673dTNfbRt1KKpJQk57xNrKN/1lpxzrXnCshAKNoCyGABAggBAggBAggBAggBAggBQoAAQoAAQoAAQr/U/tW1B5BBMNqRg3bOMUY20r9LvjOg4xVgABtzIxFP3JZkAAAAAElFTkSuQmCC) 100% 0;} .share42-counter:before{background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAYCAYAAADH2bwQAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAJlJREFUeNrEks0NwyAMhU0kdmi4MARTZYh0jS4FE3DiAjvA4dVUjZQ/p+qlfZKFrPcJPYMVANorhDDzMXGN1IF1ee/nGCNqrega6KjJWkta61dzBoyLKQEb/Rrg+WGM2RKr+ZFzxl6XJj6Z0kseQiq+gUop8hScXIQG5xx1U4ROvvv7kH8ASmvtEniklGiBlLD29/fa354CDAC6sL9OAqehCgAAAABJRU5ErkJggg==);}</style>');})})})($);
