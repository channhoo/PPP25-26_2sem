from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Set

# --- Константы и Типы ---
Color = str  # 'white' или 'black'
Position = Tuple[int, int]  # (row, col) от 0 до 7

# =============================================================================
# 1. ИЕРАРХИЯ ФИГУР (Полиморфизм и Наследование)
# =============================================================================

class Piece(ABC):
    """Базовый класс для всех игровых фигур"""
    def __init__(self, color: Color, position: Position):
        self._color = color
        self._position = position

    @property
    def color(self) -> Color:
        return self._color

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value: Position):
        self._position = value

    @abstractmethod
    def get_symbol(self) -> str:
        """Возвращает символ фигуры для отображения"""
        pass

    @abstractmethod
    def get_possible_moves(self, board: 'Board') -> List[Position]:
        """Возвращает список допустимых координат для хода (геометрия)"""
        pass

    def __str__(self):
        return self.get_symbol()


# --- Шахматные фигуры ---

class Pawn(Piece):
    def get_symbol(self) -> str:
        return 'P' if self.color == 'white' else 'p'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        r, c = self.position
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Ход вперёд на 1 клетку
        if board.is_empty((r + direction, c)):
            moves.append((r + direction, c))
            # Ход вперёд на 2 клетки (ТОЛЬКО со стартовой позиции)
            if r == start_row and board.is_empty((r + 2 * direction, c)):
                moves.append((r + 2 * direction, c))
        
        # Взятие по диагонали (только одна фигура за ход)
        for dc in [-1, 1]:
            target = (r + direction, c + dc)
            if board.is_within_bounds(target):
                target_piece = board.get_piece(target)
                if target_piece and target_piece.color != self.color:
                    moves.append(target)
        return moves


class Rook(Piece):
    def get_symbol(self) -> str:
        return 'R' if self.color == 'white' else 'r'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        return self._get_sliding_moves(board, [(0, 1), (0, -1), (1, 0), (-1, 0)])

    def _get_sliding_moves(self, board: 'Board', directions: List[Tuple[int, int]]) -> List[Position]:
        moves = []
        r, c = self.position
        for dr, dc in directions:
            for step in range(1, 8):
                nr, nc = r + dr * step, c + dc * step
                if not board.is_within_bounds((nr, nc)):
                    break
                target = board.get_piece((nr, nc))
                if target is None:
                    moves.append((nr, nc))
                else:
                    if target.color != self.color:
                        moves.append((nr, nc))
                    break
        return moves


class Knight(Piece):
    def get_symbol(self) -> str:
        return 'N' if self.color == 'white' else 'n'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        r, c = self.position
        offsets = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if board.is_within_bounds((nr, nc)):
                target = board.get_piece((nr, nc))
                if target is None or target.color != self.color:
                    moves.append((nr, nc))
        return moves


class Bishop(Piece):
    def get_symbol(self) -> str:
        return 'B' if self.color == 'white' else 'b'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        return self._get_sliding_moves(board, [(1,1),(1,-1),(-1,1),(-1,-1)])
    
    def _get_sliding_moves(self, board: 'Board', directions: List[Tuple[int, int]]) -> List[Position]:
        moves = []
        r, c = self.position
        for dr, dc in directions:
            for step in range(1, 8):
                nr, nc = r + dr * step, c + dc * step
                if not board.is_within_bounds((nr, nc)):
                    break
                target = board.get_piece((nr, nc))
                if target is None:
                    moves.append((nr, nc))
                else:
                    if target.color != self.color:
                        moves.append((nr, nc))
                    break
        return moves


class Queen(Piece):
    def get_symbol(self) -> str:
        return 'Q' if self.color == 'white' else 'q'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        r, c = self.position
        for dr, dc in directions:
            for step in range(1, 8):
                nr, nc = r + dr * step, c + dc * step
                if not board.is_within_bounds((nr, nc)):
                    break
                target = board.get_piece((nr, nc))
                if target is None:
                    moves.append((nr, nc))
                else:
                    if target.color != self.color:
                        moves.append((nr, nc))
                    break
        return moves


