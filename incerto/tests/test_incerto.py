import unittest
import incerto

incerto.PATH_TO_CHAIN_FILES = './chains/'


class TestIncerto(unittest.TestCase):

    incerto_instance = incerto.Incerto()

    def test_instance_seed(self):
        self.assertTrue(0 < self.incerto_instance.instance_seed < (2**32 - 1))
        self.assertRaises(ValueError, self.incerto_instance.set_seed, -422316)
        self.assertRaises(TypeError, self.incerto_instance.set_seed, 0.1618)
        self.assertRaises(TypeError, self.incerto_instance.set_seed, 'erro')

    def test_data_types(self):
        note_list = [self.incerto_instance.draw_note(i * 0.001)
                     for i in range(999)]
        for note in note_list:
            self.assertEqual(len(note), 3)
            for item in note:
                self.assertTrue(type(item) is int)
            self.assertTrue(note[0] >= 0 and note[0] < 128)
            self.assertTrue(note[1] == 0 or note[1] == 1)
            self.assertTrue(note[2] > 0)


class TestChain(unittest.TestCase):

    instances = [incerto.Chain('rythm'), incerto.Chain('pitch')]

    def test_read_file(self):
        self.assertRaises(IOError, incerto.Chain, 'yikes!')
        self.assertRaises(TypeError, incerto.Chain, 1245)

    def test_instances(self):
        for instance in self.instances:
            self.assertIsInstance(instance, incerto.Chain)

    def test_table_size(self):
        for instance in self.instances:
            self.assertEqual(instance.table_size,
                             len(instance.content))
            self.assertEqual(len(instance.content),
                             len(instance.original_table))
            self.assertEqual(len(instance.original_table),
                             len(instance.original_table[0]))

    def test_swap(self):
        self.assertEqual((1, 0), self.instances[0].swap(0, 1))

    def test_normalize(self):
        self.assertEqual([0.2, 0.6, 0.2],
                         self.instances[0].normalize([1, 3, 1]))

    def test_next_state(self):
        self.assertRaises(IndexError, self.instances[0].draw_next_state, 1)
        self.assertRaises(IndexError, self.instances[0].draw_next_state, -2)
        self.assertIn(self.instances[0].draw_next_state(0.5),
                      self.instances[0].states)


if __name__ == '__main__':
    unittest.main()
