#!/usr/bin/env python3
"""
Bob's Server - Rock-Paper-Scissors Game
Implements the server side of the commit-reveal protocol.

Protocol Flow (Bob's perspective):
1. Listen for Alice's connection
2. Receive Alice's commitment (hash)
3. Choose Bob's move and send it to Alice
4. Receive Alice's reveal (move + nonce)
5. Verify commitment and determine winner
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


class BobServer:
    """Bob's server implementation."""
    
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.commitment_scheme = CommitmentScheme()
        self.game_logic = GameLogic()
    
    def choose_move(self):
        """Bob randomly chooses a move."""
        move = random.choice(list(VALID_MOVES))
        print(f"🤖 Bob chose: {move.upper()}")
        return move
    
    def handle_game(self, conn, addr):
        """
        Handle a single game session with Alice.
        
        Args:
            conn: Socket connection
            addr: Client address
        """
        print(f"\n{'='*60}")
        print(f"🎮 New game started with {addr}")
        print(f"{'='*60}\n")
        
        try:
            # Phase 1: Receive Alice's commitment
            print("📥 Phase 1: Waiting for Alice's commitment...")
            msg = receive_message(conn)
            
            if msg['type'] != MSG_COMMIT:
                send_message(conn, MSG_ERROR, message="Expected COMMIT message")
                return
            
            alice_commitment = msg['data']['commitment']
            print(f"✅ Received commitment: {alice_commitment[:16]}...")
            print(f"   (Bob cannot determine Alice's move from this hash)")
            
            # Phase 2: Bob chooses his move and sends it
            print(f"\n📤 Phase 2: Bob choosing move...")
            time.sleep(0.5)  # Simulate thinking time
            bob_move = self.choose_move()
            
            send_message(conn, MSG_MOVE, move=bob_move)
            print(f"✅ Sent move to Alice: {bob_move.upper()}")
            
            # Phase 3: Receive Alice's reveal
            print(f"\n📥 Phase 3: Waiting for Alice's reveal...")
            msg = receive_message(conn)
            
            if msg['type'] != MSG_REVEAL:
                send_message(conn, MSG_ERROR, message="Expected REVEAL message")
                return
            
            alice_move = msg['data']['move']
            alice_nonce = msg['data']['nonce']
            
            print(f"✅ Alice revealed: {alice_move.upper()}")
            print(f"   Nonce: {alice_nonce[:16]}...")
            
            # Phase 4: Verify commitment
            print(f"\n🔍 Phase 4: Verifying Alice's commitment...")
            
            if not self.game_logic.is_valid_move(alice_move):
                send_message(conn, MSG_ERROR, message=f"Invalid move: {alice_move}")
                print(f"❌ Invalid move from Alice: {alice_move}")
                return
            
            is_valid = self.commitment_scheme.verify(
                alice_commitment, alice_move, alice_nonce
            )
            
            if not is_valid:
                send_message(conn, MSG_ERROR, message="Commitment verification failed! Cheating detected!")
                print(f"❌ CHEATING DETECTED! Commitment doesn't match revealed values!")
                print(f"   Expected commitment: {alice_commitment}")
                print(f"   Computed commitment: {self.commitment_scheme.commit(alice_move, alice_nonce)}")
                return
            
            print(f"✅ Commitment verified! Alice didn't cheat.")
            
            # Phase 5: Determine winner
            print(f"\n🏆 Determining winner...")
            winner = self.game_logic.determine_winner(alice_move, bob_move)
            result_msg = self.game_logic.get_result_message(winner, alice_move, bob_move)
            
            # Send result to Alice
            send_message(conn, MSG_RESULT, 
                        winner=winner,
                        alice_move=alice_move,
                        bob_move=bob_move,
                        message=result_msg)
            
            print(f"\n{'='*60}")
            print(f"📊 GAME RESULT")
            print(f"{'='*60}")
            print(f"Alice played: {alice_move.upper()}")
            print(f"Bob played:   {bob_move.upper()}")
            print(f"\n{result_msg}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error during game: {e}")
            try:
                send_message(conn, MSG_ERROR, message=str(e))
            except:
                pass
    
    def run(self):
        """Start the server and listen for connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            
            print(f"\n{'='*60}")
            print(f"🎲 Bob's Rock-Paper-Scissors Server")
            print(f"{'='*60}")
            print(f"📡 Listening on {self.host}:{self.port}")
            print(f"⏳ Waiting for Alice to connect...")
            print(f"{'='*60}\n")
            
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    self.handle_game(conn, addr)
                
                # Ask if we want to play again (in Docker, we'll just exit after one game)
                print(f"\n⏳ Ready for another game...\n")
                time.sleep(2)


def main():
    """Main entry point."""
    # Get configuration from environment variables (for Docker)
    host = os.environ.get('BOB_HOST', '0.0.0.0')
    port = int(os.environ.get('BOB_PORT', 5555))
    
    server = BobServer(host=host, port=port)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n\n👋 Server shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
