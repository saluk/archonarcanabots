<?php
/**
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * @file
 */

namespace MediaWiki\Extension\AADeckView;

class BeforePageDisplay implements \MediaWiki\Hook\BeforePageDisplayHook {


	/**
	 * @see https://www.mediawiki.org/wiki/Manual:Hooks/BeforePageDisplay
	 * @param \OutputPage $out
	 * @param \Skin $skin
	 */
	public function onBeforePageDisplay( $out, $skin ) : void {
		$pageTitle = $skin->getTitle();
		$out->addModules(['ext.aaDeckView.indexQuick']);
		if ( str_contains($out->mBodytext, 'deck-results') ) {
				$out->addModules(['ext.aaDeckView.indexDeckSearch']);
		}
		if ( str_contains($out->mBodytext, 'card-gallery-images') ) {
				$out->addModules(['ext.aaDeckView.indexGallery']);
		}
		if ( substr($pageTitle, 0, strlen('Deck:')) === 'Deck:' and !($out->getContext()->getActionName()==='edit') ) {
				$out->addModules(['ext.aaDeckView.indexDeckView']);
		}
		else {
				$out->addModules(['ext.aaDeckView.indexCommon']);
		}

		$localized_title = [];
		preg_match('/<localetitle>(.*?)<\/localetitle>/', $out->getHTML(), $localized_title);
		
		if (count($localized_title) > 1) {
			$out->setPageTitle($localized_title[1]);
		}


		if ( substr($pageTitle, 0, strlen('User')) !== 'User' && substr($pageTitle, 0, strlen('Special')) !== 'Special' && substr($pageTitle, 0, strlen('Template:')) !== 'Template:') {
			$out->addInlineScript( <<<'EOT'
				// Hotjar Tracking Code for archonarcana.com
				    (function(h,o,t,j,a,r){
					h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
					h._hjSettings={hjid:2302354,hjsv:6};
					a=o.getElementsByTagName('head')[0];
					r=o.createElement('script');r.async=1;
					r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
					a.appendChild(r);
				    })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
EOT
			);
		}

		$out->addInlineScript( <<<'EOT'
(function(f,b){if(!b.__SV){var e,g,i,h;window.mixpanel=b;b._i=[];b.init=function(e,f,c){function g(a,d){var b=d.split(".");2==b.length&&(a=a[b[0]],d=b[1]);a[d]=function(){a.push([d].concat(Array.prototype.slice.call(arguments,0)))}}var a=b;"undefined"!==typeof c?a=b[c]=[]:c="mixpanel";a.people=a.people||[];a.toString=function(a){var d="mixpanel";"mixpanel"!==c&&(d+="."+c);a||(d+=" (stub)");return d};a.people.toString=function(){return a.toString(1)+".people (stub)"};i="disable time_event track track_pageview track_links track_forms track_with_groups add_group set_group remove_group register register_once alias unregister identify name_tag set_config reset opt_in_tracking opt_out_tracking has_opted_in_tracking has_opted_out_tracking clear_opt_in_out_tracking start_batch_senders people.set people.set_once people.unset people.increment people.append people.union people.track_charge people.clear_charges people.delete_user people.remove".split(" ");
for(h=0;h<i.length;h++)g(a,i[h]);var j="set set_once union unset remove delete".split(" ");a.get_group=function(){function b(c){d[c]=function(){call2_args=arguments;call2=[c].concat(Array.prototype.slice.call(call2_args,0));a.push([e,call2])}}for(var d={},e=["get_group"].concat(Array.prototype.slice.call(arguments,0)),c=0;c<j.length;c++)b(j[c]);return d};b._i.push([e,f,c])};b.__SV=1.2;e=f.createElement("script");e.type="text/javascript";e.async=!0;e.src="undefined"!==typeof MIXPANEL_CUSTOM_LIB_URL?
MIXPANEL_CUSTOM_LIB_URL:"file:"===f.location.protocol&&"//cdn.mxpnl.com/libs/mixpanel-2-latest.min.js".match(/^\/\//)?"https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js":"//cdn.mxpnl.com/libs/mixpanel-2-latest.min.js";g=f.getElementsByTagName("script")[0];g.parentNode.insertBefore(e,g)}})(document,window.mixpanel||[]);
mixpanel.init("b9705711d013fadf78347c631a82fef8", {batch_requests: true})
EOT
		);

		try {
			$match = [];
			$result = preg_match("/^(.*)\/locale\/(.*)$/", $out->getTitle(), $match);
			if ( count($match) > 2 ) {
				$title = $match[1];
				$locale = $match[2];
				$out->setPageTitle( '...' );
				$out->clearHTML();
				$out->addHTML('<div class="cardEntry" data-locale="' . $locale . '" data-name="' . $title . '"></div>');
			}
		} finally {}

	}

}