class King(Piece):
    def get_symbol(self) -> str:
        return 'K' if self.color == 'white' else 'k'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        r, c = self.position
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if board.is_within_bounds((nr, nc)):
                    target = board.get_piece((nr, nc))
                    if target is None or target.color != self.color:
                        moves.append((nr, nc))
        return moves


# --- Шашечные фигуры (упрощённая версия) ---

class Checker(Piece):
    """Обычная шашка: ходит и бьёт по диагонали вперёд, без дамок"""
    def get_symbol(self) -> str:
        return 'O' if self.color == 'white' else 'o'

    def get_possible_moves(self, board: 'Board') -> List[Position]:
        moves = []
        r, c = self.position
        direction = -1 if self.color == 'white' else 1
        
        # Обычный ход на 1 клетку по диагонали вперёд
        for dc in [-1, 1]:
            target = (r + direction, c + dc)
            if board.is_within_bounds(target) and board.is_empty(target):
                moves.append(target)
        
        # Взятие: прыжок через вражескую шашку
        for dc in [-1, 1]:
            jump_target = (r + 2 * direction, c + 2 * dc)
            mid_target = (r + direction, c + dc)
            
            if board.is_within_bounds(jump_target) and board.is_empty(jump_target):
                mid_piece = board.get_piece(mid_target)
                if mid_piece and mid_piece.color != self.color:
                    moves.append(jump_target)
        return moves


# =============================================================================
# 2. КЛАСС ХОДА (Для системы отката)
# =============================================================================

class Move:
    """Объект, описывающий один сделанный ход"""
    def __init__(self, piece: Piece, start: Position, end: Position, captured: Optional[Piece]):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured  # Съеденная фигура (если была)

    def __str__(self):
        capture_mark = "x" if self.captured else "-"
        return f"{self.piece.get_symbol()}{capture_mark}{self._pos_to_str(self.end)}"
    
    def _pos_to_str(self, pos: Position) -> str:
        return f"{chr(97 + pos[1])}{8 - pos[0]}"


# =============================================================================
# 3. КЛАСС ДОСКИ (Инкапсуляция состояния)
# =============================================================================

class Board:
    """Базовый класс игровой доски 8x8"""
    def __init__(self):
        self._grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]

    def _setup_initial_position(self):
        """Переопределяется в наследниках для расстановки фигур"""
        pass

    def is_within_bounds(self, pos: Position) -> bool:
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def get_piece(self, pos: Position) -> Optional[Piece]:
        if not self.is_within_bounds(pos):
            return None
        return self._grid[pos[0]][pos[1]]

    def is_empty(self, pos: Position) -> bool:
        return self.get_piece(pos) is None

    def set_piece(self, pos: Position, piece: Optional[Piece]):
        if self.is_within_bounds(pos):
            self._grid[pos[0]][pos[1]] = piece
            if piece:
                piece.position = pos

    def find_king(self, color: Color) -> Optional[Position]:
        """Находит короля указанного цвета (для шахмат)"""
        for r in range(8):
            for c in range(8):
                p = self._grid[r][c]
                if p and isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    def is_square_attacked(self, pos: Position, by_color: Color) -> bool:
        """Проверяет, атакует ли фигура цвета by_color клетку pos"""
        for r in range(8):
            for c in range(8):
                piece = self._grid[r][c]
                if piece and piece.color == by_color:
                    if pos in piece.get_possible_moves(self):
                        return True
        return False

    def is_check(self, color: Color) -> bool:
        """Проверяет, находится ли король цвета color под шахом"""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        enemy_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king_pos, enemy_color)

    def get_threatened_positions(self, my_color: Color) -> Set[Position]:
        """Возвращает множество клеток, находящихся под ударом врага"""
        threatened = set()
        enemy_color = 'black' if my_color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self._grid[r][c]
                if piece and piece.color == enemy_color:
                    for m in piece.get_possible_moves(self):
                        threatened.add(m)
        return threatened

    def display(self, threatened_squares: Set[Position] = None, check_mode: bool = False):
        """Отображает доску с подсветкой угроз и шаха"""
        if threatened_squares is None:
            threatened_squares = set()

        print("\n    a   b   c   d   e   f   g   h")
        print("  +---+---+---+---+---+---+---+---+")
        
        for r in range(8):
            print(f"{8 - r} |", end="")
            for c in range(8):
                piece = self._grid[r][c]
                if piece:
                    symbol = piece.get_symbol()
                    is_threatened = (r, c) in threatened_squares
                    is_king_in_check = (check_mode and isinstance(piece, King) 
                                       and self.is_check(piece.color))
                    
                    if is_king_in_check:
                        print(f"!{symbol}!|", end="")  # Шах!
                    elif is_threatened:
                        print(f"[{symbol}]|", end="")  # Под боем
                    else:
                        print(f" {symbol} |", end="")
                else:
                    if (r, c) in threatened_squares:
                        print(" * |", end="")  # Пустая клетка под ударом
                    else:
                        print("   |", end="")
            print(f" {8 - r}")
            print("  +---+---+---+---+---+---+---+---+")
        
        print("    a   b   c   d   e   f   g   h\n")


