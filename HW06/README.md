# Rock-Paper-Scissors Secure Protocol

A cryptographically secure implementation of Rock-Paper-Scissors (Roshambo) using a commit-reveal protocol to prevent cheating.

## 🎯 Project Overview

This project implements a distributed Rock-Paper-Scissors game where Alice (client) and Bob (server) play remotely over a network. The protocol uses cryptographic commitments to ensure neither player can cheat.

## 🔐 Security Features

- **Commitment Scheme**: SHA-256 hash-based commitment prevents both players from cheating
- **Binding Property**: Alice cannot change her move after committing
- **Hiding Property**: Bob cannot determine Alice's move from the commitment
- **Nonce-based Security**: Random nonces prevent dictionary attacks

## 🏗️ Architecture

```
HW06/
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

### Option 1: Using Make (Recommended)

```bash
# Build Docker images
make build

# Run the game
make test

# View logs
make logs
```

### Option 2: Using Docker Compose Directly

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🎮 How It Works

### Protocol Flow

1. **Phase 1 - Commit**
   - Alice chooses her move (rock/paper/scissors)
   - Alice generates a random nonce
   - Alice computes: `commitment = SHA256(move || nonce)`
   - Alice sends commitment to Bob

2. **Phase 2 - Bob's Move**
   - Bob receives commitment (cannot determine Alice's move)
   - Bob chooses his move
   - Bob sends his move to Alice

3. **Phase 3 - Reveal**
   - Alice reveals her original move and nonce
   - Alice sends `(move, nonce)` to Bob

4. **Phase 4 - Verification**
   - Bob verifies: `SHA256(move || nonce) == commitment`
   - If verification fails, Alice cheated!
   - If verification succeeds, determine winner

### Why This Prevents Cheating

- **Alice cannot cheat**: Once she sends the commitment, she's cryptographically bound to that move. Changing it would fail verification.
- **Bob cannot cheat**: The commitment is a hash that doesn't reveal the move, so he must choose without knowing Alice's move.

## 🛠️ Configuration

Environment variables in `docker-compose.yml`:

```yaml
BOB_HOST: Server bind address (default: 0.0.0.0)
BOB_PORT: Server port (default: 5555)
NUM_GAMES: Number of games to play (default: 3)
STARTUP_DELAY: Delay before Alice connects (default: 3 seconds)
```

## 📊 Example Output

```
🎲 Alice's Rock-Paper-Scissors Client
============================================================
👩 Alice chose: ROCK
✅ Generated commitment: a3f5b2c8e7d1f4a9...
✅ Sent commitment to Bob

📥 Phase 2: Waiting for Bob's move...
✅ Bob played: SCISSORS
   (Bob chose without knowing Alice's move!)

📤 Phase 3: Revealing move and nonce...
✅ Revealed: ROCK

📊 GAME RESULT
============================================================
Alice played: ROCK
Bob played:   SCISSORS

ALICE WINS! rock beats scissors
============================================================
```

## 🧪 Testing

The implementation includes several test scenarios:

```bash
# Run standard test (3 games)
make test

# View specific logs
make logs-alice
make logs-bob

# Check container status
make status
```

## 🔒 Security Analysis

### Commitment Scheme Properties

- **Hiding**: `P(Bob determines move | commitment) ≈ 1/3` (brute force only)
- **Binding**: `P(Alice changes move | commitment sent) = 0` (computationally infeasible to find collision)

### Attack Resistance

1. **Alice tries to cheat by changing move**: ❌ Commitment verification fails
2. **Bob tries to see Alice's move early**: ❌ SHA-256 is one-way function
3. **Man-in-the-middle**: ❌ Would require breaking SHA-256
4. **Replay attacks**: ❌ Each game uses fresh random nonce

## 📚 References

- NIST FIPS 180-4: Secure Hash Standard (SHA-256)
- Commitment Schemes in Cryptography (Goldreich, 2001)
- Docker Documentation: https://docs.docker.com

## 👨‍💻 Author

Nicolas Leone - 1986354
Cybersecurity - Homework 06

## 📄 License

Educational use only - Cybersecurity Course Assignment
