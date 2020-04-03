from pyutilib.misc.timing import HierarchicalTimer
import pyutilib.th as unittest


class TestHierarchicalTimer(unittest.TestCase):
    def test_hierarchical_timer(self):
        timer = HierarchicalTimer()
        timer.start_increment('all')
        for i in range(10):
            timer.start_increment('a')
            for i in range(5):
                timer.start_increment('aa')
                timer.stop_increment('aa')
            timer.start_increment('ab')
            timer.stop_increment('ab')
            timer.stop_increment('a')
            timer.start_increment('b')
            timer.stop_increment('b')
        timer.start_increment('a')
        with self.assertRaisesRegex(ValueError, 'all is not the currently active timer. The only timer that can currently be stopped is all.a'):
            timer.stop_increment('all')
        timer.stop_increment('a')
        timer.stop_increment('all')

        a_percent = timer.get_relative_percent_time('all.a')
        aa_percent = timer.get_relative_percent_time('all.a.aa')
        aa_total_percent = timer.get_total_percent_time('all.a.aa')
        self.assertAlmostEqual(aa_total_percent, a_percent/100 * aa_percent/100 * 100)
        self.assertAlmostEqual(timer.get_num_calls('all.a'), 11)
        self.assertAlmostEqual(timer.get_num_calls('all.a.ab'), 10)
        self.assertAlmostEqual(timer.get_num_calls('all.a.aa'), 50)
        timer.get_total_time('all.b')
        print(timer)
