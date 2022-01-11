import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

import unittest

from edit.mgeo_task import MGeoTask

class TestMGeoTask(unittest.TestCase):
    def test_do_undo(self):
        '''
        do - undo function에 대한 테스트
        '''

        list_obj = list()   

        # do task1
        task1 = MGeoTask()
        task1.do(list_obj, int(10))

        self.assertEqual(len(list_obj), 1)
        self.assertEqual(list_obj[0], 10)

        # do task2
        task2 = MGeoTask()     
        task2.do(list_obj, int(11))

        self.assertEqual(len(list_obj), 2)
        self.assertEqual(list_obj[1], 11)

        # undo task2
        task2.undo()

        self.assertEqual(len(list_obj), 1)
        self.assertEqual(list_obj[0], 10)

        # undo task1
        task1.undo()
        
        self.assertEqual(len(list_obj), 0)


    def test_do_undo_redo(self):
        '''
        do - undo 수행 이후, redo 까지 수행하는 테스트
        '''

        list_obj = list()   

        # do task1
        task1 = MGeoTask()
        task1.do(list_obj, int(10))

        self.assertEqual(len(list_obj), 1)
        self.assertEqual(list_obj[0], 10)

        # do task2
        task2 = MGeoTask()     
        task2.do(list_obj, int(11))

        self.assertEqual(len(list_obj), 2)
        self.assertEqual(list_obj[1], 11)

        # undo task2
        task2.undo()

        self.assertEqual(len(list_obj), 1)
        self.assertEqual(list_obj[0], 10)

        # redo task2
        task2.redo()
        
        self.assertEqual(len(list_obj), 2)
        self.assertEqual(list_obj[1], 11)


if __name__ == '__main__':
    unittest.main()