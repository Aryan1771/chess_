import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import chess
from stockfish import Stockfish
import os
import math
import sys
import winsound
from random import randint as r
import chess.pgn
import chess.polyglot
from tkinter import filedialog

# ================= CONFIG =================
SQUARE = 80
MENU, PLAYING = "menu", "playing"
AI_MOVE_DELAY = r(3,10)*1000
MIN_ELO = 800
MAX_ELO = 2400
K_FACTOR = 24
SELECT_COLOR = "#FFD54F"
LAST_MOVE_COLOR = "#AED581"
CHECK_COLOR = "#FF5252"
IMAGE_FILES = {
    "wP": "w_pawn_png_shadow_1024px.png",
    "wR": "w_rook_png_shadow_1024px.png",
    "wN": "w_knight_png_shadow_1024px.png",
    "wB": "w_bishop_png_shadow_1024px.png",
    "wQ": "w_queen_png_shadow_1024px.png",
    "wK": "w_king_png_shadow_1024px.png",
    "bP": "b_pawn_png_shadow_1024px.png",
    "bR": "b_rook_png_shadow_1024px.png",
    "bN": "b_knight_png_shadow_1024px.png",
    "bB": "b_bishop_png_shadow_1024px.png",
    "bQ": "b_queen_png_shadow_1024px.png",
    "bK": "b_king_png_shadow_1024px.png",
}
PROMOTION_MAP = {
    "Queen": chess.QUEEN,
    "Rook": chess.ROOK,
    "Bishop": chess.BISHOP,
    "Knight": chess.KNIGHT
}
# ================= RESOURCE PATH FIX =================
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)



