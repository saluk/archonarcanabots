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

class ShowMissingArticle implements \MediaWiki\Page\Hook\ShowMissingArticleHook {


	// TODO - it's a little weird that the resource loader isn't working
	//      - we can't access mw.config anymore?
	//      - DeckData pages return 404 status code
	//
	/**
	 * @see https://www.mediawiki.org/wiki/Manual:Hooks/ShowMissingArticle
	 * @param \OutputPage $out
	 */
	public function onShowMissingArticle( $article ) : void {
		$out = $article->getContext()->getOutput();

		if ( $out->getTitle()->getNsText() == "Deck" ) {
			$out->setPageTitle( 'Deck:Loading' );
			$out->clearHTML();
			$out->setStatusCode(200);
			$html = <<<EOD
<html>
<style>

/* link formatting */
.mw-body a:link {
  text-decoration: none;
  color: #1c2b9c;
  border-bottom: 2px solid transparent;
}

.mw-body a:visited {
  text-decoration: none;
  border-bottom: 2px solid transparent;
  color: #1c2b9c;
}

.mw-body a:hover {
  color: #000000;
  text-decoration: underline;
  border-bottom: 2px solid transparent;
}

/* decklist preview */
.decklist-viewer {
  display: grid;
  grid-template-columns: auto 150px 150px 150px;
  grid-template-rows: auto 40px 60px auto 40px 50px;
  grid-gap: 5px;
  background-color: #f0f0f0;
  padding: 5px 5px 5px 5px;
  max-width: 850px;
  box-sizing:border-box;
}

.decklist-viewer > div {
  text-align: center;
}

.decklist-image {
  grid-row-start: 1;
  grid-row-end: 7;
  min-width: 200px;
  max-width: 400px;
  padding: 5px 8px 7px 7px;
  margin: 5px;
  border-radius: 3%;
  background-color: #c0c0c0;
  display:flex;
  align-items:center;
  justify-content:center;
}

.decklist-image img {
  max-width: 100%;
  height: auto;
  border-radius: 3%;
  filter: drop-shadow(2px 2px 0px #000000);
}

.decklist-title {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: castoro;
  font-size: 2.3em;
  line-height: 1em;
  border-bottom: 1px dashed #a0a0a0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 5px 5px 5px;
}

.set-name {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: zilla slab;
  font-size: 1.5em;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.set-houses img {
  filter: drop-shadow(3px 3px 0px #303030);
  margin-left: 3px;
  margin-right: 3px;
  height: 40px;
  width: 40px;
}

.set-houses {
  grid-column-start: 2;
  grid-column-end: 5;
  border-bottom: 1px dashed #a0a0a0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.deck-info {
  grid-column-start: 2;
  grid-column-end: 5;
  display: flex;
}

.card-types,
.card-rarities,
.card-enhancements {
  font-family: lato;
  line-height: 2em;
  padding:10px 0px 10px 0px;
  flex:1;
}

.card-types:first-line,
.card-rarities:first-line,
.card-enhancements:first-line {
  font-weight: 500;
  font-family: zilla slab;
  font-size: 1.2em;
  color: #505050;
}

.card-types img,
.card-rarities img,
.card-enhancements img {
  filter: drop-shadow(1px 1px 0px #303030);
  height: 22px;
  width: 22px;
   margin-bottom:2px;
}

.deck-aember {
  grid-column-start: 2;
  grid-column-end: 5;
  font-family: lato;
  border-bottom: 1px dashed #a0a0a0;
  padding: 5px 5px 5px 5px;
}

   .links {
     grid-column-start:2;
     grid-column-end:5;
     display:flex;
   }

.link-1,
.link-2,
.link-3 {
  font-family: lato;
  font-size: 0.9em;
  display: flex;
  flex:1;
  justify-content: center;
  align-items: center;
  padding: 5px 0px 5px 0px;
}

.decklist-image a:hover {
  border-bottom:0px !important;
}


@media screen and (min-width:901px) {
.mw-body h2 {
  font-family: castoro !important;
  border-bottom:1px solid #000000 !important;
}

.mw-body h2:after {
  border:0px solid #000000 !important;
}

}

@media screen and (max-width: 900px) {

  .mw-body h2 {
  font-family: castoro !important;
  border-bottom:1px solid #000000 !important;
  }

  .mw-body h2:after {
  border:0px solid #000000 !important;
  }


  .decklist-viewer {
    display: grid;
    grid-template-columns: calc(33% - 2px) calc(33% - 3px) calc(33% - 2px);
    grid-gap: 5px;
    background-color: #ffffff;
    padding: 5px 5px 5px 5px;
    max-width: 850px;
    border:0px;
  }

  .decklist-image {
    grid-column-start: 1;
    grid-column-end: 4;
    min-width: 250px;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
    text-align:center;
    padding: 0px;
    background-color:#ffffff;
  }

  .decklist-title {
    grid-column-start: 1;
    grid-column-end: 4;
    font-size: 1.8em;
    line-height: 1em;
    padding: 10px 5px 5px 5px;
  }

  .set-name {
    grid-column-start: 1;
    grid-column-end: 4;
    font-size: 1.3em;
  }

  .set-houses {
    grid-column-start: 1;
    grid-column-end: 4;
    border-bottom: 1px dashed #a0a0a0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 0px 0px 10px 0px;
  }
  .deck-info {
    grid-column-start: 1;
    grid-column-end: 4;
  }

   .card-types, .card-rarities, .card-enhancements {
      padding:0px 0px 10px 0px;
  }

  .card-types:first-line,
  .card-rarities:first-line,
  .card-enhancements:first-line {
    font-size: 1em;
    font-family: lato;
    font-weight:600;
  }

  .deck-aember {
    grid-column-start: 1;
    grid-column-end: 4;
    padding: 10px 5px 10px 5px;
  }


   .links {
     grid-column-start:1;
     grid-column-end:4;
   }

  .link-1,
  .link-2,
  .link-3 {
    font-size: 0.9em;
    padding: 5px 0px 5px 0px;
  }

}

/* adjustments for very small screens */
@media screen and (max-width:370px) {

  .deck-info {
     display:block;
  }

  .card-types,
  .card-rarities,
  .card-enhancements {
    grid-column-start: 1;
    grid-column-end: 4;
    border-bottom:1px dashed #a0a0a0;
  }

  .deck-aember {
    grid-column-start: 1;
    grid-column-end: 4;
    padding: 0px 0px 5px 0px;
  }


}



/*
 *
 * Formatting for the card list preview
 *
 */

  .card-preview-gallery {
    width: 100%;
    overflow: hidden;
    display: flex; /* I hate internet explorer */
    flex-wrap: wrap;
    display: grid; /* every other browser gets a pretty grid */
    grid-column-gap:10px;
    grid-row-gap:10px;
  }

.card-preview {
  position: relative;
    min-width: 150px;
    max-width: 300px;
    overflow: hidden;
    height: auto;
  transition:all .5s ease-in-out;
  }

.card-preview:hover {
   filter:brightness(.8);
   cursor:pointer;
}

  .card-preview img {
    width: 100%;
    height: auto;
  }


.enhanced-card {
  position:absolute;
  height:100%;
  width:100%;
  display:block;
  top:0px;
  left:0px;
  content:"";
  z-index:5;
  opacity:1;
  border-radius:5%;
}

.enhanced-card:before {
  position:absolute;
  top:40%;
  right:0px;
  content:"Enhanced";
  font-family:lato;
  padding:3px 5px 3px 10px;
  background-color:#353331;
  color:white;
  opacity:1;
  font-size:.9em;
}

@media screen and (max-width:600px) {
  .card-preview-gallery {
    grid-template-columns: repeat(2, 1fr);
    grid-column-gap:5px;
    grid-row-gap:5px;
  }

  .enhanced-card:before {
  font-size:.85em;
}

}

@media screen and (min-width: 601px) and (max-width: 900px) {
  .card-preview-gallery {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (min-width: 901px) and (max-width: 1200px) {
  .card-preview-gallery {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media screen and (min-width: 1201px) {
  .card-preview-gallery {
    grid-template-columns: repeat(5, 1fr);
  }

}

.loading-screen {
  height:150px;
  width:150px;
  background-color:#c0c0c0;
  position:relative;
  border-radius:50%;
  overflow:hidden;
}

.outer-circle {
  position:absolute;
  top:0px;
  left:0px;
  height:100%;
  width:100%;
    background-image:conic-gradient(
				#000000 0,
				#000000 15%,
				#c0c0c0 0,
				#c0c0c0 20%,
				#303030 0,
				#303030 35%,
				#c0c0c0 0,
				#c0c0c0 40%,
				#000000 0,
				#000000 55%,
				#c0c0c0 0,
				#c0c0c0 60%,
				#505050 0,
				#505050 75%,
				#c0c0c0 0,
				#c0c0c0 80%,
				#303030 0,
				#303030 95%,
				#c0c0c0 0,
				#c0c0c0 100%
		);
  -webkit-animation-name: spin;
  -webkit-animation-duration: 30s;
  -webkit-animation-iteration-count: infinite;
  -webkit-animation-timing-function: linear;
  border-radius:50%;
}

.inner-circle {
  position:absolute;
  top:10%;
  left:10%;
  height:80%;
  width:80%;
  background-color:#c0c0c0;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  /*font-family:verdana;*/
}

@-moz-keyframes spin {
    from { -moz-transform: rotate(0deg); }
    to { -moz-transform: rotate(360deg); }
}
@-webkit-keyframes spin {
    from { -webkit-transform: rotate(0deg); }
    to { -webkit-transform: rotate(360deg); }
}
@keyframes spin {
    from {transform:rotate(0deg);}
    to {transform:rotate(360deg);}
}


</style>

<!-- import fonts -->
  <link href='https://fonts.googleapis.com/css?family=Castoro' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Mate SC' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Lato' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css?family=Zilla Slab' rel='stylesheet'>

<!-- archon card / decklist -->
<h2>Decklist</h2>
  <div class="decklist-viewer">
    <div class="decklist-image"><div class="loading-screen">
  <div class="outer-circle"></div>
  <div class="inner-circle">Loading<br>Decklist</div>
</div>
</div>
    <div class="decklist-title">Decklist</div>
    <div class="set-name"><br></div>
    <div class="set-houses"><br>
    </div>
    <div class="deck-info">
    <div class="card-types">
      <br><br><br><br><br>
    </div>
    <div class="card-rarities">
      <br><br><br><br><br>
    </div>
    <!-- remove this entire div if the deck is pre-MM -->
    <div class="card-enhancements">
     <br><br><br><br><br>
    </div>
    </div>
    <div class="deck-aember"></div>
    <div class="links">
      <div class="link-1"></div>
      <div class="link-2"></div>
      <div class="link-3"></div>
    </div>
  </div>
</html>
EOD;
			$out->addHTML($html);

		}
	}

}
