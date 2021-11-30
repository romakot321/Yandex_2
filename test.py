import unittest
import character
from datetime import datetime as dt

class Test(unittest.TestCase):
    def test_test(self):
        self.assertTrue(True)


class TestHero(unittest.TestCase):
    def test_update(self):
        hero = character.Hero()
        hero.lasttime = dt(2000, 1, 1, 1)
        hero.is_moving = False
        self.assertEqual(hero.velocity, (0, 0))
        hero.update()
        self.assertEqual(hero.velocity, (0, 0))
        hero.lasttime = dt(2000, 1, 1, 1)
        hero.is_moving = True
        hero.update()
        self.assertNotEqual(hero.velocity, (0, 0))
        with self.subTest():
            for i in range(1000):
                hero = character.Hero()
                hero.lasttime = dt(2000, 1, 1, 1)
                hero.update()
                self.assertNotEqual(hero.velocity, (0, 0))


    def test_velocity(self):
        hero = character.Hero()
        hero.add_velocity((1, 2))
        self.assertEqual(hero.velocity, (1, 2))
        hero.add_velocity((-1000, -1000))
        self.assertEqual(hero.velocity, (-999, -998))
        with self.subTest():
            for i in range(-100, 100):
                for j in range(-100, 100):
                    hero.set_velocity(0, 0)
                    hero.add_velocity((i * character.BLOCK_SIZE, 
                                       j * character.BLOCK_SIZE))
                    self.assertEqual(hero.velocity, (i * character.BLOCK_SIZE, 
                                                     j * character.BLOCK_SIZE))
                    hero.update()

    def test_character(self):
        pass


class TestNPC(unittest.TestCase):
    def test_creating(self):
        npc = character.NPC(-1, 0, None)

    def test_character(self):
        pass

         
class TestCharacter(unittest.TestCase):
    def test_creating(self):
        c = character.Character(156, -14)
        self.assertIsInstance(c.health, int or float)

    def test_move(self):
        pass

    def test_inventory(self):
        pass


if __name__ == "__main__":
    unittest.main()

