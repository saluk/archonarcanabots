import json

from util import cargo_query
from models import wiki_model

COMMENTARY = """
<templatestyles src="Template:Card/styles.css" /><templatestyles src="Template:FAQ_Entry/styles.css" />
{{#ifeq: %(RulesType)s|Commentary|
{{#vardefine: Q | {{#explode:%(RulesText)s|//|0}} }} 
{{#vardefine: Q | {{#replace:{{#var: Q}}|Commentary|X}} }}
{{#vardefine: A | {{#explode:%(RulesText)s|//|1}} }} 
{{#vardefine: Q1 | {{#replace:{{#var:Q}}|[|<nowiki> </nowiki>}}}} 
{{#vardefine: Q1 | {{#replace:{{#var:Q1}}|]|<nowiki> </nowiki>}}}} 
<div class="commentaryQ">{{#var: Q}}</p>{{#if: %(RulesSource)s}
|{{#ifexpr: {{#expr:{{#rpos:%(RulesSource)s}|.png}}+{{#rpos:%(RulesSource)s}|.jpg}}}}<0
      |<p><div class="source-header"><span class="source-text">Source:</span> %(RulesSource)s/div>
      |{{#vardefine: img1 | {{#explode:%(RulesSource)s|•|0}} }} 
{{#ifexpr: {{#expr:{{#rpos:{{#var: img1}}|.png}}+{{#rpos:{{#var: img1}}|.jpg}}}} = -2
|<p><div class="source-header"><span class="source-text">Source:</span> {{#var: img1}}</div>
          <div class="rule-source">{{#vardefine: i | 1 }}{{#while:
   | {{#ifexpr: {{#var: i }} < 10 | true }}
   | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
|<p><div class="source-header"><span class="source-text">Source</span></div>
          <div class="rule-source">{{#vardefine: i | 0 }}{{#while:
 | {{#ifexpr: {{#var: i }} < 10 | true }}
 | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
}}
}}
|}}</div><nowiki>
</nowiki>|
{{#vardefine: Q | {{#explode:%(RulesText)s|//|0}} }} 
{{#vardefine: A | {{#explode:%(RulesText)s|//|1}} }} 
{{#vardefine: Q1 | {{#replace:{{#var:Q}}|[|<nowiki> </nowiki>}}}} 
{{#vardefine: Q1 | {{#replace:{{#var:Q1}}|]|<nowiki> </nowiki>}}}} 
{{#vardefine: Q1 | {{#replace:{{#var:Q1}}|"|<nowiki> </nowiki>}}}}
<ul class="accordion">
  <html><input id="</html>{{#var: Q1}}<html>" type="checkbox" class="hide">
  <li>
    <label for="</html>{{#var: Q1}}<html>" class="toggleRed"></html>{{#var:Q}}
<html></label></html>
    <div class="inner"><p><span class="arcanaAdvises">Arcana Advises</span>: {{#var:A}}</p>
<p><div class="arcanaAdvises2">For more information about Arcana Advises and Outstanding Issues, [[Outstanding Issues|click here]].</div></p>
    <div class="spacer"></div>
    </div>
  </li>
</ul>
}}
"""

FAQ = """
<templatestyles src="Template:Card/styles.css" /><templatestyles src="Template:FAQ_Entry/styles.css" />
{{#vardefine: Q | {{#explode:%(RulesText)s|//|0}} }} {{#vardefine: A | {{#explode:%(RulesText)s|//|1}} }} {{#vardefine: Q | {{#replace:{{#var: Q}}|FFGRuling|X}} }} {{#vardefine: Q1 | {{#replace:{{#var:Q}}|[|<nowiki> </nowiki>}}}} {{#vardefine: Q1 | {{#replace:{{#var:Q1}}|]|<nowiki> </nowiki>}}}} {{#vardefine: Q1 | {{#replace:{{#var:Q1}}|"|<nowiki> </nowiki>}}}}
<ul class="accordionFAQ"><html><input id="</html>{{#var: Q1}}<html>" type="checkbox" class="hide">
  <li>
    <label for="</html>{{#var: Q1}}<html>" class="toggle"></html>{{#var: Q}}<html></p></label></html>
    <div class="inner"><div class="spacer"></div>{{#var: A}}{{#if: %(RulesSource)s
|{{#ifexpr: {{#expr:{{#rpos:%(RulesSource)s|.png}}+{{#rpos:%(RulesSource)s|.jpg}}}}<0
      |<p><div class="source-header"><span class="source-text">Source:</span> %(RulesSource)s</div>
      |{{#vardefine: img1 | {{#explode:%(RulesSource)s|•|0}} }} 
{{#ifexpr: {{#expr:{{#rpos:{{#var: img1}}|.png}}+{{#rpos:{{#var: img1}}|.jpg}}}} = -2
|<p><div class="source-header"><span class="source-text">Source:</span> {{#var: img1}}</div>
          <div class="rule-source">{{#vardefine: i | 1 }}{{#while:
   | {{#ifexpr: {{#var: i }} < 10 | true }}
   | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
|<p><div class="source-header"><span class="source-text">Source</span></div>
          <div class="rule-source">{{#vardefine: i | 0 }}{{#while:
 | {{#ifexpr: {{#var: i }} < 10 | true }}
 | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
}}
}}
|}}<div class="spacer"></div></div>
  </li>
</ul>
<div class="faqQuestion">{{#var: Q}}</div>
<div class="faqAnswer">{{#var: A}}
{{#if: %(RulesSource)s
|{{#ifexpr: {{#expr:{{#rpos:%(RulesSource)s|.png}}+{{#rpos:%(RulesSource)s|.jpg}}}}<0
      |<p><div class="source-header"><span class="source-text">Source:</span> %(RulesSource)s</div>
      |{{#vardefine: img1 | {{#explode:%(RulesSource)s|•|0}} }} 
{{#ifexpr: {{#expr:{{#rpos:{{#var: img1}}|.png}}+{{#rpos:{{#var: img1}}|.jpg}}}} = -2
|<p><div class="source-header"><span class="source-text">Source:</span> {{#var: img1}}</div>
          <div class="rule-source">{{#vardefine: i | 1 }}{{#while:
   | {{#ifexpr: {{#var: i }} < 10 | true }}
   | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
|<p><div class="source-header"><span class="source-text">Source</span></div>
          <div class="rule-source">{{#vardefine: i | 0 }}{{#while:
 | {{#ifexpr: {{#var: i }} < 10 | true }}
 | <nowiki />
{{#vardefine: img1 | {{#explode:%(RulesSource)s|•| {{#var:i}} }} }}
{{#if: {{#var: img1}} |<div class="rule-source-image">[[File:{{#var: img1}}|frameless|class=rule-source-img]]</div>|}}
{{#vardefine: i | {{#expr: {{#var: i }} + 1 }} }}
}}
          </div>
}}
}}
|}}</div>
"""


