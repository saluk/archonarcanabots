--Module:LuacardStyle
--canstage
return {
  cardstyle = [==[

/* CSSSECTION MAIN */
/* changes the display for mobile screens */

/* adds hidden element for the page previews */

.pageOverlay {
  font-size:0px;
  line-height:0px;
  height:0px;
  float:left;
}

.pageOverlay img {
  display:none;
}

.pageOverlay p {
  height:0px;
}


/* changes the display for mobile screens */

@media screen and (max-width: 780px) {

  .cardEntry {
  width: 100%;
  max-width: 500px;
  background-color: #fafafa;
  border-radius: 20px;
  /*  box-shadow: 2px 2px 0px 2px rgba(0, 0, 0, 0.05); */
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  margin-bottom: 15px;
  margin-top: 10px;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid #909090;
  }

  div.cardEntry .image {
  padding-bottom: 10px;
  padding-top: 10px;
  width: 100%;
  text-align: center;
  background-color: #d3d0c5;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  box-sizing: border-box;
  }

  div.image img {
  filter: drop-shadow(0 0 0.2rem #505050);
  border-radius:20px;
  }
  
  div.sets img {
  filter: drop-shadow(1px 1px 0px #808080);
  padding-bottom:2px;
  }


  div.topRow {
  display: flex;
  width: 100%;
  filter: drop-shadow(0px 3px 0px #909090);

  }

  .topRow a:link,
  .topRow a:visited {
  color: white;
  }



  div.topRow .type {
  flex:1;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  background-color: #434238;
  box-sizing: border-box;
  font-weight: bold;
  }
  div.topRow .house {
  flex:2;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  background-color: #434238;
  box-sizing: border-box;
  font-weight: bold;
  }
  div.topRow .rarity {
  flex:2;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  background-color: #434238;
  box-sizing: border-box;
  font-weight: bold;
  }
  
  div.house img {
  filter: drop-shadow(0 0 0.1rem #303030);
  }

  div.topRow .untamed {
  background-color: #083628;
  }

  div.topRow .saurian {
  background-color: #0C4C47;
  }

  div.topRow .logos {
  background-color: #003A45;
  }


  div.topRow .shadows {
  background-color: #14132F;
  }

  div.topRow .brobnar {
  background-color: #880514;
  }

  div.topRow .dis {
  background-color: #353833;
  }

  div.topRow .mars {
      background-color:#4c3380;
  }

  div.topRow .sanctum {
      background-color:#1E3A79;
  }

  div.topRow .starAlliance {
      background-color:#302B66;
  }
  
  div.topRow .unfathomable {
    background-color:#3d4789;
  }

  div.topRow .ekwidon {
    background-color:#801924;
  }

  .rarity img {
  padding-bottom: 3px;
  }


  .creatureRow {
  display: flex;
  width: 100%;
  flex: 1;
  box-sizing: border-box;
  }

  div.creatureRow .power,
  div.creatureRow .armor,
  div.creatureRow .aember {
  flex: 1;
  background-color: #dedcd3;
  text-align: center;
  padding-top: 12px;
  padding-bottom: 8px;
  box-sizing: border-box;
  font-weight: bold;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  border-bottom: 1px solid #c0c0c0;
  }

  div.creatureRow a:link,
  div.creatureRow a:visited {
  color: #000000;
  }

  div.traits {
  text-align: center;
  padding-top: 8px;
  padding-bottom: 8px;
  }

  div.cardText {
  width: 100%;
  background-color: #fafafa;
  text-align: left;
  padding-top: 16px;
  padding-bottom: 8px;
  padding-left: 20px;
  padding-right: 15px;
  box-sizing: border-box;
  line-height: 1.5em;
  }
  
  .cardText a:link, .cardText a:visited, .flavorText a:link, .flavorText a:visited, .traits a:link, .traits a:visited {
      color:black;
      text-decoration:none;
      border-bottom: 1px black dotted;
  }
  
  .cardText a:hover, .flavorText a:hover, .traits a:hover {
      color:black;
      text-decoration:none;
      border-bottom: 1px black solid;
  }


  div.flavorText {
  width: 100%;
  background-color: #fafafa;
  padding-top: 8px;
  padding-bottom: 25px;
  padding-left: 20px;
  padding-right: 15px;
  box-sizing: border-box;
  font-style: italic;
  font-size: 1em;
  line-height: 1.5em;
  }

  .artist {
background-color: #dedcd3;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
      border-top: 1px solid #c0c0c0;

  padding-top: 8px;
  padding-bottom: 10px;
  box-sizing: border-box;
  padding-left: 8px;
  padding-right: 8px;
  text-align: center;
  }
  
  .artist a:link, a:visited {
      color:black;
      text-decoration:none;
      border-bottom:1px dotted #000000;
  }
  
  .artist a:hover {
      color:black;
      text-decoration:none;
      border-bottom:1px solid #000000;
  }

  div.sets {
  display:flex;
  }
  
  .sets .setEntry {
  flex:1;
  background-color:#e9e8e2;
  border-top:1px solid #c0c0c0;
  border-top-left-radius:20px;
  border-top-right-radius:20px;
  padding-top:8px;
  padding-bottom:8px;
  box-sizing:border-box;
  padding-left:8px;
  padding-right:8px;
  text-align:center;
  }
  
  .sets .setMenu {
  flex:1;
  max-width:80px;
  background-color:#e9e8e2;
  border-top:1px solid #c0c0c0;
  border-top-left-radius:20px;
  border-top-right-radius:20px;
  padding-top:8px;
  padding-bottom:8px;
  box-sizing:border-box;
  padding-left:8px;
  padding-right:8px;
  text-align:center;
  }

  
  .sets a:link, .sets a:visited {
      color:black;
  }

  /* toggle display */

  .hide {
  display: none
  }

  .accordion {
  list-style: none;
  padding: 0;
  margin-left: 0px;
  }

  .accordion li,
  .accordion ul {
  margin-left: 0px;
  margin-top: 10px;
  margin-bottom: 10px;

  }

  .toggle {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  border-radius: 10px;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  transition: background .3s ease;
  border-left: 8px solid #535246;
  background-color: #f4f3f0;
  box-sizing: border-box;
  }

  .toggle:hover {
  background: #dedcd3;
  box-sizing: border-box;
  }

  .toggleWhite {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 0px;
  padding-right: 0px;
  transition: background .3s ease;
  background-color: #ffffff;
  box-sizing: border-box;
  }

  .toggleWhite:hover {
  background: #ffffff;
  box-sizing: border-box;
  }

  .toggleRed {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  border-radius: 10px;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  transition: background .3s ease;
  border-left: 8px solid #e03434;
  background-color: #f4f3f0;
  box-sizing: border-box;
  }

  .toggleRed:hover {
  background: #dedcd3;
  box-sizing: border-box;
  }

  ul.accordion .inner {
  text-align: left;
  overflow: hidden;
  padding-left: 17px;
  padding-right: 10px;
  max-height: 0;
  line-height: 1.5em;
  transition: max-height .6s ease;
  }

  .arcanaAdvises {
  display: inline;
  background-color: crimson;
  color: white;
  padding: 3px;
  border-radius: 3px;
  font-variant-caps: all-small-caps;
  font-size: 1.1em;
  }

  .arcanaAdvises2 {
  display: inline;
  color: crimson;
  font-weight: bold;
  }

  .accordion input[type="checkbox"]:checked+li>.inner {
  max-height: 1000px;
  }

  /* faq accordion that hides on desktop */

  .accordionFAQ {
  list-style: none;
  padding: 0;
  margin-left: 0px;
  }

  .accordionFAQ li,
  .accordionFAQ ul {
  margin-left: 0px;
  margin-top: 10px;
  margin-bottom: 10px;

  }

  ul.accordionFAQ .inner {
  text-align: left;
  overflow: hidden;
  padding-left: 17px;
  padding-right: 10px;
  max-height: 0;
  line-height: 1.5em;
  transition: max-height .6s ease;
  }

  .accordionFAQ input[type="checkbox"]:checked+li>.inner {
  max-height: 1000px;
  }


  .faqQuestion,
  .faqAnswer {
  display: none;
  }

  .spacer {
  height: 10px;
  width: 100%;
  display: block;
  box-sizing: border-box;
  }


}

@media screen and (max-width: 380px) {
  .topRow img {
      display:none;
  }

}

/* changes the view for desktop screens */
@media screen and (min-width: 781px) {

  .cardEntry {
  display: flex;
  border-radius: 20px;
  border: 1px solid #909090;
  background-color: #fafafa;
  width: 700px;
  box-sizing: border-box;
  margin-bottom: 15px;
  margin-top:10px;
  }

  div.cardEntry .image {
  padding-bottom: 20px;
  padding-top: 20px;
  padding-left: 10px;
  padding-right: 10px;
  text-align: center;
  background-color: #fafafa;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
  box-sizing: border-box;
  }

  div.image img {
  filter: drop-shadow(0 0 0.2rem #505050);
  border-radius:20px;
  }
  
      div.sets img {
  filter: drop-shadow(1px 1px 0px #808080);
      padding-bottom:2px;
  }

  div.rightSide {
  display: flex;
  flex-direction: column;
  flex: 1;
  box-sizing: border-box;
  }

  div.topRow {
  display: flex;
  width: 100%;
  filter: drop-shadow(0px 3px 0px #909090);

  }

  .topRow a:link,
  .topRow a:visited {
  color: white;
  }


  div.house img {
  filter: drop-shadow(0 0 0.2rem #202020);
  }

  div.topRow .type {
  flex: 1;
  background-color: #434238;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  box-sizing: border-box;
  font-weight: bold;
  }

  div.topRow .house {
  flex: 2;
  background-color: #434238;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  padding-left: 8px;
  box-sizing: border-box;
  font-weight: bold;
  border-bottom-left-radius: 20px;

  }

  div.topRow .rarity {
  flex: 2;
  background-color: #434238;
  color: white;
  text-align: center;
  padding-top: 15px;
  padding-bottom: 15px;
  box-sizing: border-box;
  font-weight: bold;
  border-top-right-radius: 20px;
  }

  div.topRow .untamed {
  background-color: #083628;
  }

  div.topRow .saurian {
  background-color: #0C4C47;
  }

  div.topRow .logos {
  background-color: #003A45;
  }


  div.topRow .shadows {
  background-color: #14132F;
  }

  div.topRow .brobnar {
  background-color: #880514;
  }

  div.topRow .dis {
  background-color: #353833;
  }

  div.topRow .mars {
          background-color:#4c3380;
  }

  div.topRow .sanctum {
      background-color:#1E3A79;
  }

  div.topRow .starAlliance {
          background-color:#302B66;
  }

  div.topRow .unfathomable {
    background-color:#3d4789;
  }

  div.topRow .ekwidon {
    background-color:#801924;
  }

  .rarity img {
  padding-bottom: 3px;
  }


  .creatureRow {
  display: flex;
  box-sizing: border-box;
  margin-left: 15px;
  }

  div.creatureRow a:link,
  div.creatureRow a:visited {
  color: #000000;
  }


  div.creatureRow .power,
  div.creatureRow .armor,
  div.creatureRow .aember {
  flex: 1;
  background-color: #dedcd3;
  text-align: center;
  padding-top: 12px;
  padding-bottom: 8px;
  box-sizing: border-box;
  font-weight: bold;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  border-bottom: 1px solid #c0c0c0;
  }

  div.traits {
  text-align: center;
  padding-top: 15px;
  padding-bottom: 8px;
  padding-left: 15px;
  }

  div.cardText {
  width: 100%;
  flex: 1;
  background-color: #fafafa;
  text-align: left;
  padding-top: 16px;
  padding-bottom: 8px;
  padding-left: 20px;
  padding-right: 8px;
  box-sizing: border-box;
  line-height: 1.5em;
  height: 100%;
  }
  
  .cardText a:link, .cardText a:visited, .flavorText a:link, .flavorText a:visited, .traits a:link, .traits a:visited {
      color:black;
      text-decoration:none;
      border-bottom: 1px black dotted;
  }
  
  .cardText a:hover, .flavorText a:hover, .traits a:hover {
      color:black;
      text-decoration:none;
      border-bottom: 1px black solid;
  }

  div.flavorText {
  width: 100%;
  background-color: #fafafa;
  padding-top: 8px;
  padding-bottom: 25px;
  padding-left: 20px;
  padding-right: 8px;
  box-sizing: border-box;
  font-style: italic;
  font-size: 1em;
  line-height: 1.5em;
  }

  .artist {
  background-color: #dedcd3;
  border-bottom-right-radius: 20px;
  padding-top: 8px;
      border-top: 1px solid #c0c0c0;
  border-top-left-radius:20px;
  padding-bottom: 10px;
  box-sizing: border-box;
  padding-left: 8px;
  padding-right: 8px;
  text-align: center;  
  }

  .artist a:link, a:visited {
      color:black;
      text-decoration:none;
      border-bottom:1px dotted #000000;
  }
  
  .artist a:hover {
      color:black;
      text-decoration:none;
      border-bottom:1px solid #000000;
  }

  div.sets {
  display:flex;
  margin-left:20px;
  }
  
  .sets .setEntry {
  flex:1;
  background-color:#e9e8e2;
  border-top:1px solid #c0c0c0;
  border-top-right-radius:20px;
  border-top-left-radius:20px;
  padding-top:8px;
  padding-bottom:8px;
  box-sizing:border-box;
  padding-left:8px;
  padding-right:8px;
  text-align:center;
  }
  
  .sets .setMenu {
  flex:1;
  max-width:80px;
  background-color:#e9e8e2;
  border-top:1px solid #c0c0c0;
  border-top-left-radius:20px;
  border-top-right-radius:20px;
  padding-top:8px;
  padding-bottom:8px;
  box-sizing:border-box;
  padding-left:8px;
  padding-right:8px;
  text-align:center;
  }

  .sets a:link, .sets a:visited {
      color:black;
  }


  /* for desktop devices */

  div.faqQuestion {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  border-radius: 10px;
  color: black;
  text-align: left;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  margin-top: 10px;
  border-left: 8px solid #535246;
  background-color: #f4f3f0;
  box-sizing: border-box;
  }

  div.faqAnswer {
  text-align: left;
  padding-left: 17px;
  display: block;
  padding-right: 10px;
  margin-top: 5px;
  margin-bottom: 15px;
  line-height: 1.5em;
  }

  .accordionFAQ {
  display: none;
  }

  /* toggle display */

  .hide {
  display: none
  }

  .accordion {
  list-style: none;
  padding: 0;
  margin-left: 0px;
  }

  .accordion li,
  .accordion ul {
  margin-left: 0px;
  margin-top: 8px;
  margin-bottom: 8px;
  }

  .toggle {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  border-radius: 10px;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  transition: background .3s ease;
  border-left: 8px solid #535246;
  background-color: #f4f3f0;
  box-sizing: border-box;
  }

  .toggle:hover {
  background: #dedcd3;
  box-sizing: border-box;
  }

  .toggleWhite {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 0px;
  padding-right: 0px;
  transition: background .3s ease;
  background-color: #ffffff;
  box-sizing: border-box;
  }

  .toggleWhite:hover {
  background: #ffffff;
  box-sizing: border-box;
  }

  .toggleRed {
  width: 100%;
  display: block;
  height: auto;
  line-height: 1.5em;
  border-radius: 10px;
  color: black;
  cursor: pointer;
  text-align: left;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
  transition: background .3s ease;
  border-left: 8px solid #e03434;
  background-color: #f4f3f0;
  box-sizing: border-box;
  }

  .toggleRed:hover {
  background: #dedcd3;
  box-sizing: border-box;
  }

  ul.accordion .inner {
  text-align: left;
  overflow: hidden;
  padding-left: 17px;
  padding-right: 10px;
  margin-top: 5px;
  margin-bottom: 0px;
  max-height: 0;
  line-height: 1.5em;
  transition: max-height .6s ease;
  }

  .arcanaAdvises {
  display: inline;
  background-color: crimson;
  color: white;
  padding: 3px;
  border-radius: 3px;
  font-variant-caps: all-small-caps;
  font-size: 1.1em;
  }

  .arcanaAdvises2 {
  display: inline;
  color: crimson;
  font-weight: bold;
  }

  .accordion input[type="checkbox"]:checked+li>.inner {
  max-height: 1000px;
  }

  .spacer {
  height: 5px;
  width: 100%;
  display: block;
  box-sizing: border-box;
  }
  

}

  /* CSSSECTION AEMBER STYLE */
  .aemberImg {
  margin-left:2px;
  }

  /* CSSSECTION ALT ART */
  @media screen and (max-width: 780px) {
  .largeBackground {
              background-color: #d3d0c5;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      width:100%;
  
  }
  
      #wrap {
      width: 100%;
      max-width: 320px;
      overflow: hidden;
      margin-right: auto;
      margin-left: auto;
      box-sizing: border-box;
      }
      
      .gallery-label1 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #dedcd3;
      color: black;
      left: 10px;
      text-align:center;
      width:140px;
      padding: 5px 0px 5px 0px;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      border-top: 1px solid #808080;
      transition: background .2s ease-in-out;
  }
  
  .gallery-label2 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #dedcd3;
      color: black;
      left:160px;
      text-align:center;
      width:140px;
      padding: 5px 0px 5px 0px;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      border-top: 1px solid #808080;
      transition: background .2s ease-in-out;
  }
  
  .gallery-label3 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #c0c0c0;
      color: white;
      left: 250px;
      padding: 12px 25px 12px 25px;
      border-radius: 10px;
  }
  
  }
  
  @media screen and (min-width: 781px) {
  
  .largeBackground {
      width:100%;
      max-width:325px;
      margin-right:10px;
  }
  
      #wrap {
      width: 100%;
      max-width: 325px;
      overflow: hidden;
      margin-right: 10px;
      }
      
      .gallery-label1 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #dedcd3;
      color: black;
      left: 20px;
      text-align:center;
      width:90px;
      padding: 5px 0px 5px 0px;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      border-top: 1px solid #c0c0c0;
      transition: background .2s ease-in-out;
  }
  
  .gallery-label2 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #dedcd3;
      color: black;
      left:115px;
      text-align:center;
      width:90px;
      padding: 5px 0px 5px 0px;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      border-top: 1px solid #c0c0c0;
      transition: background .2s ease-in-out;
  }
  
  .gallery-label3 {
      position: absolute;
      bottom: 0px;
      font-weight: 600;
      background-color: #c0c0c0;
      color: white;
      left: 250px;
      padding: 12px 25px 12px 25px;
      border-radius: 10px;
  }
  
  }
  
  ul#gallery-container {
      position: relative;
      width: 100%;
      max-width: 800px;
      min-width: 310px;
      height: 475px;
      margin: 0;
      text-align: center;
      display: block;
  }
  
  li.gallery-item {
      display: inline-block;
      appearance: none;
  }
  
  div.gallery-fullsize {
      position: absolute;
      top: 10px;
      left: 5px;
      display: block;
      z-index: -1;
      opacity: 0;
  }
  
  .gallery-fullsize img {
      border-radius: 20px;
      filter: drop-shadow(0 0 0.2rem #505050);
      max-height: 425px;
      width: auto;
  }
  
  .gallery-label1:hover,
  .gallery-label2:hover,
  .gallery-label3:hover,
  input.gallery-selector:checked~.gallery-label1,
  input.gallery-selector:checked~.gallery-label2 {
      background-color: #c0c0c0;
      cursor: pointer;
  }
  
  
  
  input.gallery-selector:checked~div.gallery-fullsize {
      display: block;
      opacity: 1;
      z-index: 10;
      animation-name: fade;
      animation-duration: .8s;
      animation-timing-function: ease-in-out;
  }
  
  
  @keyframes fade {
      from {
      opacity: .4
      }
  
      to {
      opacity: 1
      }
  }
  
  input.gallery-selector {
      display: none;
  }
  
  label.gallery-label {
      cursor: pointer;
  }

  /* CSSSECTION errata */
    @media screen and (max-width:780px) {

      .cardText {
        box-sizing:border-box;
      }
     
        .cardText .horizontalLine {
       position:absolute;
       top:32px;
       left:0px;
       height:0px;
       width:100%;
       border-bottom:1px solid #c0c0c0;
       z-index:20;
       }
        
        ul#gallery-containerErrata {
       position: relative;
       width: 100%;
       height: 200px;
       margin: 0;
       text-align: left;
       display: block;
       background-color:#fafafa;
       box-sizing:border-box;
     }
     
     li.gallery-itemErrata {
       display: inline-block;
       appearance: none;
       margin-left:0px;
         box-sizing:border-box;
     }
     
     .gallery-label1Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       margin-left:0px;
         left: 0px;
       padding: 5px 20px 5px 20px;
         border-top-left-radius:20px;
       border-top-right-radius:20px;
     }
     
     .gallery-label2Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       left: 55%;
       padding: 5px 20px 5px 20px;
       border-top-left-radius:20px;
       border-top-right-radius:20px;
     }
     
     .gallery-label3Errata {
       position: absolute;
       bottom: 0px;
       font-weight: 600;
       background-color: #fafafa;
       color: white;
       left: 250px;
       padding: 12px 25px 12px 25px;
       border-radius: 10px;
     }
     
     .gallery-label1Errata:hover,
     .gallery-label2Errata:hover,
     .gallery-label3Errata:hover, input.gallery-selectorErrata:checked~.gallery-label1Errata, input.gallery-selectorErrata:checked~.gallery-label2Errata {
       background-color: #dedede;
       background-image:linear-gradient(#dedede 75%,#fafafa);
       cursor: pointer;
     }
     
     input.gallery-selectorErrata:checked~div.gallery-fullsizeErrata {
       display: block;
       opacity: 1;
       z-index: 10;
       animation-name: fadeText;
       animation-duration: .8s;
       animation-timing-function: ease-in-out;
           box-sizing:border-box;
     }
     
     }
     
     /* phone screens to accommodate magda the rat */
     
     @media screen and (max-width: 500px) {
     
        ul#gallery-containerErrata {
       position: relative;
       width: 100%;
       height: 250px;
       margin: 0;
       text-align: left;
       display: block;
       box-sizing:border-box;
     }
     
     }
     
     /* makes the buttons smaller */
     
     @media screen and (max-width: 380px) {
     
     
     .gallery-label1Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       margin-left:0px;
         left: 0px;
       padding: 5px 10px 5px 10px;
         border-top-left-radius:20px;
       border-top-right-radius:20px;
     }
     
     .gallery-label2Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       left: 55%;
       padding: 5px 10px 5px 10px;
       border-top-left-radius:20px;
       border-top-right-radius:20px;
     }
     
     .gallery-label3Errata {
       position: absolute;
       bottom: 0px;
       font-weight: 600;
       background-color: #fafafa;
       color: white;
       left: 250px;
       padding: 12px 25px 12px 25px;
       border-radius: 10px;
     }
     
     }
     
     
     /* desktop screens */
     @media screen and (min-width: 781px) {
     
      
        .cardText .horizontalLine {
       position:absolute;
       top:32px;
       height:1px;
       width:100%;
       background-color:#c0c0c0;
       z-index:20;
       }
       
       ul#gallery-containerErrata {
       position: relative;
       width: 100%;
       height: 180px;
       max-width:400px;
       margin: 0;
       text-align: left;
       display: block;
       background-color:#fafafa;
       box-sizing:border-box;
     }
     
     li.gallery-itemErrata {
       display: inline-block;
       appearance: none;
       margin-left:0px;
         box-sizing:border-box;
     }
     
     
     .gallery-label1Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       left: 0px;
       margin-left:0px;
       padding: 5px 20px 5px 20px;
         border-top-left-radius:20px;
       border-top-right-radius:20px;
       transition: background .2s ease-in-out;
     }
     
     .gallery-label2Errata {
       position: absolute;
       top: 1px;
       font-weight: 600;
       background-color: #fafafa;
       color: black;
       left: 55%;
       padding: 5px 20px 5px 20px;
       border-top-left-radius:20px;
       border-top-right-radius:20px;
       transition: background .2s ease-in-out;
     }
     
     .gallery-label3Errata {
       position: absolute;
       bottom: 0px;
       font-weight: 600;
       background-color: #fafafa;
       color: white;
       left: 250px;
       padding: 12px 25px 12px 25px;
       border-radius: 10px;
     }
     
     .gallery-label1Errata:hover,
     .gallery-label2Errata:hover,
     .gallery-label3Errata:hover, input.gallery-selectorErrata:checked~.gallery-label1Errata, input.gallery-selectorErrata:checked~.gallery-label2Errata {
       background-color: #dedede;
       cursor: pointer;
     }
     
     input.gallery-selectorErrata:checked~div.gallery-fullsizeErrata {
       display: block;
       opacity: 1;
       z-index: 10;
       animation-name: fadeText;
       animation-duration: .8s;
       animation-timing-function: ease-in-out;
           box-sizing:border-box;
     }
     
     }
     /* end media */
     
     
     
     
     div.gallery-fullsizeErrata {
       position: absolute;
       top: 32px;
       left: 0px;
       display: block;
       z-index: -1;
       opacity: 0;
           padding-top: 16px;
         padding-bottom: 8px;
         box-sizing: border-box;
         line-height: 1.5em;
         clear:both;
     }
     
     
     
     
     @keyframes fadeText {
       from {
         opacity: .4
       }
     
       to {
         opacity: 1
       }
     }
     
     input.gallery-selectorErrata {
       display: none;
     }
     
     ul#gallery-containerErrata, li.gallery-itemErrata {
       margin-left:0px;
     }       
  ]==],
  multihouse_style = [==[
      /* CSSSECTION MULTI HOUSE */
  @media screen and (max-width: 780px) {
      .largeBackground {
        background-color: #d3d0c5;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        width: 100%;
      }
    
      #wrap {
        width: 100%;
        max-width: 320px;
        overflow: hidden;
        margin-right: auto;
        margin-left: auto;
        box-sizing: border-box;
      }
      
          .gallery-label1, .gallery-label2, .gallery-label3, .gallery-label4, .gallery-label5, .gallery-label6, .gallery-label7 {
        position: absolute;
        bottom: 0px;
        font-weight: 600;
        background-color: #e9e8e2;
        color: black;
        text-align: center;
        width: 35px;
        padding: 5px 0px 5px 0px;
        box-sizing:border-box;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        border-top: 1px solid #808080;
        transition: all 0.5s ease-in-out;
      }
    
    
    
      .gallery-label1 {
        left: 0px;
        left: calc(41% - 120px);
      }
    
      .gallery-label2 {
        left: 35px;
        left: calc(41% - 80px);
      }
    
      .gallery-label3 {
        left: 70px;
        left: calc(41% - 40px);
      }
      
        .gallery-label4 {
        left: 105px;
        left:41%;
      }
      
      .gallery-label5 {
        left: 140px;
        left:calc(41% + 40px);
      }
      
      .gallery-label6 {
        left: 175px;
        left:calc(41% + 80px);
      }
      
      .gallery-label7 {
        left:210px;
        left:calc(41% + 120px);
      }
      
      .house-logo {
        filter:drop-shadow(2px 2px 0px #303030);
      }
      
    }
    
    @media screen and (max-width:360px) {
    
      .gallery-label1 {
        left: 0px;
        left: calc(38% - 105px);
      }
    
      .gallery-label2 {
        left: 35px;
        left: calc(38% - 70px);
      }
    
      .gallery-label3 {
        left: 70px;
        left: calc(38% - 35px);
      }
      
        .gallery-label4 {
        left: 105px;
        left:38%;
      }
      
      .gallery-label5 {
        left: 140px;
        left:calc(38% + 35px);
      }
      
      .gallery-label6 {
        left: 175px;
        left:calc(38% + 70px);
      }
      
      .gallery-label7 {
        left:210px;
        left:calc(38% + 105px);
      }
    }
    
    @media screen and (min-width: 781px) {
      .largeBackground {
        width: 100%;
        max-width: 325px;
        margin-right: 10px;
      }
    
      #wrap {
        width: 100%;
        max-width: 325px;
        overflow: hidden;
        margin-right: 10px;
      }
      
      #wrap .house-logo {
        filter:drop-shadow(2px 2px 0px #303030);
      }
      
      .gallery-label1, .gallery-label2, .gallery-label3, .gallery-label4, .gallery-label5, .gallery-label6, .gallery-label7 {
            position: absolute;
        bottom: 0px;
        font-weight: 600;
        background-color: #dedcd3;
        color: black;
        text-align: center;
        width: 35px;
        padding: 5px 1px 5px 0px;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        border-top: 1px solid #c0c0c0;
        transition: background 0.5s ease-in-out;
        box-sizing:border-box;
      }
    
      .gallery-label1 {
        left: 25px;
      }
    
      .gallery-label2 {
        left: 65px;
      }
    
      .gallery-label3 {
        left: 105px;
      }
      
      .gallery-label4 {
        left:145px;
      }
      
      .gallery-label5 {
        left:185px;
      }
      
      .gallery-label6 {
        left:225px;
      }
      
      .gallery-label7 {
        left:265px;
      }
    }
    
    ul#gallery-container {
      position: relative;
      width: 100%;
      max-width: 800px;
      min-width: 310px;
      height: 475px;
      margin: 0;
      text-align: center;
      display: block;
    }
    
    li.gallery-item {
      display: inline-block;
      appearance: none;
    }
    
    div.gallery-fullsize {
      position: absolute;
      top: 10px;
      left: 5px;
      display: block;
      z-index: -1;
      opacity: 0;
    }
    
    .gallery-fullsize img {
      border-radius: 20px;
      filter: drop-shadow(0 0 0.2rem #505050);
      max-height: 425px;
      width: auto;
    }
    
    .gallery-label1:hover,
    .gallery-label2:hover,
    .gallery-label3:hover,
    .gallery-label4:hover,
    .gallery-label5:hover,
    .gallery-label6:hover,
    .gallery-label7:hover,
    input.gallery-selector:checked ~ .gallery-label1,
    input.gallery-selector:checked ~ .gallery-label2,
    input.gallery-selector:checked ~ .gallery-label3,
    input.gallery-selector:checked ~ .gallery-label4,
    input.gallery-selector:checked ~ .gallery-label5,
    input.gallery-selector:checked ~ .gallery-label6,
    input.gallery-selector:checked ~ .gallery-label7 {
      background-color: #a0a0a0;
      cursor: pointer;
    }
    
    label .house-logo {
      width: 25px;
      height: auto;
    }
    
    input.gallery-selector:checked ~ div.gallery-fullsize {
      display: block;
      opacity: 1;
      z-index: 10;
      animation-name: fade;
      animation-duration: 0.8s;
      animation-timing-function: ease-in-out;
    }
    
    @keyframes fade {
      from {
        opacity: 0.4;
      }
    
      to {
        opacity: 1;
      }
    }
    
    input.gallery-selector {
      display: none;
    }
    
    label.gallery-label {
      cursor: pointer;
    }
  ]==]
}