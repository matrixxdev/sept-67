# ⬡ SEPT — The SEPTEM-67 Programming Language

```
███████╗███████╗██████╗ ████████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝
███████╗█████╗  ██████╔╝   ██║
╚════██║██╔══╝  ██╔═══╝    ██║
███████║███████╗██║        ██║
╚══════╝╚══════╝╚═╝        ╚═╝
```

> **SEPT** is a fully working scripting language built around the **SEPTEM-67 number system** (base 67). Every number can be expressed in classic decimal *or* as a compact base-67 literal. The language uses Unicode symbols for keywords, making it look like it fell out of a alien spaceship.

---

## 🚀 Quick Start

```bash
git clone https://github.com/matrixxdev/sept-67
cd sept-67
python3 src/sept.py examples/01_hello.sept
```

> **Requirements:** Python 3.8+ — no dependencies, no install needed.
> When you've cloned it, unzip the Zip Folder and drag & drop the Files into the sept-67 Folder, and delete the Zip Folder.

---

## 🌌 What is SEPTEM-67?

SEPTEM-67 is a positional numeral system with **base 67** using these 67 symbols:

| Range     | Symbols          | Values |
|-----------|------------------|--------|
| Digits    | `0–9`            | 0–9    |
| Uppercase | `A–Z`            | 10–35  |
| Lowercase | `a–z`            | 36–61  |
| Galactic  | `Ω · Δ Φ Σ`      | 62–66  |

```
Decimal  →  SEPTEM-67
10       →  A
67       →  10
255      →  3E
1337     →  JΔ
1000000  →  4Δ7
```

With just **4 digits**, SEPT-67 can represent over **20 million** values.  
Binary would need **25 digits** for the same.

---

## 📖 Language Reference

### Variables

```sept
ΔΩ name := value       ΩΩΩ declare variable
name := new_value      ΩΩΩ reassign variable
```

### Number Literals

```sept
ΔΩ a := 42             ΩΩΩ decimal literal
ΔΩ b := §A             ΩΩΩ S67 literal → 10
ΔΩ c := §JΔ            ΩΩΩ S67 literal → 1337
ΔΩ d := §10            ΩΩΩ S67 literal → 67
```

### Output

```sept
Φ expression           ΩΩΩ print (decimal / string)
ΦΔ expression          ΩΩΩ print as SEPTEM-67
```

### Types

| Type    | Example          | Notes                  |
|---------|-----------------|------------------------|
| Number  | `42`, `§1A`     | floats & S67 literals  |
| String  | `"hello"`       | double-quoted           |
| Bool    | `Ω·Δ` / `Ω·Φ` | true / false           |
| Null    | `Ω·Σ`           | null / none            |
| List    | `[1, 2, 3]`     | zero-indexed           |

### Operators

```sept
ΩΩΩ Arithmetic
x + y   x - y   x * y   x / y   x % y   x ^ y

ΩΩΩ Comparison
x == y   x != y   x < y   x > y   x <= y   x >= y

ΩΩΩ Logic
x ΩΔ y    ΩΩΩ and
x ΩΦ y    ΩΩΩ or
ΩΣ x      ΩΩΩ not
```

### If / Else

```sept
Δif x > 10 {
    Φ "big"
} Δelse Δif x > 5 {
    Φ "medium"
} Δelse {
    Φ "small"
}
```

### Loops

```sept
ΩΩΩ Loop N times (with index variable i)
Ω67 10 ΣΦ i {
    ΦΔ i
}

ΩΩΩ Loop over list / range
Ω67 range(5) ΣΦ i {
    Φ i
}

ΩΩΩ While loop
ΩΔΩ x < 100 {
    x := x * 2
}
```

### Functions

```sept
ΣΩ add(a, b) {
    ΣΣ a + b
}

Φ add(§A, §B)    ΩΩΩ prints 21 (10 + 11)
```

### Comments

```sept
ΩΩΩ This is a comment — everything after ΩΩΩ on a line is ignored
```

### Break

```sept
Ω67 100 ΣΦ i {
    Δif i == 10 { ΣΔ }    ΩΩΩ break out of loop
    Φ i
}
```

---

## 🔧 Built-in Functions

| Function       | Description                         |
|----------------|-------------------------------------|
| `s67(n)`       | Convert number → SEPTEM-67 string   |
| `dec(s)`       | Convert S67 string → decimal        |
| `len(x)`       | Length of string or list            |
| `str(x)`       | Convert anything to string          |
| `num(x)`       | Convert to number                   |
| `sqrt(n)`      | Square root                         |
| `abs(n)`       | Absolute value                      |
| `floor(n)`     | Round down                          |
| `ceil(n)`      | Round up                            |
| `pow(a, b)`    | a to the power of b                 |
| `max(a, b, …)` | Maximum value                       |
| `min(a, b, …)` | Minimum value                       |
| `range(n)`     | List `[0, 1, …, n-1]`              |
| `range(a, b)`  | List `[a, a+1, …, b-1]`           |
| `append(l, x)` | Append to list                      |
| `input(prompt)`| Read user input                     |
| `type(x)`      | Type name as string                 |

---

## 📁 Examples

| File                         | What it shows                         |
|------------------------------|---------------------------------------|
| `examples/01_hello.sept`     | Hello World + first S67 variables     |
| `examples/02_math.sept`      | Arithmetic & S67 literals             |
| `examples/03_control.sept`   | if/else, loops, while                 |
| `examples/04_functions.sept` | Functions, recursion, prime check     |
| `examples/05_lists.sept`     | Lists, range, string ops              |
| `examples/06_showcase.sept`  | 🌌 Full showcase demo                |

Run any example:
```bash
python3 src/sept.py examples/06_showcase.sept
```

---

## 🖥️ REPL

```bash
python3 src/sept.py
```

```
⬡ sept> ΔΩ x := §Ω
⬡ sept> ΦΔ x * x
```

Type `.help` for reference, `.symbols` for the full S67 table, `exit` to quit.

---

## 🧪 Tests

```bash
python3 tests/test_sept.py
```

---

## ⬡ Keyword Reference Card

| Keyword | Meaning           |
|---------|-------------------|
| `ΔΩ`    | `let` (declare)   |
| `Φ`     | `print`           |
| `ΦΔ`    | `print` as S67    |
| `Δif`   | `if`              |
| `Δelse` | `else`            |
| `Ω67`   | `for` / loop      |
| `ΩΔΩ`   | `while`           |
| `ΣΩ`    | `func` (define)   |
| `ΣΣ`    | `return`          |
| `ΣΔ`    | `break`           |
| `ΣΦ`    | `in` (loop var)   |
| `ΩΔ`    | `and`             |
| `ΩΦ`    | `or`              |
| `ΩΣ`    | `not`             |
| `Ω·Δ`   | `true`            |
| `Ω·Φ`   | `false`           |
| `Ω·Σ`   | `null`            |
| `ΩΩΩ`   | comment           |
| `§`     | S67 literal prefix|

---

## 📜 License

MIT — do whatever you want, just keep it galactic.

---

*Built with Python 3. No dependencies. Pure math. Base 67. Forever.*