def thumb(filename, size):
    return 'https://archonarcana.com/thumb.php?width={}&f={}'.format(size, filename)


class DeckWriter:

    def __init__(self, deck, locale, session):
        self.deck = deck
        self.locale = locale
        self.session = session

    def deck_json(self):
        def cd(card):
            d = wiki_model.card_data(card.data) if self.locale=='en' else wiki_model.card_data(card.data, self.locale)
            d.update({
                "house": card.data["house"],
                "card_type": card.data["card_type"],
                "front_image": card.data["front_image"]
            })
            if self.locale != 'en':
                d['image_number'] = self.locale.capitalize()+'-'+d['image_number']
            return d
        cards = self.deck.get_cards() if self.locale=='en' else self.deck.get_locale_cards(self.session, self.locale)
        d = {
            'name': self.deck.name,
            'key': self.deck.key,
            'expansion': self.deck.expansion,
            'cards': [cd(card) for card in cards]
        }
        return d

    def decklist(self):
        return """
<div><img src="https://images.skyjedi.com/custom/{}/en/deck_list.png" width="300" height="380"></div>
""".format(self.deck.key)

    def name(self):
        return """
{{DISPLAYTITLE:<span style="position: absolute; clip: rect(1px 1px 1px 1px); 
clip: rect(1px, 1px, 1px, 1px);">{{FULLPAGENAME}}</span>}}
= %s =
    """ % self.deck.name

    def card_browser(self):
        mav = "Maverick:%s"
        anomaly = "Anomaly:%s"
        enhanced = "enhanced"

        def wc(c, co):
            return (
                """
<a href="/%(card_name)s">
    %(is_maverick)s
    %(is_anomaly)s
    %(is_enhanced)s
    <img id="img_%(card_name)s"
        src="%(img_src)s" width="140" height="200"
    >
</a>
                """ %
                {
                    "card_name": c['card_title'], 
                    "img_src": thumb(c['image_number'], 200),
                    "is_maverick": mav % co['house'] if co['is_maverick'] else '',
                    "is_anomaly": anomaly % co['house'] if co['is_anomaly'] else '',
                    "is_enhanced": enhanced if co['is_enhanced'] else ''
                }
            )
        return "".join(wc(card.aa_format(), card.data) for card in self.deck.get_cards())

    def commentary(self):
        texts = {}
        params = {
            "tables": "RuleData",
            "fields": "RulesText, RulesType, RulesSource, RulesPages, RulesDate"
        }
        params["group_by"] = params["fields"]
        print(params)
        results = cargo_query(params)
        print(len(results['cargoquery']))
        cards = [(card.aa_format(), card.data) for card in self.deck.get_cards()]

        def cards_in_text(result, rule_types):
            for card in cards:
                if (
                    (
                        (card[0]['card_title'] in result['RulesText'] and not result['RulesPages']) or
                        (card[0]['card_title'] in result['RulesPages'])
                    ) and (result['RulesType'] in rule_types)
                    and '//' in result['RulesText']
                ):
                    yield card

        for result in results['cargoquery']:
            result = result['title']
            matched = [c[0]['card_title'] for c in cards_in_text(result, ['FFGRuling', 'FAQ'])]
            if not matched:
                continue
            t = result['RulesText']
            if t in texts:
                texts[t]['cards'].extend(matched)
            else:
                texts[t] = {**result}
                texts[t]['cards'] = matched
            texts[t]['cards'] = [n for n in set(texts[t]['cards'])]

        sorted_texts = sorted(
            texts.values(),
            key=lambda o: tuple(sorted(o['cards']))
        )
        r = []
        for result in sorted_texts:
            r.append(
                ", ".join(result['cards']) +
                "<br>" +
                FAQ % {
                    "RulesType": result['RulesType'],
                    "RulesSource": result["RulesSource"],
                    "RulesText": result["RulesText"]
                }
            )
        if r:
            r.insert(0, "\n== Rulings ==\n")
        return "\n".join(r)

    def write(self):
        fields = []
        fields.append('<templatestyles src="Template:Deck/style.css" />')
        fields.append(
            (
                '<div class="deckjson" style="display:none"><nowiki>' +
                '{json_data}' +
                '</nowiki></div>'
            ).format(json_data=json.dumps(self.deck_json()))
        )
        fields.append('<div class="deck_contents"></div>')
        return "\n".join(fields)


def write(deck):
    return DeckWriter(deck).write()
