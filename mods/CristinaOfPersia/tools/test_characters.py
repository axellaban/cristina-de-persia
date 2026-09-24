"""Contratos de recursos: coordenadas, transparencia y regeneracion reproducible."""
import unittest
from pathlib import Path
from PIL import Image
import make_macri
import make_maximo

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / 'mods/CristinaOfPersia/data'


class CharacterAssetsTest(unittest.TestCase):
    def test_all_frames_keep_engine_dimensions_and_transparency(self):
        groups = [('KID', range(401,620)), ('PV', make_maximo.POSES),
                  ('PV', range(851,889)), ('VIZIER', range(751,785))]
        for folder, resources in groups:
            for resource in resources:
                rel = Path(folder) / f'res{resource}.png'
                with self.subTest(resource=str(rel)):
                    with Image.open(ROOT / 'data' / rel) as source, Image.open(MOD / rel) as result:
                        self.assertEqual(result.size, source.size)
                        self.assertEqual(result.mode, 'P')
                        self.assertEqual(result.info.get('transparency'), 0)
                        self.assertTrue(set(result.convert('RGBA').getchannel('A').tobytes()) <= {0,255})

    def test_maximo_frames_are_reproducible(self):
        for resource in make_maximo.POSES:
            with self.subTest(resource=resource), Image.open(ROOT / f'data/PV/res{resource}.png') as source:
                expected = (make_maximo.embrace(source,resource) if 911<=resource<=916
                            else make_maximo.render(source,resource))
                with Image.open(MOD / f'PV/res{resource}.png') as actual:
                    self.assertEqual(actual.convert('RGBA').tobytes(), expected.convert('RGBA').tobytes())

    def test_mauricio_frames_are_reproducible(self):
        for folder, resources in [('PV', range(851,889)), ('VIZIER', range(753,785))]:
            for resource in resources:
                with self.subTest(folder=folder,resource=resource), Image.open(ROOT / f'data/{folder}/res{resource}.png') as source:
                    expected = make_macri.transform(source)
                    with Image.open(MOD / f'{folder}/res{resource}.png') as actual:
                        self.assertEqual(actual.convert('RGBA').tobytes(), expected.convert('RGBA').tobytes())

    def test_combat_placeholders_stay_invisible(self):
        for resource in (776,777,778):
            with Image.open(MOD / f'VIZIER/res{resource}.png') as image:
                self.assertIsNone(image.convert('RGBA').getbbox())

    def test_combat_effects_are_not_recolored_as_clothing(self):
        for resource in (751,752):
            with Image.open(ROOT / f'data/VIZIER/res{resource}.png') as source, Image.open(MOD / f'VIZIER/res{resource}.png') as result:
                self.assertEqual(source.convert('RGBA').tobytes(),result.convert('RGBA').tobytes())

    def test_mauricio_keeps_vest_shirt_belt_and_blue_eye_when_raising_arm(self):
        required = {make_macri.VEST, make_macri.SHIRT, make_macri.BELT}
        for resource in (851,870,877,879,880,881):
            with self.subTest(resource=resource), Image.open(MOD / f'PV/res{resource}.png') as image:
                self.assertTrue(required <= set(image.tobytes()))
                # En 881 el antebrazo tapa el perfil original.
                if resource != 881:
                    self.assertIn(make_macri.EYE,set(image.tobytes()))

    def test_maximo_tracksuit_stripes_are_on_sleeves_not_only_shoes(self):
        for resource in (801,807,811,921,930):
            eye = make_maximo.POSES[resource][0]
            with self.subTest(resource=resource), Image.open(MOD / f'PV/res{resource}.png') as image:
                upper = image.crop((0,eye[1]+6,image.width,min(image.height-3,eye[1]+18)))
                self.assertIn(make_maximo.WHITE,set(upper.tobytes()))


if __name__ == '__main__':
    unittest.main()
