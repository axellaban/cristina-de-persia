#!/usr/bin/env python3
"""Regenera todos los gráficos del mod a partir de los originales de data/."""
import make_kid, make_bullrich, make_baton, make_items, make_maximo, make_macri, make_guards, make_title, make_shovels, make_promo

for mod in (make_kid, make_bullrich, make_baton, make_items, make_maximo, make_macri, make_guards, make_title, make_shovels, make_promo):
    print(f"== {mod.__name__}")
    mod.main()
