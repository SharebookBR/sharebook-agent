#!/usr/bin/env python
from __future__ import annotations

import random
import unittest

import cover_prompt_from_url
import cover_roulette


class CoverRouletteTests(unittest.TestCase):
    def test_selects_three_distinct_styles(self):
        direction = cover_roulette.pick_direction(rng=random.Random(7))

        selected = [style["id"] for style in direction["styles"]]
        selected_groups = [style["group"] for style in direction["styles"]]

        self.assertEqual(3, len(selected))
        self.assertEqual(3, len(set(selected)))
        self.assertEqual(3, len(set(selected_groups)))

    def test_keeps_macro_groups_distinct_across_many_seeds(self):
        for seed in range(100):
            with self.subTest(seed=seed):
                direction = cover_roulette.pick_direction(rng=random.Random(seed))
                groups = [style["group"] for style in direction["styles"]]
                self.assertEqual(len(groups), len(set(groups)))

    def test_excludes_recent_styles(self):
        avoided = {
            "serigrafia-editorial",
            "ilustracao-cientifica",
            "diorama-3d",
        }

        direction = cover_roulette.pick_direction(
            rng=random.Random(11),
            avoid_styles=sorted(avoided),
        )

        selected = {style["id"] for style in direction["styles"]}
        self.assertTrue(selected.isdisjoint(avoided))

    def test_excludes_recent_macro_groups(self):
        avoided = {"impresso-colagem", "explicativo-tecnico"}

        direction = cover_roulette.pick_direction(
            rng=random.Random(17),
            avoid_groups=sorted(avoided),
        )

        selected = {style["group"] for style in direction["styles"]}
        self.assertTrue(selected.isdisjoint(avoided))

    def test_seed_is_reproducible(self):
        first = cover_roulette.pick_direction(rng=random.Random(23))
        second = cover_roulette.pick_direction(rng=random.Random(23))

        self.assertEqual(first, second)

    def test_rejects_unknown_style(self):
        with self.assertRaisesRegex(ValueError, "Estilos desconhecidos"):
            cover_roulette.pick_direction(
                rng=random.Random(1),
                avoid_styles=["nao-existe"],
            )

    def test_rejects_unknown_macro_group(self):
        with self.assertRaisesRegex(ValueError, "Macrogrupos desconhecidos"):
            cover_roulette.pick_direction(
                rng=random.Random(1),
                avoid_groups=["nao-existe"],
            )

    def test_rejects_impossible_style_count(self):
        with self.assertRaisesRegex(ValueError, "excede"):
            cover_roulette.pick_direction(
                rng=random.Random(1),
                style_count=len(cover_roulette.STYLE_FAMILIES) + 1,
            )

    def test_prompt_contains_one_block_per_style_and_palette_freedom(self):
        direction = cover_roulette.pick_direction(rng=random.Random(31))
        book = {
            "title": "Livro de Teste",
            "author": "Autora Exemplo",
            "synopsis": "Uma sinopse curta.",
        }

        prompt = cover_prompt_from_url.build_prompt(book, direction)

        for style in direction["styles"]:
            self.assertIn(style["id"], prompt)
            self.assertIn(style["group"], prompt)
        self.assertIn("cores como âncoras", prompt)
        self.assertIn("não misturar as famílias", prompt)
        self.assertIn("Livro de Teste", prompt)


if __name__ == "__main__":
    unittest.main()