class ChessBoard(Board):
    """Доска для шахмат с классической расстановкой"""
    def _setup_initial_position(self):
        # Белые фигуры (ряды 6-7, индексы)
        for c in range(8):
            self._grid[6][c] = Pawn('white', (6, c))
        
        self._grid[7][0] = Rook('white', (7, 0))
        self._grid[7][1] = Knight('white', (7, 1))
        self._grid[7][2] = Bishop('white', (7, 2))
        self._grid[7][3] = Queen('white', (7, 3))
        self._grid[7][4] = King('white', (7, 4))
        self._grid[7][5] = Bishop('white', (7, 5))
        self._grid[7][6] = Knight('white', (7, 6))
        self._grid[7][7] = Rook('white', (7, 7))

        # Чёрные фигуры (ряды 0-1)
        for c in range(8):
            self._grid[1][c] = Pawn('black', (1, c))
        
        self._grid[0][0] = Rook('black', (0, 0))
        self._grid[0][1] = Knight('black', (0, 1))
        self._grid[0][2] = Bishop('black', (0, 2))
        self._grid[0][3] = Queen('black', (0, 3))
        self._grid[0][4] = King('black', (0, 4))
        self._grid[0][5] = Bishop('black', (0, 5))
        self._grid[0][6] = Knight('black', (0, 6))
        self._grid[0][7] = Rook('black', (0, 7))


class CheckersBoard(Board):
    """Доска для упрощённых шашек"""
    def _setup_initial_position(self):
        # Чёрные шашки (верх, ряды 0-2) — только на тёмных клетках
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:  # Тёмные клетки
                    self._grid[r][c] = Checker('black', (r, c))
        
        # Белые шашки (низ, ряды 5-7) — только на тёмных клетках
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self._grid[r][c] = Checker('white', (r, c))


# =============================================================================
# 4. КОНТРОЛЛЕР ИГРЫ (Логика, валидация, история)
# =============================================================================

