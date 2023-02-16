from mastervault import master_vault_lookup


def deprecated_markup(page_name):
    p = wp.page(page_name)
    existing = p.read()
    lines = existing.split('\n')
    new = []
    while lines:
        next = lines.pop(0)
        new.append(next)
        if "<!-- mvdecklink " in next:
            alter_line = lines.pop(0)
            parse = wtp.parse(alter_line)
            for l in parse.external_links:
                print(l.text, l.url)
                url = master_vault_lookup(deck_name=l.text)["url"]
                l.url = url
            new.append(parse.pprint())
    updated = "\n".join(new)
    if updated!=existing:
        p.edit(updated,"deck lookups")
