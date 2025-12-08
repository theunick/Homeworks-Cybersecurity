# Dice Game Secure Protocol

A cryptographically secure implementation of a dice game using a commit-reveal protocol to prevent cheating.

## 🎯 Project Overview

This project implements a distributed dice game where Alice (client) and Bob (server) play remotely over a network. Players roll k six-sided dice, sum the results, and compare. The protocol uses cryptographic commitments to ensure neither player can cheat.

## 🔐 Security Features

- **Commitment Scheme**: SHA-256 hash-based commitment prevents both players from cheating
- **Binding Property**: Alice cannot change her dice sum after committing
- **Hiding Property**: Bob cannot determine Alice's sum from the commitment
- **Nonce-based Security**: Random nonces prevent dictionary attacks
- **Match System**: Multiple games in a match with final score tracking

## 🏗️ Architecture

```
HW07/
├── alice/
│   ├── Dockerfile         # Alice's container configuration
│   └── alice.py          # Client implementation
├── bob/
│   ├── Dockerfile         # Bob's container configuration
│   └── bob.py            # Server implementation
├── shared/
│   └── protocol.py       # Shared protocol and crypto logic
├── docker-compose.yml    # Orchestration configuration
├── Makefile             # Build and run commands
└── README.md            # This file
```

## 📋 Requirements

- Docker Desktop (installed and running)
- Python 3.11+ (for local testing, not required for Docker)

## 🚀 Quick Start

### Using Make (Recommended)

```bash
# Build Docker images
make build

# Run the game (5 games match with 3 dice)
make test

# View logs
make logs

# Cleanup
make clean-docker
```

### Using Docker Compose Directly

```bash
# Build and run
docker-compose up --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🎮 How It Works

### Protocol Flow

1. **Phase 1 - Commit**
   - Alice rolls k dice and computes sum
   - Alice generates a random nonce
   - Alice computes: `commitment = SHA256(sum || nonce)`
   - Alice sends commitment to Bob

2. **Phase 2 - Bob's Roll**
   - Bob receives commitment (cannot determine Alice's sum)
   - Bob rolls k dice and computes sum
   - Bob sends his sum and dice to Alice

3. **Phase 3 - Reveal**
   - Alice reveals her original sum, dice, and nonce
   - Alice sends `(sum, dice, nonce)` to Bob

4. **Phase 4 - Verification**
   - Bob verifies: `SHA256(sum || nonce) == commitment`
   - Bob verifies: `sum(dice) == sum`
   - If verification fails, Alice cheated!
   - If verification succeeds, determine winner

5. **Match Completion**
   - Repeat for configured number of games
   - Track wins/losses/ties
   - Determine match winner

### Why This Prevents Cheating

- **Alice cannot cheat**: Once she sends the commitment, she's cryptographically bound to that sum. Changing it would fail verification.
- **Bob cannot cheat**: The commitment is a hash that doesn't reveal the sum, so he must roll without knowing Alice's result.

## 🛠️ Configuration

Environment variables in `docker-compose.yml`:

- `NUM_DICE`: Number of dice per player (default: 3)
- `NUM_GAMES`: Number of games in match (default: 5)
- `BOB_PORT`: Server port (default: 5555)
- `STARTUP_DELAY`: Delay before Alice connects (default: 3s)

## 📊 Example Output

```
🎲 Game 1
============================================================
Alice rolled: [4, 6, 2]
Alice's sum: 12
Bob rolled: [3, 5, 1]
Bob's sum: 9

GAME 1 RESULT
============================================================
Alice: [4, 6, 2] = 12
Bob:   [3, 5, 1] = 9

ALICE WINS! 12 beats 9
============================================================
```

## 🔒 Security Analysis

### Commitment Scheme Properties

- **Hiding**: SHA-256 preimage resistance + 256-bit nonce
- **Binding**: SHA-256 collision resistance
- **Computational Security**: ~2^128 operations to break

### Attack Prevention

1. **Alice changing sum**: Requires SHA-256 collision (infeasible)
2. **Bob determining sum**: Requires inverting SHA-256 + guessing nonce (infeasible)
3. **Replay attacks**: Fresh nonce per game (probability 2^-256)

## 🐳 Docker Deployment

Two isolated containers simulate two virtual machines:

- **alice**: Client container, initiates games
- **bob**: Server container, listens on port 5555
- **dice_network**: Bridge network for TCP/IP communication

## 📚 References

- NIST FIPS 180-4: Secure Hash Standard (SHA-256)
- Docker Documentation: https://docs.docker.com
- Python secrets module: https://docs.python.org/3/library/secrets.html
