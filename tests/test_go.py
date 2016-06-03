import unittest
import go

MANUAL_EMPTY_BOARD = '''         
.........
.........
.........
.........
.........
.........
.........
.........
.........
          '''

EMPTY_ROW = '.' * go.N + '\n'
TEST_BOARD = go.load_board('''
.X.....OO
X........
''' + EMPTY_ROW * 7)

pc = go.parse_coords
def pc_set(string):
    return set(map(pc, string.split()))

class TestGoBoard(unittest.TestCase):
    def test_load_board(self):
        self.assertEqual(len(go.EMPTY_BOARD), (go.W * (go.W + 1)))
        self.assertEqual(go.EMPTY_BOARD, MANUAL_EMPTY_BOARD)
        self.assertEqual(go.EMPTY_BOARD, go.load_board('. \n' * go.N ** 2))

    def test_parsing(self):
        self.assertEqual(pc('A' + str(go.N)), go.W)

    def test_neighbors(self):
        corner = pc('A1')
        neighbors = [go.EMPTY_BOARD[c] for c in go.neighbors(corner)]
        self.assertEqual(sum(1 for n in neighbors if n.isspace()), 2)

        side = pc('A2')
        side_neighbors = [go.EMPTY_BOARD[c] for c in go.neighbors(side)]
        self.assertEqual(sum(1 for n in side_neighbors if n.isspace()), 1)

class TestGroupHandling(unittest.TestCase):
    def test_flood_fill(self):
        expected_board = go.load_board('''
            .X.....##
            X........
        ''' + EMPTY_ROW * 7)
        actual_board, _ = go.flood_fill(TEST_BOARD, pc('H9'))
        self.assertEqual(expected_board, actual_board)

    def test_find_liberties(self):
        stones = pc_set('H9 J9')
        expected_liberties = pc_set('G9 H8 J8')
        actual_liberties = go.find_liberties(TEST_BOARD, stones)
        self.assertEqual(expected_liberties, actual_liberties)

    def test_deduce_groups(self):
        expected_groups = ([
            go.Group(
                stones=pc_set('B9'),
                liberties=pc_set('A9 C9 B8')
            ),
            go.Group(
                stones=pc_set('A8'),
                liberties=pc_set('A9 A7 B8')
            ),
            ], [
            go.Group(
                stones=pc_set('H9 J9'),
                liberties=pc_set('G9 H8 J8')
            )
            ]
        )
        actual_groups = go.deduce_groups(TEST_BOARD)
        self.assertEqual(expected_groups, actual_groups)

    def test_update_groups(self):
        existing_X_groups, existing_O_groups = go.deduce_groups(TEST_BOARD)
        updated_board = go.place_stone(TEST_BOARD, 'X', pc('A9'))
        updated_X_groups, updated_O_groups = go.update_groups(updated_board, existing_X_groups, existing_O_groups, pc('A9'))
        self.assertEqual(updated_X_groups, [go.Group(
            stones=pc_set('A8 A9 B9'),
            liberties=pc_set('A7 B8 C9')
        )])
        self.assertEqual(existing_O_groups, updated_O_groups)

class TestEyeHandling(unittest.TestCase):
    def test_eyeish(self):
        self.assertEqual(go.is_eyeish(TEST_BOARD, pc('A9')), 'X')
        self.assertEqual(go.is_eyeish(TEST_BOARD, pc('B8')), None)
        self.assertEqual(go.is_eyeish(TEST_BOARD, pc('B9')), None)

    def test_likely_eye(self):
        board = go.load_board('''
            XX.X.....
            X.XO.....
            .XOO.....
            X........
        ''' + EMPTY_ROW * 5)
        self.assertEqual(go.is_likely_eye(board, pc('A7')), 'X')
        self.assertEqual(go.is_likely_eye(board, pc('B8')), 'X')
        self.assertEqual(go.is_likely_eye(board, pc('C9')), None)
        self.assertEqual(go.is_likely_eye(board, pc('A9')), None)

class TestPosition(unittest.TestCase):
    def assertEqualPositions(self, position1, position2):
        def sort_groups(groups):
            return sorted(groups, key=lambda g: sorted(g.stones) + sorted(g.liberties))
        canonical_p1 = position1._replace(groups=tuple(map(sort_groups, position1.groups)))
        canonical_p2 = position2._replace(groups=tuple(map(sort_groups, position2.groups)))
        self.assertEqual(canonical_p1, canonical_p2)

    def test_move(self):
        start_board = go.load_board(EMPTY_ROW * 5 + '''
            XXXX.....
            XOOX.....
            O.OX.....
            OOXX.....
        ''')
        start_position = go.Position(
            board=start_board,
            n=0,
            caps=(1, 2),
            groups=go.deduce_groups(start_board),
            ko=None
        )
        expected_board = go.load_board(EMPTY_ROW * 5 + '''
            OOOO.....
            O..O.....
            .O.O.....
            ..OO.....
        ''')
        expected_position = go.Position(
            board=expected_board,
            n=1,
            caps=(2, 7),
            groups=go.deduce_groups(expected_board),
            ko=None
        )
        actual_position = start_position.play_move(pc('B2'))
        self.assertEqualPositions(actual_position, expected_position)

    def test_ko_move(self):
        start_board = go.load_board('''
            .OX......
            OX.......
        ''' + EMPTY_ROW * 7)
        start_position = go.Position(
            board=start_board,
            n=0,
            caps=(1, 2),
            groups=go.deduce_groups(start_board),
            ko=None
        )
        expected_board = go.load_board('''
            O.O......
            XO.......
        ''' + EMPTY_ROW * 7)
        expected_position = go.Position(
            board=expected_board,
            n=1,
            caps=(2, 2),
            groups=go.deduce_groups(expected_board),
            ko=pc('A9')
        )
        actual_position = start_position.play_move(pc('A9'))

        self.assertEqualPositions(actual_position, expected_position)
