from numpy.random import randint, normal, choice, seed
from numpy import linspace

PATH_TO_CHAIN_FILES = 'incerto/chains/'
STANDARD_DEVIATION = 60
DEPTH_BETWEEN_TABLES = 1000


class Incerto(object):
    '''High level class for the melody generator.'''
    def __init__(self, given_seed=None):
        self.set_seed(given_seed)
        self.p_chain, self.r_chain = Chain('pitch'), Chain('rythm')
        self.note_gen = self.note_generator()

    def set_seed(self, seed_given):
        if seed_given is None:
            seed_given = randint(low=0, high=2**32 - 1, dtype='uint32')
        try:
            seed(seed_given)
            self.instance_seed = seed_given
        except ValueError:
            raise ValueError('Value error. Seed must be convertible to 32 '
                             'bit unsigned integers.')

    def note_generator(self):
        while True:
            rythmic_cell = self.r_chain.content[self.r_chain.current_state]
            for duration_in_ms in rythmic_cell:
                pitch_state = self.p_chain.draw_next_state(self.chain_change)
                MIDI_pitch = self.p_chain.content[pitch_state][0]
                pause_or_note = 1 if duration_in_ms > 0 else 0
                yield [MIDI_pitch, pause_or_note, abs(duration_in_ms)]
            self.r_chain.draw_next_state(self.chain_change)

    def draw_note(self, chain_change):
        self.chain_change = chain_change
        return next(self.note_gen)


class Chain(object):
    ''' A Markov Chain for musical parameters. It loads files from the 'chains'
    directory. The only interface it provides is the 'draw_next_state' method,
    which accepts the argument 'depth_of_table'. This argument relates to a
    interpolation between the original probability table and its modified
    version.The starting state of the chain is drawn from uniform distribution.

    Class atributes:
        - chain_type: specifies whether it's a 'rythm' or a 'pitch' chain,
        - states: an array of indicies refferent to the chain's states.
        - content: an array of the content related to each state.
        - original_table: the transition probability table.
        - uncertain_table: a modified version of the original table.
        '''
    def __init__(self, chain_type):
        self.chain_type = chain_type
        self.three_d_transition_table = self.setup_tables()
        self.current_state = randint(self.table_size)

    def setup_tables(self):
        self.content, self.original_table = self.parse_file(self.read_file())
        self.uncertain_table = self.modify_table(self.original_table)
        self.states = self.make_state_array()
        self.deal_with_table_type()
        return self.interpolate_tables(self.original_table,
                                       self.uncertain_table)

    def read_file(self):
        try:
            with open(''.join([PATH_TO_CHAIN_FILES,
                               self.chain_type]), 'r') as f:
                file_lines = f.readlines()
        except IOError:
            raise IOError('File not found. Make sure chain_type is either'
                          '"pitch" or "rythm". In case of error even after'
                          'argument complience, check for files'
                          'in the chains/ folder.')
        except TypeError:
            raise TypeError('Type error. The function read_file must receive '
                            'a string, either "pitch" or "rythm".')
        return file_lines

    def parse_file(self, file):
        self.table_size = int(file[0].split()[0])
        content = []
        probabilities = []
        for i in range(self.table_size):
            state_content = list(map(int,
                                 file[1 + self.table_size + i][2:-1].split()))
            content.append(state_content)
            transition_probabilities = list(map(int, file[1 + i].split()))
            probabilities.append(transition_probabilities)
        return content, probabilities

    def modify_table(self, in_probabilities):
        out_probabilities = []
        for in_line in in_probabilities:
            out_line = []
            for probability in in_line:
                if probability != 0:
                    out_line.append(abs(normal(probability,
                                               STANDARD_DEVIATION)))
                else:
                    out_line.append(0)
            out_probabilities.append(out_line)
        return out_probabilities

    def make_state_array(self):
        return list(linspace(0, self.table_size, self.table_size,
                             endpoint=False, dtype='int'))

    def deal_with_table_type(self):
        if self.chain_type == 'rythm':
            self.swap(self.original_table, self.uncertain_table)

    def swap(self, a, b):
        return b, a

    def interpolate_tables(self, a_table, b_table):
        state_axis = []
        for i in range(self.table_size):
            probability_axis = []
            for j in range(self.table_size):
                depth_axis = list(linspace(a_table[i][j],
                                           b_table[i][j],
                                           DEPTH_BETWEEN_TABLES))
                probability_axis.append(depth_axis)
            state_axis.append(probability_axis)
        return(state_axis)

    def draw_next_state(self, depth_of_table):
        z = int(depth_of_table * 1000)
        try:
            weights = [self.three_d_transition_table[self.current_state][i][z]
                       for i in range(self.table_size)]
        except IndexError:
            raise IndexError('IndexError: depth_of_table should'
                             ' be between 0 and 0.999.')
        self.current_state = choice(self.states, p=self.normalize(weights))
        return self.current_state

    def normalize(self, array):
        summation = sum(array)
        return [i / summation for i in array]
