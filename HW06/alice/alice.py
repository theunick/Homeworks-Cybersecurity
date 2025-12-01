#!/usr/bin/env python3
"""
Alice's Client - Rock-Paper-Scissors Game
Implements the client side of the commit-reveal protocol.

Protocol Flow (Alice's perspective):
1. Connect to Bob's server
2. Choose move and create commitment (hash)
3. Send commitment to Bob
4. Receive Bob's move
5. Reveal move and nonce to Bob
6. Receive game result
"""

import socket
import sys
import os
import random
import time

# Add shared directory to path
sys.path.insert(0, '/app/shared')

from protocol import (
    CommitmentScheme, GameLogic, VALID_MOVES,
    MSG_COMMIT, MSG_MOVE, MSG_REVEAL, MSG_RESULT, MSG_ERROR,
    send_message, receive_message
)


class AliceClient:
    """Alice's client implementation."""
    
    def __init__(self, server_host='bob', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.commitment_scheme = CommitmentScheme()
        self.game_logic = GameLogic()
    
    def choose_move(self):
        """Alice randomly chooses a move."""
        move = random.choice(list(VALID_MOVES))
        print(f"👩 Alice chose: {move.upper()}")
        return move
    
    def play_game(self):
        """Play a single game with Bob."""
        print(f"\n{'='*60}")
        print(f"🎮 Connecting to Bob's server at {self.server_host}:{self.server_port}")
        print(f"{'='*60}\n")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                print(f"✅ Connected to Bob!\n")
                
                # Phase 1: Alice chooses and commits
                print("📤 Phase 1: Creating commitment...")
                alice_move = self.choose_move()
                alice_nonce = self.commitment_scheme.generate_nonce()
                alice_commitment = self.commitment_scheme.commit(alice_move, alice_nonce)
                
                print(f"✅ Generated commitment: {alice_commitment[:16]}...")
                print(f"   (This hides Alice's move: {alice_move.upper()})")
                
                send_message(sock, MSG_COMMIT, commitment=alice_commitment)
                print(f"✅ Sent commitment to Bob\n")
                
                # Phase 2: Receive Bob's move
                print("📥 Phase 2: Waiting for Bob's move...")
                msg = receive_message(sock)
                
                if msg['type'] == MSG_ERROR:
                    print(f"❌ Error from Bob: {msg['data']['message']}")
                    return
                
                if msg['type'] != MSG_MOVE:
                    print(f"❌ Unexpected message type: {msg['type']}")
                    return
                
                bob_move = msg['data']['move']
                print(f"✅ Bob played: {bob_move.upper()}")
                print(f"   (Bob chose without knowing Alice's move!)\n")
                
                # Phase 3: Alice reveals
                print("📤 Phase 3: Revealing move and nonce...")
                time.sleep(0.5)
                
                send_message(sock, MSG_REVEAL, move=alice_move, nonce=alice_nonce)
                print(f"✅ Revealed: {alice_move.upper()}")
                print(f"   Nonce: {alice_nonce[:16]}...\n")
                
                # Phase 4: Receive result
                print("📥 Phase 4: Waiting for result...")
                msg = receive_message(sock)
                
                if msg['type'] == MSG_ERROR:
                    print(f"❌ Error from Bob: {msg['data']['message']}")
                    return
                
                if msg['type'] != MSG_RESULT:
                    print(f"❌ Unexpected message type: {msg['type']}")
                    return
                
                # Display result
                winner = msg['data']['winner']
                result_msg = msg['data']['message']
                
                print(f"\n{'='*60}")
                print(f"📊 GAME RESULT")
                print(f"{'='*60}")
                print(f"Alice played: {alice_move.upper()}")
                print(f"Bob played:   {bob_move.upper()}")
                print(f"\n{result_msg}")
                print(f"{'='*60}\n")
                
        except ConnectionRefusedError:
            print(f"❌ Cannot connect to Bob at {self.server_host}:{self.server_port}")
            print(f"   Make sure Bob's server is running!")
        except Exception as e:
            print(f"❌ Error during game: {e}")
    
    def run(self, num_games=1):
        """
        Run multiple games.
        
        Args:
            num_games: Number of games to play
        """
        print(f"\n{'='*60}")
        print(f"🎲 Alice's Rock-Paper-Scissors Client")
        print(f"{'='*60}")
        print(f"🎯 Will play {num_games} game(s) with Bob")
        print(f"{'='*60}\n")
        
        for game_num in range(1, num_games + 1):
            if num_games > 1:
                print(f"\n{'🎮'*20}")
                print(f"Game {game_num}/{num_games}")
                print(f"{'🎮'*20}\n")
            
            self.play_game()
            
            if game_num < num_games:
                print(f"\n⏳ Waiting 3 seconds before next game...\n")
                time.sleep(3)
        
        print(f"\n👋 All games completed!\n")


def main():
    """Main entry point."""
    # Get configuration from environment variables (for Docker)
    server_host = os.environ.get('BOB_HOST', 'bob')
    server_port = int(os.environ.get('BOB_PORT', 5555))
    num_games = int(os.environ.get('NUM_GAMES', 3))
    
    # Add delay to ensure Bob's server is ready
    startup_delay = int(os.environ.get('STARTUP_DELAY', 2))
    if startup_delay > 0:
        print(f"⏳ Waiting {startup_delay} seconds for Bob's server to start...")
        time.sleep(startup_delay)
    
    client = AliceClient(server_host=server_host, server_port=server_port)
    
    try:
        client.run(num_games=num_games)
    except KeyboardInterrupt:
        print("\n\n👋 Client shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
