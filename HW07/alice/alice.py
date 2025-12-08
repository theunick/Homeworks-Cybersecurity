#!/usr/bin/env python3
"""
Alice's Client - Dice Game
Implements the client side of the commit-reveal protocol for dice games.

Protocol Flow (Alice's perspective):
1. Connect to Bob's server
2. Roll k dice and create commitment (hash of sum)
3. Send commitment to Bob
4. Receive Bob's dice sum
5. Reveal own sum and nonce to Bob
6. Receive game result
7. Repeat for match length
8. Receive match result
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


class AliceClient:
    """Alice's client implementation."""
    
    def __init__(self, server_host='bob', server_port=5555, num_dice=3):
        self.server_host = server_host
        self.server_port = server_port
        self.num_dice = num_dice
        self.commitment_scheme = CommitmentScheme()
        self.dice_logic = DiceLogic()
    
    def play_game(self, game_num):
        """
        Play a single game with Bob.
        
        Args:
            game_num: Game number in the match
            
        Returns:
            Tuple (alice_sum, bob_sum, winner) or None on error
        """
        print(f"\n{'='*60}")
        print(f"🎲 Game {game_num}")
        print(f"{'='*60}\n")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                print(f"✅ Connected to Bob!\n")
                
                # Phase 1: Alice rolls dice and commits
                print(f"📤 Phase 1: Rolling {self.num_dice} dice and creating commitment...")
                alice_dice = self.dice_logic.roll_dice(self.num_dice)
                alice_sum = self.dice_logic.calculate_sum(alice_dice)
                
                print(f"🎲 Alice rolled: {alice_dice}")
                print(f"📊 Alice's sum: {alice_sum}")
                
                alice_nonce = self.commitment_scheme.generate_nonce()
                alice_commitment = self.commitment_scheme.commit(str(alice_sum), alice_nonce)
                
                print(f"✅ Generated commitment: {alice_commitment[:16]}...")
                print(f"   (This hides Alice's sum: {alice_sum})")
                
                send_message(sock, MSG_COMMIT, 
                           commitment=alice_commitment,
                           num_dice=self.num_dice)
                print(f"✅ Sent commitment to Bob\n")
                
                # Phase 2: Receive Bob's result
                print("📥 Phase 2: Waiting for Bob's dice sum...")
                msg = receive_message(sock)
                
                if msg['type'] == MSG_ERROR:
                    print(f"❌ Error from Bob: {msg['data']['message']}")
                    return None
                
                if msg['type'] != MSG_RESULT:
                    print(f"❌ Unexpected message type: {msg['type']}")
                    return None
                
                bob_sum = msg['data']['bob_sum']
                bob_dice = msg['data']['bob_dice']
                print(f"✅ Bob rolled: {bob_dice}")
                print(f"📊 Bob's sum: {bob_sum}")
                print(f"   (Bob chose without knowing Alice's sum!)\n")
                
                # Phase 3: Alice reveals
                print("📤 Phase 3: Revealing sum and nonce...")
                time.sleep(0.3)
                
                send_message(sock, MSG_REVEAL, 
                           alice_sum=alice_sum,
                           alice_dice=alice_dice,
                           nonce=alice_nonce)
                print(f"✅ Revealed sum: {alice_sum}")
                print(f"   Dice: {alice_dice}")
                print(f"   Nonce: {alice_nonce[:16]}...\n")
                
                # Phase 4: Receive game result
                print("📥 Phase 4: Waiting for game result...")
                msg = receive_message(sock)
                
                if msg['type'] == MSG_ERROR:
                    print(f"❌ Error from Bob: {msg['data']['message']}")
                    return None
                
                if msg['type'] != MSG_MATCH_RESULT:
                    print(f"❌ Unexpected message type: {msg['type']}")
                    return None
                
                # Display result
                winner = msg['data']['winner']
                result_msg = msg['data']['message']
                
                print(f"\n{'='*60}")
                print(f"📊 GAME {game_num} RESULT")
                print(f"{'='*60}")
                print(f"Alice: {alice_dice} = {alice_sum}")
                print(f"Bob:   {bob_dice} = {bob_sum}")
                print(f"\n{result_msg}")
                print(f"{'='*60}\n")
                
                return (alice_sum, bob_sum, winner)
                
        except ConnectionRefusedError:
            print(f"❌ Cannot connect to Bob at {self.server_host}:{self.server_port}")
            print(f"   Make sure Bob's server is running!")
            return None
        except Exception as e:
            print(f"❌ Error during game: {e}")
            return None
    
    def play_match(self, num_games):
        """
        Play a complete match with Bob.
        
        Args:
            num_games: Number of games in the match
        """
        print(f"\n{'='*60}")
        print(f"🎲 Alice's Dice Game Client")
        print(f"{'='*60}")
        print(f"🎯 Match configuration:")
        print(f"   - Number of dice: {self.num_dice}")
        print(f"   - Games in match: {num_games}")
        print(f"{'='*60}\n")
        
        alice_wins = 0
        bob_wins = 0
        ties = 0
        
        for game_num in range(1, num_games + 1):
            result = self.play_game(game_num)
            
            if result is None:
                print(f"❌ Game {game_num} failed, aborting match")
                return
            
            alice_sum, bob_sum, winner = result
            
            if winner == 1:
                alice_wins += 1
            elif winner == 2:
                bob_wins += 1
            else:
                ties += 1
            
            if game_num < num_games:
                print(f"\n⏳ Waiting 2 seconds before next game...\n")
                time.sleep(2)
        
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
            print(f"🎉 ALICE WINS THE MATCH! ({alice_wins}-{bob_wins})")
        elif bob_wins > alice_wins:
            print(f"😔 Bob wins the match ({bob_wins}-{alice_wins})")
        else:
            print(f"🤝 MATCH TIED! ({alice_wins}-{bob_wins})")
        
        print(f"{'='*70}\n")
        print(f"\n👋 Match completed!\n")


def main():
    """Main entry point."""
    # Get configuration from environment variables (for Docker)
    server_host = os.environ.get('BOB_HOST', 'bob')
    server_port = int(os.environ.get('BOB_PORT', 5555))
    num_dice = int(os.environ.get('NUM_DICE', 3))
    num_games = int(os.environ.get('NUM_GAMES', 5))
    
    # Add delay to ensure Bob's server is ready
    startup_delay = int(os.environ.get('STARTUP_DELAY', 2))
    if startup_delay > 0:
        print(f"⏳ Waiting {startup_delay} seconds for Bob's server to start...")
        time.sleep(startup_delay)
    
    client = AliceClient(server_host=server_host, 
                        server_port=server_port,
                        num_dice=num_dice)
    
    try:
        client.play_match(num_games=num_games)
    except KeyboardInterrupt:
        print("\n\n👋 Client shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
