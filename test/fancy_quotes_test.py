import unittest

from models import fancy_quotes


class FancyQuoteTests(unittest.TestCase):

  def test_fancy(self):

      # Turn simple quotes into the correct left vs right fancy.
      a = fancy_quotes.force(
          'Shea "Cloudkicker"')
      e = 'Shea “Cloudkicker”'
      self.assertEqual(a, e)

      # Same but at front of string.
      a = fancy_quotes.force(
          '"Cloudkicker" Shea')
      e = '“Cloudkicker” Shea'
      self.assertEqual(a, e)

      # Turn simple apostrophe into fancy.
      a = fancy_quotes.force(
          "Flint's Stash")
      e = "Flint’s Stash"
      self.assertEqual(a, e)

      # Don't change fancy that are already good.
      a = fancy_quotes.force(
          """It said, “Can’t allow.”""")
      e = """It said, “Can’t allow.”"""
      self.assertEqual(a, e)

      # Fix two right fancy quotes and an apostrophe.
      a = fancy_quotes.force(
          "”It's only theoretical until it occurs.”\n")
      e = "“It’s only theoretical until it occurs.”\n"
      self.assertEqual(a, e)

      # Fix two left fancy quotes and an apostrophe.
      a = fancy_quotes.force(
          "“It's only theoretical until it occurs.“\n")
      e = "“It’s only theoretical until it occurs.”\n"
      self.assertEqual(a, e)

      # Find fixes across and adjacent to newlines.
      a = fancy_quotes.force(
          '''"One"\n"Two" it's "Three"\n"Four"''')
      e = '''“One”\n“Two” it’s “Three”\n“Four”'''
      self.assertEqual(a, e)
