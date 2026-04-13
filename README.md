
# Project: Stratego LLM Test Based Games

## 1. Introduction

Stratego LLM is a research framework designed to evaluate the strategic reasoning and behavioral characteristics of Large Language Models (LLMs) in an imperfect-information game setting.

Unlike static benchmarks, this project pits models (e.g., Mistral, Gemma, Llama, Qwen) against each other in the board game Stratego to analyze dynamic performance. The primary goal is to determine which model performs better by measuring:

Win Rates & Dominance: Quantitative analysis of Win/Loss/Draw ratios across 100+ match simulations.

Behavioral Profiling: Classifying models as Stable (consistent, rule-abiding) vs. Aggressive (high attack frequency, risky plays).

Efficiency: Measuring time-to-move and token consumption to determine the "cost of intelligence."

Strategic Consistency: Analyzing how often models hallucinate invalid moves versus making logically sound decisions.

The system includes an automated arena for batch matchmaking, a custom logger for dataset creation, and a prompt-optimizer that refines strategies based on match outcomes.

## 2. Project Initialization (Local Setup)

Follow these steps to set up the development environment on your local machine.

### Prerequisites

* **Git**: Ensure Git is installed.
* **Python**: Python 3.8+ is recommended.

### Installation Steps

1. **Clone the Repository**
Clone the project to your local machine (e.g., in VS Code).
```bash
git clone https://github.com/davszi/Stratego.git
cd Stratego

```


2. **Create and Activate Virtual Environment**
It is highly recommended to work within a virtual environment.
* **Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```


* **Windows (CMD)**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat

```


* **macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate

```




> **Note:** If successful, you will see `(.venv)` at the start of your terminal line. To exit later, simply type `deactivate`.


3. **Install Dependencies**
Update pip and install the package in editable mode.
```bash
python -m pip install --upgrade pip
pip install -e .

```


*To install additional dependencies for Hugging Face models:*
```bash
pip install -e ".[hf]"

```


4. **Verify Installation**
Use the following commands to install environment files for Stratego Duel and Custom into the `textarena` folder.
```bash
stratego-install-env

```






### Setting up Ollama:

1. Install Ollama: 
For macOS & Linux: `curl -fsSL https://ollama.com/install.sh | sh`
For Windows (Powershell): `irm https://ollama.com/install.ps1 | iex` 
2. Start Ollama: `ollama serve`


### Managing Models

* **Check available models:**
```bash
`ollama list`

```


* **Pull (Download) a new model:**
```bash
`ollama pull mistral:7b'

```



---

## 5. Usage & Gameplay

You can run the game using the `stratego` command. Ensure your Ollama client is running if using local LLMs.

**Basic Command:**

```bash
stratego --p0 ollama:mistral:7b --p1 ollama:gemma3:1b --prompt base

```

**Arguments:**

* `--p0`: Agent for Player 0 (e.g., `ollama:mistral:7b` or `hf:TinyLlama/TinyLlama-1.1B-Chat-v1.0`).
* `--p1`: Agent for Player 1.
* `--prompt`: The prompt strategy to use.
* `--size`: Board size (NxN). Default is 10.
```bash
# Example for a smaller board
stratego --p0 ollama:mistral:7b --p1 ollama:mistral:7b --size 6

```



---

## 6. Dataset & Prompt Optimization

The system includes automated logging and prompt improvement mechanisms implemented in `main.py`.

### Logging (GameLogger)

Every move, prompt, and metadata is saved to CSV logs. The `cli()` function initializes a `GameLogger`:

* **Log Directory:** Controlled via `--log-dir` (default: `logs`).
* **Initial Prompt Logging:** The logger captures the exact initial prompt used by the agent to ensure reproducibility.

### Automated Prompt Improvement

The system automatically attempts to improve the System Prompt based on gameplay data.

* **Mechanism:** The runner checks the number of CSV logs in the log directory.
* **Trigger:** Every **3 games**, `improve_prompt()` is called.
* **Logic:** It analyzes recent games and updates `stratego/prompts/current_prompt.txt`.

### Hugging Face Dataset Integration

To upload your game logs to Hugging Face:

1. **Install Libraries:**
```bash
pip install huggingface huggingface_hub datasets

```


2. **Configuration:**
* Join your HF Organization.
* Update `./datasets/uploader.py` with your repository name.


3. **Authentication:**
* Create a **WRITE** token in your Hugging Face settings.
* Run `hf auth login` in your terminal and paste the token (do not save as git credential).


4. **Upload:**
Once authenticated, use the uploader script to push logs to the dataset repository.

---

## 7. Benchmarking

Use the built-in benchmark tool to evaluate model performance over multiple games.

**Command:**

```bash
benchmark --p0 {model_A} --p1 {model_B} --size {N} --game {count}