# ================= GUI =================
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess")
        self.root.bind("<Control-z>", self.undo_move)
        self.canvas = tk.Canvas(root, width=8*SQUARE, height=8*SQUARE)
        self.canvas.pack()

        # ✅ FIXED STOCKFISH PATH
        stockfish_path = resource_path("stockfish")
        self.stockfish = Stockfish(
            stockfish_path,
            parameters={"Skill Level": 10}
        )

        self.player_elo = 1200
        self.ai_elo = 1200

        self.images = {}
        self.load_images()
        self.last_move = None
        self.flipped = False
        self.book_path = "book.bin"   # optional opening book
        self.root.bind("<f>", self.flip_board)
        self.root.bind("<Control-s>", self.save_pgn)
        self.root.bind("<Control-l>", self.load_pgn)
        self.board = chess.Board()
        self.state = MENU

        self.selected_square = None
        self.legal_targets = []
        self.last_move = None

        self.white_time = 300
        self.black_time = 300
        self.timed = True

        self.create_slider()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_menu()

    # ================= MENU =================
    def draw_menu(self):
        self.canvas.delete("all")
        self.state = MENU
        self.canvas.create_text(320, 120, text="♟ CHESS", font=("Arial", 32, "bold"))
        self.canvas.create_text(320, 220, text="Timed Game (5 min)", font=("Arial", 18))
        self.canvas.create_text(320, 260, text="Untimed Game", font=("Arial", 18))
    def undo_move(self, event=None):
        if len(self.board.move_stack) >= 2:
            self.board.pop()
            self.board.pop()
            self.draw_board()
    def menu_click(self, event):
        if 200 <= event.y <= 240:
            self.timed = True
        elif 240 < event.y <= 280:
            self.timed = False
        else:
            return
        winsound.Beep(800, 100)
        self.start_game()

    # ================= SLIDER =================
    def create_slider(self):
        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(frame, text="AI Elo").pack(side="left")

        self.elo_slider = tk.Scale(
            frame,
            from_=MIN_ELO,
            to=MAX_ELO,
            orient="horizontal",
            length=300,
            resolution=100,
            command=self.update_ai_elo
        )
        self.elo_slider.set(self.ai_elo)
        self.elo_slider.pack(side="left")

    def update_ai_elo(self, value):
        self.ai_elo = int(value)
        skill = int((self.ai_elo - MIN_ELO) / (MAX_ELO - MIN_ELO) * 20)
        self.stockfish.update_engine_parameters({"Skill Level": max(0, min(20, skill))})
        depth = 5 + skill // 2
        self.stockfish.set_depth(depth)

    # ================= GAME =================
    def start_game(self):
        self.board.reset()
        self.state = PLAYING
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.white_time = 300
        self.black_time = 300
        self.draw_board()
        if self.timed:
            self.update_timer()
    

    def draw_board(self):
        self.canvas.delete("all")

        for r in range(8):
            for c in range(8):
                if not self.flipped:
                    file = c
                    rank = 7 - r
                else:
                    file = 7 - c
                    rank = r
                sq = chess.square(file, rank)
                color = "#EEEED2" if (r + c) % 2 == 0 else "#769656"
                if sq == self.selected_square:
                    color = SELECT_COLOR
                elif self.last_move and sq in self.last_move:
                    color = LAST_MOVE_COLOR
                elif self.board.is_check() and sq == self.board.king(self.board.turn):
                    color = CHECK_COLOR
                x1, y1 = c*SQUARE, r*SQUARE
                self.canvas.create_rectangle(
                    x1, y1, x1+SQUARE, y1+SQUARE,
                    fill=color, outline=""
                )

                piece = self.board.piece_at(sq)
                if piece:
                    key = ("w" if piece.color else "b") + piece.symbol().upper()
                    self.canvas.create_image(
                        x1+SQUARE//2, y1+SQUARE//2,
                        image=self.images[key]
                    )

        self.draw_move_hints()
        self.draw_timer()
        self.draw_arrow()
    def flip_board(self, event=None):
        self.flipped = not self.flipped
        self.draw_board()
    # ================= TIMER =================
    def draw_timer(self):
        if not self.timed:
            return

        wt = f"{self.white_time//60}:{self.white_time%60:02d}"
        bt = f"{self.black_time//60}:{self.black_time%60:02d}"

        self.canvas.create_rectangle(0, 0, 8*SQUARE, 30, fill="#222", outline="")
        self.canvas.create_text(120, 15, text=f"White {wt}", fill="white")
        self.canvas.create_text(520, 15, text=f"Black {bt}", fill="white")
        self.canvas.create_text(
            320, 15,
            text=f"Elo: {self.player_elo} vs {self.ai_elo}",
            fill="white"
        )

    def update_timer(self):
        if self.state != PLAYING or not self.timed:
            return

        if self.board.turn == chess.WHITE:
            self.white_time -= 1
        else:
            self.black_time -= 1

        if self.white_time <= 0:
            self.handle_game_end("loss")
            return
        if self.black_time <= 0:
            self.handle_game_end("win")
            return

        self.draw_board()
        self.root.after(1000, self.update_timer)
    def square_to_screen(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)

        if not self.flipped:
            col = file
            row = 7 - rank
        else:
            col = 7 - file
            row = rank

        return col, row
    def draw_arrow(self):
        if not self.last_move:
            return

        from_sq, to_sq = self.last_move

        col1, row1 = self.square_to_screen(from_sq)
        col2, row2 = self.square_to_screen(to_sq)

        x1 = col1 * SQUARE + SQUARE // 2
        y1 = row1 * SQUARE + SQUARE // 2
        x2 = col2 * SQUARE + SQUARE // 2
        y2 = row2 * SQUARE + SQUARE // 2

        self.canvas.create_line(
            x1, y1, x2, y2,
            width=5,
            fill="#FF6F00",
            arrow=tk.LAST
        )

    # ================= MOVE HINTS =================
    def draw_move_hints(self):
        if self.selected_square is None:
            return

        for t in self.legal_targets:
            col, row = self.square_to_screen(t)

            cx = col * SQUARE + SQUARE // 2
            cy = row * SQUARE + SQUARE // 2

            if self.board.piece_at(t):
                self.canvas.create_oval(
                    cx-18, cy-18, cx+18, cy+18,
                    outline="black", width=3
                )
            else:
                self.canvas.create_oval(
                    cx-6, cy-6, cx+6, cy+6,
                    fill="#333", outline=""
                )
    # ================= INPUT =================
    def handle_click(self, event):
        if self.state == MENU:
            self.menu_click(event)
        else:
            self.click(event)

    def click(self, event):
        col, row = event.x // SQUARE, event.y // SQUARE
        if not self.flipped:
            sq = chess.square(col, 7 - row)
        else:
            sq = chess.square(7 - col, row)
        if self.selected_square is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == chess.WHITE:
                self.selected_square = sq
                self.legal_targets = [
                    m.to_square for m in self.board.legal_moves if m.from_square == sq
                ]
        else:
            move = chess.Move(self.selected_square, sq)

            if self.is_promotion(move):
                choice = simpledialog.askstring(
                    "Promotion", "Queen / Rook / Bishop / Knight"
                )
                if choice not in PROMOTION_MAP:
                    self.selected_square = None
                    self.legal_targets = []
                    self.draw_board()
                    return
                move = chess.Move(
                    self.selected_square, sq,
                    promotion=PROMOTION_MAP[choice]
                )

            if move in self.board.legal_moves:
                self.board.push(move)
                self.last_move = (move.from_square, move.to_square)
                self.draw_board()

                if self.board.is_game_over():
                    self.handle_game_end()
                else:
                    self.ai_move()
            self.selected_square = None
            self.legal_targets = []
            self.draw_board()
            winsound.Beep(800, 100)
    # ================= AI =================
    def save_pgn(self, event=None):
        file = filedialog.asksaveasfilename(
            defaultextension=".pgn",
            filetypes=[("PGN Files", "*.pgn")]
        )
        if not file:
            return

        game = chess.pgn.Game.from_board(self.board)

        with open(file, "w") as f:
            f.write(str(game))
    def load_pgn(self, event=None):
        file = filedialog.askopenfilename(
            filetypes=[("PGN Files", "*.pgn")]
        )
        if not file:
            return

        with open(file) as f:
            game = chess.pgn.read_game(f)

        self.board = game.end().board()
        self.draw_board()
    def ai_move(self):
        # Opening Book First
        if os.path.exists(self.book_path):
            try:
                with chess.polyglot.open_reader(self.book_path) as reader:
                    entry = reader.weighted_choice(self.board)
                    if entry:
                        move = entry.move
                        self.board.push(move)
                        self.last_move = (move.from_square, move.to_square)
                        self.draw_board()
                        return
            except:
                pass
        if self.board.is_game_over():
            self.handle_game_end()
            return
        self.stockfish.set_fen_position(self.board.fen())
        uci = self.stockfish.get_best_move()
        if not uci:
            return
        move = chess.Move.from_uci(uci)
        self.root.after(AI_MOVE_DELAY, lambda: self.execute_ai_move(move))
    def execute_ai_move(self, move):
        if self.board.is_game_over():
            self.handle_game_end()
            return
        self.board.push(move)
        self.last_move = (move.from_square, move.to_square)
        self.draw_board()
        winsound.Beep(800, 100)
    # ================= GAME END =================
    def handle_game_end(self, forced=None):
        result = None
        winsound.Beep(800, 100)
        if forced == "win":
            result = 1
            msg = "You won!"
        elif forced == "loss":
            result = 0
            msg = "You lost."
        elif self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                result = 0
                msg = "Checkmate! You lost."
            else:
                result = 1
                msg = "Checkmate! You won!"
        elif self.board.is_stalemate() or \
            self.board.is_insufficient_material() or \
            self.board.can_claim_threefold_repetition() or \
            self.board.can_claim_fifty_moves():
            result = 0.5
            msg = "Draw!"
        else:
            return
        self.update_elo(result)
        messagebox.showinfo("Game Over", f"{msg}\nNew Elo: {self.player_elo}")
        self.draw_menu()
    def update_elo(self, score):
        expected = 1 / (1 + 10 ** ((self.ai_elo - self.player_elo) / 400))
        self.player_elo += int(K_FACTOR * (score - expected))
    # ================= UTIL =================
    def is_promotion(self, move):
        piece = self.board.piece_at(move.from_square)
        return piece and piece.piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]
    def load_images(self):
        for k, f in IMAGE_FILES.items():
            img_path = resource_path(os.path.join("images", f))
            img = Image.open(img_path).resize((70, 70))
            self.images[k] = ImageTk.PhotoImage(img)
# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()
