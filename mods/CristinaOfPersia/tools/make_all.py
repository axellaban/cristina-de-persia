#!/usr/bin/env python3
"""Regenera todos los gráficos del mod a partir de los originales de data/."""
import make_kid, make_bullrich, make_flask, make_baton, make_trumpet, make_items, make_maximo, make_macri, make_bufones, make_title, make_shovels, make_promo, make_icon

for mod in (make_kid, make_bullrich, make_flask, make_baton, make_trumpet, make_items, make_maximo, make_macri, make_bufones, make_title, make_shovels, make_promo, make_icon):
    print(f"== {mod.__name__}")
    mod.main()