class ChessGame:
    """Контроллер для игры в шахматы"""
    def __init__(self):
        self.board = ChessBoard()
        self.board._setup_initial_position()
        self.current_turn = 'white'
        self.history: List[Move] = []
        self.is_game_over = False
        self.game_name = "Шахматы"

    def get_valid_moves_for_piece(self, piece: Piece) -> List[Position]:
        """Фильтрует геометрические ходы, оставляя только легальные (без шаха)"""
        raw_moves = piece.get_possible_moves(self.board)
        valid_moves = []
        
        for target in raw_moves:
            # Симуляция хода
            original_target = self.board.get_piece(target)
            original_pos = piece.position
            
            self.board.set_piece(target, piece)
            self.board.set_piece(original_pos, None)
            
            # Проверяем, не остался ли свой король под шахом
            if not self.board.is_check(piece.color):
                valid_moves.append(target)
            
            # Отмена симуляции
            self.board.set_piece(original_pos, piece)
            self.board.set_piece(target, original_target)
            
        return valid_moves

    def make_move(self, start: Position, end: Position) -> bool:
        """Пытается сделать ход, возвращает True при успехе"""
        piece = self.board.get_piece(start)
        
        if not piece or piece.color != self.current_turn:
            print("❌ Неверная фигура или не ваш ход.")
            return False

        valid_moves = self.get_valid_moves_for_piece(piece)
        if end not in valid_moves:
            print("❌ Недопустимый ход (правила или шах).")
            return False

        # Фиксация хода
        captured = self.board.get_piece(end)
        move_obj = Move(piece, start, end, captured)
        
        self.board.set_piece(end, piece)
        self.board.set_piece(start, None)
        
        # Превращение пешки в ферзя
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and end[0] == 0) or \
               (piece.color == 'black' and end[0] == 7):
                new_queen = Queen(piece.color, end)
                self.board.set_piece(end, new_queen)
                move_obj.piece = new_queen

        self.history.append(move_obj)
        
        # Проверка окончания игры
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        if self.board.is_check(self.current_turn):
            if not self._has_any_valid_moves(self.current_turn):
                winner = 'белые' if self.current_turn == 'black' else 'чёрные'
                print(f"♔ МАТ! Победили {winner}! ♔")
                self.is_game_over = True
        elif not self._has_any_valid_moves(self.current_turn):
            print("♔ ПАТ! Ничья. ♔")
            self.is_game_over = True

        return True

    def _has_any_valid_moves(self, color: Color) -> bool:
        """Проверяет, есть ли у игрока цвета color хотя бы один легальный ход"""
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece((r, c))
                if p and p.color == color:
                    if self.get_valid_moves_for_piece(p):
                        return True
        return False

    def undo_move(self):
        """Отменяет последний ход"""
        if not self.history:
            print("⚠ Нет ходов для отката.")
            return
        
        last_move = self.history.pop()
        self.board.set_piece(last_move.start, last_move.piece)
        self.board.set_piece(last_move.end, last_move.captured)
        self.current_turn = last_move.piece.color
        print(f"↩ Ход отменён: {last_move}")

    def show_hints(self, pos: Position):
        """Показывает допустимые ходы для фигуры на позиции pos"""
        piece = self.board.get_piece(pos)
        if not piece or piece.color != self.current_turn:
            print("⚠ Выберите свою фигуру.")
            return
        
        moves = self.get_valid_moves_for_piece(piece)
        readable = [f"{chr(97 + c)}{8 - r}" for r, c in moves]
        print(f"💡 Ходы для {piece.get_symbol()}{pos}: {', '.join(readable) or 'нет'}")

    def parse_input(self, text: str) -> Optional[Position]:
        """Преобразует строку типа 'e2' в кортеж (6, 4)"""
        try:
            col = ord(text[0].lower()) - ord('a')
            row = 8 - int(text[1])
            return (row, col) if self.board.is_within_bounds((row, col)) else None
        except:
            return None

    def run(self):
        """Главный игровой цикл"""
        print(f"\n🎮 {self.game_name} (OOP-версия) 🎮")
        print("Команды: 'e2 e4' (ход) | 'undo' (откат) | 'hint e2' (подсказка) | 'exit'")
        
        while not self.is_game_over:
            threatened = self.board.get_threatened_positions(self.current_turn)
            is_check = self.board.is_check(self.current_turn)
            
            self.board.display(threatened, is_check)
            status = "♔ ШАХ! ♔" if is_check else ""
            print(f"➤ Ход: {'⚪ Белые' if self.current_turn == 'white' else '⚫ Чёрные'} {status}")
            
            cmd = input("\nВаш ход > ").strip().lower()
            
            if cmd == 'exit':
                print("👋 Спасибо за игру!")
                break
            if cmd == 'undo':
                self.undo_move()
                continue
            if cmd.startswith('hint'):
                parts = cmd.split()
                if len(parts) == 2:
                    pos = self.parse_input(parts[1])
                    if pos:
                        self.show_hints(pos)
                    else:
                        print("❌ Неверная координата")
                continue

            # Обработка обычного хода
            parts = cmd.split()
            if len(parts) == 2:
                start = self.parse_input(parts[0])
                end = self.parse_input(parts[1])
                if start and end:
                    self.make_move(start, end)
                else:
                    print("❌ Формат: 'e2 e4' (откуда куда)")
            elif cmd:
                print("❌ Неизвестная команда")


