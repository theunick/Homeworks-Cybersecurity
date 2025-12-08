#!/usr/bin/env python3
"""
Bob's Server - Dice Game
Implements the server side of the commit-reveal protocol for dice games.

Protocol Flow (Bob's perspective):
1. Listen for Alice's connection
2. Receive Alice's commitment (hash of sum)
3. Roll k dice and send sum to Alice
4. Receive Alice's reveal (sum + nonce)
5. Verify commitment and determine winner
6. Repeat for match length
7. Send match result
"""

import socket
import sys
import os
import time

# Add shared directory to path
sys.path.insert(0, '/app/shared')

from protocol import (
    CommitmentScheme, DiceLogic,
    MSG_COMMIT, MSG_RESULT, MSG_REVEAL, MSG_MATCH_RESULT, MSG_ERROR,
    send_message, receive_message
)


class BobServer:
    """Bob's server implementation."""
    
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.commitment_scheme = CommitmentScheme()
        self.dice_logic = DiceLogic()
    
    def handle_game(self, conn, addr, game_num):
        """
        Handle a single game session with Alice.
        
        Args:
            conn: Socket connection
            addr: Client address
            game_num: Game number in match
            
        Returns:
            Tuple (alice_sum, bob_sum, winner) or None on error
        """
        print(f"\n{'='*60}")
        print(f"🎮 Game {game_num} with {addr}")
        print(f"{'='*60}\n")
        
        try:
            # Phase 1: Receive Alice's commitment
            print("📥 Phase 1: Waiting for Alice's commitment...")
            msg = receive_message(conn)
            
            if msg['type'] != MSG_COMMIT:
                send_message(conn, MSG_ERROR, message="Expected COMMIT message")
                return None
            
            alice_commitment = msg['data']['commitment']
            num_dice = msg['data']['num_dice']
            
            print(f"✅ Received commitment: {alice_commitment[:16]}...")
            print(f"   Number of dice: {num_dice}")
            print(f"   (Bob cannot determine Alice's sum from this hash)")
            
            # Phase 2: Bob rolls dice and sends result
            print(f"\n📤 Phase 2: Bob rolling {num_dice} dice...")
            time.sleep(0.3)  # Simulate thinking time
            
            bob_dice = self.dice_logic.roll_dice(num_dice)
            bob_sum = self.dice_logic.calculate_sum(bob_dice)
            
            print(f"🎲 Bob rolled: {bob_dice}")
            print(f"📊 Bob's sum: {bob_sum}")
            
            send_message(conn, MSG_RESULT, 
                        bob_sum=bob_sum,
                        bob_dice=bob_dice)
            print(f"✅ Sent result to Alice: {bob_dice} = {bob_sum}")
            
            # Phase 3: Receive Alice's reveal
            print(f"\n📥 Phase 3: Waiting for Alice's reveal...")
            msg = receive_message(conn)
            
            if msg['type'] != MSG_REVEAL:
                send_message(conn, MSG_ERROR, message="Expected REVEAL message")
                return None
            
            alice_sum = msg['data']['alice_sum']
            alice_dice = msg['data']['alice_dice']
            alice_nonce = msg['data']['nonce']
            
            print(f"✅ Alice revealed: {alice_dice} = {alice_sum}")
            print(f"   Nonce: {alice_nonce[:16]}...")
            
            # Phase 4: Verify commitment
            print(f"\n🔍 Phase 4: Verifying Alice's commitment...")
            
            # Verify sum matches dice
            expected_sum = sum(alice_dice)
            if alice_sum != expected_sum:
                send_message(conn, MSG_ERROR, 
                           message=f"Invalid sum! Dice {alice_dice} != sum {alice_sum}")
                print(f"❌ Invalid sum from Alice!")
                return None
            
            # Verify commitment
            is_valid = self.commitment_scheme.verify(
                alice_commitment, str(alice_sum), alice_nonce
            )
            
            if not is_valid:
                send_message(conn, MSG_ERROR, 
                           message="Commitment verification failed! Cheating detected!")
                print(f"❌ CHEATING DETECTED! Commitment doesn't match!")
                print(f"   Expected: {alice_commitment}")
                print(f"   Computed: {self.commitment_scheme.commit(str(alice_sum), alice_nonce)}")
                return None
            
            print(f"✅ Commitment verified! Alice didn't cheat.")
            
            # Phase 5: Determine winner
            print(f"\n🏆 Determining winner...")
            winner = self.dice_logic.determine_winner(alice_sum, bob_sum)
            result_msg = self.dice_logic.get_result_message(winner, alice_sum, bob_sum)
            
            # Send result to Alice
            send_message(conn, MSG_MATCH_RESULT,
                        winner=winner,
                        alice_sum=alice_sum,
                        alice_dice=alice_dice,
                        bob_sum=bob_sum,
                        bob_dice=bob_dice,
                        message=result_msg)
            
            print(f"\n{'='*60}")
            print(f"📊 GAME {game_num} RESULT")
            print(f"{'='*60}")
            print(f"Alice: {alice_dice} = {alice_sum}")
            print(f"Bob:   {bob_dice} = {bob_sum}")
            print(f"\n{result_msg}")
            print(f"{'='*60}\n")
            
            return (alice_sum, bob_sum, winner)
            
        except Exception as e:
            print(f"❌ Error during game: {e}")
            try:
                send_message(conn, MSG_ERROR, message=str(e))
            except:
                pass
            return None
    
    def run_match(self, num_games=5):
        """
        Run a match of multiple games.
        
        Args:
            num_games: Number of games in the match
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(num_games)
            
            print(f"\n{'='*60}")
            print(f"🎲 Bob's Dice Game Server")
            print(f"{'='*60}")
            print(f"📡 Listening on {self.host}:{self.port}")
            print(f"🎯 Match: {num_games} games")
            print(f"⏳ Waiting for Alice to connect...")
            print(f"{'='*60}\n")
            
            alice_wins = 0
            bob_wins = 0
            ties = 0
            
            for game_num in range(1, num_games + 1):
                conn, addr = server_socket.accept()
                with conn:
                    result = self.handle_game(conn, addr, game_num)
                    
                    if result is None:
                        print(f"❌ Game {game_num} failed")
                        continue
                    
                    alice_sum, bob_sum, winner = result
                    
                    if winner == 1:
                        alice_wins += 1
                    elif winner == 2:
                        bob_wins += 1
                    else:
                        ties += 1
                
                if game_num < num_games:
                    print(f"\n⏳ Ready for next game...\n")
                    time.sleep(1)
            
            # Display match result
            print(f"\n{'='*70}")
            print(f"🏆 MATCH FINAL RESULTS")
            print(f"{'='*70}")
            print(f"Total games played: {num_games}")
            print(f"Alice wins: {alice_wins}")
            print(f"Bob wins:   {bob_wins}")
            print(f"Ties:       {ties}")
            print(f"")
            
            if alice_wins > bob_wins:
                print(f"😔 Alice wins the match ({alice_wins}-{bob_wins})")
            elif bob_wins > alice_wins:
                print(f"🎉 BOB WINS THE MATCH! ({bob_wins}-{alice_wins})")
            else:
                print(f"🤝 MATCH TIED! ({alice_wins}-{bob_wins})")
            
            print(f"{'='*70}\n")


def main():
    """Main entry point."""
    # Get configuration from environment variables (for Docker)
    host = os.environ.get('BOB_HOST', '0.0.0.0')
    port = int(os.environ.get('BOB_PORT', 5555))
    num_games = int(os.environ.get('NUM_GAMES', 5))
    
    server = BobServer(host=host, port=port)
    
    try:
        server.run_match(num_games=num_games)
    except KeyboardInterrupt:
        print("\n\n👋 Server shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