```

**Example:**

```bash
benchmark --p0 llama3.2:1b --p1 gemma3:1b --size 6 --game 4

```

## 8. GUI
After installing the package, you can use command `gui` to run the game in graphic user interface.

## 9. Scoring
Since we played different number of games for each model, we needed another method to finalize the score.
We made score equation based on following factors: win/draw rate, number of games that reached turn limit, number of total played games, win rate as playing as Player 1, and number of losses with invalid moves.
* Score based on the win/draw rate of various game board.
$$S^{size}_m = \frac{\sum_{s\in{\{4,5,6\}}}w_s(W_{m,s}+0.5D_{m,s})}{\sum_{s\in{\{4,5,6\}}}w_sN_{m,s}}$$
  $m$ is model, $o$ is opponent, $w_s$ is the weight for each board size, $N_{m,s}$ is total number of the game that the model $m$ played for $s$ board size, $W_{m,s}$ as number of wins of the model $m$ with $s$ board size, and $D_{m,s}$ as number of draws fo teh model $m$ with $s$ board size.
* Score based on the total number of games that reached turn limit.
$$S^{speed}_m = 1-\frac{EndedByTernLimit_m}{N_m}$$
$N_m$ is total number of games played by the model $m$.
* Reduction point based on the number of gamed lost by invalid moves.
$$R^{inv}_m = \frac{LostByInvalid_m}{N_m}$$
For the bonus point for playing as Player 1, compute win rate as player1 against an opponent.
$$p1(m \rarr o)=\frac{W^{P1}_{m,o}+0.5D_{m,o}}{G_{m,o}}$$
$G_{m,o}$ as total game played between the model $m$ as Player 1 and opponent $o$ as Player 2.
  * Now, compute opponent's Player 1 win rate from the set.
$$p1(o \rarr m)=\frac{W^{P1}_{o,m}+0.5D_{o,m}}{G_{o,m}}$$
$G_{o,m}$ as total game played between the opponent $o$ as Player 1 and model $m$ as Player 2.
  * Next, compute the win rate of the model $m$ as it playing as Player 2 against same opponent $o$, means $o$ plays Player1.
$$p2(m \larr o)=\frac{W^{P2}_{o,m}+0.5D_{o,m}}{G_{o,m}}$$
  * Compute the difference between the Player 1 win rate between model $m$ and opponent $o$.
$$edge_1(m,o) = p1(m\rarr o)-p1(o\rarr m)$$
  * Next, compare the winrate from $p1$ between $p2$ of the model $m$.
$$edge_2(m,o) = p1(m\rarr o)-p2(m\larr o)$$
$edge_2(m,o)$ is usually negative, since the models have higher win rate, when they play as Player2. They play biased.
  * Now compute the total bonus from the match.
$$bonus_{pair}(m,o) = max(0,edge_1(m,o))+max(0,edge_2(m,o))$$
  * Adjust standard for giving weight. Set standard as less number of games to being pair.
$$w_{m,o}=min(G_{m,o},G_{o,m})$$
  * Then compute raw bonus point by repeating those steps above with all opponents.
$$B^{raw}_m = \frac{\sum_o w_{m,o}bonus_{pair}(m,o)}{\sum_o w_{m,o}}$$
  * Find the total bonus.
Clamp it between 0 to 1, means the minimum is 0 and maximum is 1 for the final bonus.
$$B_m=clip(\frac{B^{raw}_{m}}{0.2},0,1)$$
For here, set the limit dividing with 0.2.
* Computed Reliability Coefficient using Buehlmann $k$. $k$ is set to 300 here, to make $C_m$ for only 100 games played models to 0.5, means half reliable.
$$C_m=\sqrt{\frac{N_m}{N_m+k}}$$
* For computing final score, we set the weights as following:\
$a=0.60$ reward as played bord size\
$b=0.15$ reward for ending game in turn limit\
$c=0.25$ deduction for playing invalid\
$d=0.20$ reward for winning as player 1\
$w_4=0.75$ weight for 4 x 4 board\
$w_5=1.00$ weight for 5 x 5 board\
$w_6=1.35$ weight for 6 x 6 board\
Credibility $k = 300$
* Combining all scores and reductions, here is the score equation for our final score of each model:
### $$Score_m=100\cdot C_m\cdot (aS^{size}_m+bS^{speed}_m-cR^{inv}_m+dB_m)$$