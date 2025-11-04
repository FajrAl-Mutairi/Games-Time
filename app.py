from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "game_secret_key"


# 🏠 الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("home.html")


# 🎯 لعبة Guess the Number
@app.route("/guessnumber", methods=["GET", "POST"])
def guessnumber():
    if "secret_number" not in session:
        session.clear()  # 🧼 امسحي الجلسة القديمة أول
        session["secret_number"] = random.randint(1, 100)
        session["attempts"] = 0
        session["message"] = "I'm thinking of a number between 1 and 100 "
        session["game_over"] = False

    secret_number = session["secret_number"]
    message = session.get("message", "")
    game_over = session.get("game_over", False)

    if request.method == "POST" and not game_over:
        try:
            guess = int(request.form["guess"])
            session["attempts"] += 1

            if guess < secret_number:
                message = "Too low! Try again ⬇"
            elif guess > secret_number:
                message = "Too high! Try again ⬆"
            else:
                message = f" Correct! The number was {secret_number}. You guessed it in {session['attempts']} attempts."
                session["game_over"] = True

            session["message"] = message

        except ValueError:
            session["message"] = "Please enter a valid number."

    return render_template(
        "guessnumber.html",
        message=session.get("message", ""),
        game_over=session.get("game_over", False)
    )

# مسار لإعادة تهيئة لعبة Guess the Number
@app.route("/guessnumber/reset")
def reset_guessnumber():
    session["secret_number"] = random.randint(1, 100)
    session["attempts"] = 0
    session["message"] = "I'm thinking of a number between 1 and 100 🎯"
    session["game_over"] = False
    return redirect(url_for("guessnumber"))


#  لعبة Tic Tac Toe
def check_winner(board, player):
    win_conditions = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for condition in win_conditions:
        if all(board[i] == player for i in condition):
            return True
    return False

@app.route("/tictactoe", methods=["GET", "POST"])
def tictactoe_index():
    if request.method == "POST":
        session["player1"] = request.form["player1"]
        session["player2"] = request.form["player2"]
        session["board"] = [" " for _ in range(9)]
        session["current_player"] = "player1"
        session["scores"] = {"player1": 0, "player2": 0}
        return redirect(url_for("tictactoe_game"))
    return render_template("index.html")  

@app.route("/game")
def tictactoe_game():
    return render_template(
        "game.html",
        board=session.get("board", [" " for _ in range(9)]),
        current=session.get("current_player", "player1"),
        player1=session.get("player1", "Player 1"),
        player2=session.get("player2", "Player 2"),
        scores=session.get("scores", {"player1": 0, "player2": 0}),
        winner=None,
        draw=False
    )

@app.route("/move/<int:pos>")
def move(pos):
    board = session["board"]
    current = session["current_player"]
    symbol = "X" if current == "player1" else "O"
    
    winner = None
    if board[pos] == " ":
        board[pos] = symbol
        if check_winner(board, symbol):
            session["scores"][current] += 1
            winner = current
            session["board"] = [" " for _ in range(9)]
            session["current_player"] = "player1"
            return render_template(
                "game.html",
                board=session["board"],
                current="player1",
                player1=session["player1"],
                player2=session["player2"],
                scores=session["scores"],
                winner=winner,
                draw=False
            )
        elif " " not in board:
            session["board"] = [" " for _ in range(9)]
            session["current_player"] = "player1"
            return render_template(
                "game.html",
                board=session["board"],
                current="player1",
                player1=session["player1"],
                player2=session["player2"],
                scores=session["scores"],
                winner=None,
                draw=True
            )
    
    session["current_player"] = "player2" if current == "player1" else "player1"
    session["board"] = board
    return redirect(url_for("tictactoe_game"))

@app.route("/reset")
def reset():
    session["board"] = [" " for _ in range(9)]
    session["current_player"] = "player1"
    return redirect(url_for("tictactoe_game"))

@app.route("/change_players")
def change_players():
    session.pop("player1", None)
    session.pop("player2", None)
    session["board"] = [" " for _ in range(9)]
    session["current_player"] = "player1"
    return redirect(url_for("tictactoe_index"))

# تشغيل السيرفر
if __name__ == "__main__":
    app.run(debug=True)