class CheckersGame(ChessGame):
    """Контроллер для упрощённой игры в шашки"""
    def __init__(self):
        self.board = CheckersBoard()
        self.board._setup_initial_position()
        self.current_turn = 'white'
        self.history: List[Move] = []
        self.is_game_over = False
        self.game_name = "Шашки (упрощённые)"

    def get_valid_moves_for_piece(self, piece: Piece) -> List[Position]:
        # В упрощённых шашках не проверяем "шах", только геометрия
        return piece.get_possible_moves(self.board)

    def make_move(self, start: Position, end: Position) -> bool:
        piece = self.board.get_piece(start)
        
        if not piece or piece.color != self.current_turn:
            print("❌ Неверная фигура или не ваш ход.")
            return False

        valid_moves = self.get_valid_moves_for_piece(piece)
        if end not in valid_moves:
            print("❌ Недопустимый ход.")
            return False

        captured = None
        # Если был прыжок на 2 клетки — это взятие
        if abs(start[0] - end[0]) == 2:
            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            captured = self.board.get_piece(mid)
            self.board.set_piece(mid, None)  # Убираем съеденную шашку

        move_obj = Move(piece, start, end, captured)
        self.board.set_piece(end, piece)
        self.board.set_piece(start, None)
        self.history.append(move_obj)
        
        # В упрощённой версии: нет дамок, ход всегда переходит
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Проверка победы (нет ходов или нет фигур)
        if not self._has_any_valid_moves(self.current_turn):
            winner = '⚪ Белые' if self.current_turn == 'black' else '⚫ Чёрные'
            print(f"🏆 ПОБЕДА! {winner} выиграли! 🏆")
            self.is_game_over = True

        return True
    
    def run(self):
        """Игровой цикл для шашек (без проверки шаха)"""
        print(f"\n🎮 {self.game_name} 🎮")
        print("Команды: 'a3 b4' (ход) | 'undo' (откат) | 'exit'")
        
        while not self.is_game_over:
            threatened = self.board.get_threatened_positions(self.current_turn)
            self.board.display(threatened, check_mode=False)  # Шаха в шашках нет
            print(f"➤ Ход: {'⚪ Белые' if self.current_turn == 'white' else '⚫ Чёрные'}")
            
            cmd = input("\nВаш ход > ").strip().lower()
            if cmd == 'exit':
                print("👋 Спасибо за игру!")
                break
            if cmd == 'undo':
                self.undo_move()
                continue
            
            parts = cmd.split()
            if len(parts) == 2:
                start = self.parse_input(parts[0])
                end = self.parse_input(parts[1])
                if start and end:
                    self.make_move(start, end)
                else:
                    print("❌ Формат: 'a3 b4'")
            elif cmd:
                print("❌ Неизвестная команда")


# =============================================================================
# ЗАПУСК ПРОГРАММЫ
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("   ШАХМАТНЫЙ СИМУЛЯТОР (Объектно-Ориентированный)")
    print("="*50)
    print("\nВыберите режим игры:")
    print("  1 — ♟️  Шахматы (полные правила)")
    print("  2 — ⚪ Шашки (упрощённые: без дамок, один прыжок)")
    
    while True:
        choice = input("\nВаш выбор (1 или 2) > ").strip()
        if choice == '2':
            game = CheckersGame()
            break
        elif choice == '1':
            game = ChessGame()
            break
        else:
            print("❌ Введите 1 или 2")
    
    game.run()
