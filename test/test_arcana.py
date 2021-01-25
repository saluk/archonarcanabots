from splinter import Browser
import pytest
import time

@pytest.fixture
def browser():
    b =  Browser('firefox', headless=True)
    yield b
    b.quit()


def test_cardgallery(browser):
    browser.visit("https://archonarcana.com/Card_Gallery?order_by=House+Name")
    time.sleep(2)
    assert("1127 results" in browser.find_by_css('div.cg-results').first.text)
    autocannon = browser.find_by_css('a[href=Autocannon] img').first
    assert(
        autocannon['src'].find('/thumb.php?f=341-019.png') or
        autocannon['src'].find('/images/d/d8/341-019.png')
    )


def test_topsearch(browser):
    browser.visit("https://archonarcana.com/")
    time.sleep(0.5)
    browser.find_by_css("#searchInput").type("apple")
    time.sleep(5)
    found_card = found_deck = found_containing = found_deck_containing = False
    for link in browser.find_by_css("a.mw-searchSuggest-link div img"):
        if "width=40" in link["src"]:
            found_card = True
    for link in browser.find_by_css("a.mw-searchSuggest-link"):
        if "Deck:" in link["href"]:
            found_deck = True
        elif "containing..." in link.text and not "Deck names" in link.text:
            found_containing = True
        elif "Deck names containing..." in link.text:
            found_deck_containing = True
    assert found_card and found_deck and found_containing and found_deck_containing, (found_card, found_deck, found_containing, found_deck_containing)


def get_visible_image(browser):
    for img in browser.find_by_css('.gallery-fullsize img'):
        if img.visible:
            return img

def test_cards(browser):
    #Dark Amber Vault
    browser.visit("https://archonarcana.com/Dark_%C3%86mber_Vault")
    assert browser.find_by_css('.gallery-label2 img.house-logo[alt="Logos.png"]').first
    assert browser.find_by_css('.cardText a').first.text == 'Mutant'
    assert browser.find_by_css('.topRow .house').first.text == 'Multi'
    assert browser.find_by_css('.artist a').first.text == 'Dany Orizio'
    assert '479-001-Dis.png' in get_visible_image(browser)['src']
    browser.find_by_css('.house-logo[alt="Logos.png"]').first.click()
    time.sleep(0.5)
    assert '479-001-Logos.png' in get_visible_image(browser)['src']

    assert 'Chonkers' in browser.find_by_css('.faqQuestion').first.text
    assert 'So Chonkers will still only have 1 power this turn' in browser.find_by_css('.faqAnswer').first.text
    assert browser.find_by_css('#Note').first