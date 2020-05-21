def dequote(t):
    quotes = ['“', '”']
    while '"' in t:
        next = quotes.pop(0)
        t = t.replace('"', next, 1)
        quotes.append(next)
    return t
