"""
Dice Game Commitment Protocol
Implements a cryptographically secure commit-reveal scheme for dice games.
"""

import hashlib
import secrets
import json
import random

# Protocol message types
MSG_COMMIT = "COMMIT"
MSG_RESULT = "RESULT"
MSG_REVEAL = "REVEAL"
MSG_MATCH_RESULT = "MATCH_RESULT"
MSG_ERROR = "ERROR"


class CommitmentScheme:
    """
    Implements a cryptographic commitment scheme using SHA-256.
    
    Properties:
    - Hiding: The commitment doesn't reveal the committed value
    - Binding: The committer cannot change the value after commitment
    """
    
    @staticmethod
    def generate_nonce(length=32):
        """Generate a cryptographically secure random nonce."""
        return secrets.token_hex(length)
    
    @staticmethod
    def commit(value, nonce):
        """
        Create a commitment to a value using SHA-256.
        
        Args:
            value: The value to commit to (dice sum as string)
            nonce: A random nonce for security
            
        Returns:
            The commitment (SHA-256 hash as hex string)
        """
        data = f"{value}||{nonce}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def verify(commitment, value, nonce):
        """
        Verify that a revealed value matches the original commitment.
        
        Args:
            commitment: The original commitment hash
            value: The revealed value
            nonce: The revealed nonce
            
        Returns:
            True if verification succeeds, False otherwise
        """
        expected_commitment = CommitmentScheme.commit(value, nonce)
        return commitment == expected_commitment


class DiceLogic:
    """Dice game logic."""
    
    @staticmethod
    def roll_dice(num_dice=1):
        """
        Roll num_dice six-sided dice.
        
        Args:
            num_dice: Number of dice to roll
            
        Returns:
            List of dice results (each 1-6)
        """
        return [random.randint(1, 6) for _ in range(num_dice)]
    
    @staticmethod
    def calculate_sum(dice_results):
        """Calculate the sum of dice results."""
        return sum(dice_results)
    
    @staticmethod
    def determine_winner(sum1, sum2):
        """
        Determine the winner based on dice sums.
        
        Args:
            sum1: Player 1's dice sum
            sum2: Player 2's dice sum
            
        Returns:
            1 if player 1 wins, 2 if player 2 wins, 0 for tie
        """
        if sum1 > sum2:
            return 1  # Player 1 wins
        elif sum2 > sum1:
            return 2  # Player 2 wins
        else:
            return 0  # Tie
    
    @staticmethod
    def get_result_message(winner, alice_sum, bob_sum):
        """Generate a human-readable result message."""
        if winner == 0:
            return f"TIE! Both scored {alice_sum}"
        elif winner == 1:
            return f"ALICE WINS! {alice_sum} beats {bob_sum}"
        else:
            return f"BOB WINS! {bob_sum} beats {alice_sum}"
    
    @staticmethod
    def get_match_result_message(alice_wins, bob_wins, ties):
        """Generate match result message."""
        total = alice_wins + bob_wins + ties
        msg = f"MATCH COMPLETE ({total} games):\n"
        msg += f"  Alice wins: {alice_wins}\n"
        msg += f"  Bob wins: {bob_wins}\n"
        msg += f"  Ties: {ties}\n"
        
        if alice_wins > bob_wins:
            msg += f"\n🏆 ALICE WINS THE MATCH!"
        elif bob_wins > alice_wins:
            msg += f"\n🏆 BOB WINS THE MATCH!"
        else:
            msg += f"\n🤝 MATCH TIED!"
        
        return msg


class ProtocolMessage:
    """Helper class for creating and parsing protocol messages."""
    
    @staticmethod
    def create(msg_type, **kwargs):
        """
        Create a protocol message.
        
        Args:
            msg_type: Type of message
            **kwargs: Message-specific data
            
        Returns:
            JSON-encoded message string
        """
        message = {"type": msg_type, "data": kwargs}
        return json.dumps(message)
    
    @staticmethod
    def parse(message_str):
        """
        Parse a protocol message.
        
        Args:
            message_str: JSON-encoded message string
            
        Returns:
            Dictionary with 'type' and 'data' keys
        """
        try:
            message = json.loads(message_str)
            if "type" not in message or "data" not in message:
                raise ValueError("Invalid message format")
            return message
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse message: {e}")


def send_message(sock, msg_type, **kwargs):
    """
    Send a protocol message over a socket.
    
    Args:
        sock: Socket object
        msg_type: Message type
        **kwargs: Message data
    """
    message = ProtocolMessage.create(msg_type, **kwargs)
    sock.sendall(message.encode('utf-8') + b'\n')


def receive_message(sock):
    """
    Receive a protocol message from a socket.
    
    Args:
        sock: Socket object
        
    Returns:
        Parsed message dictionary
    """
    # Read until newline
    data = b''
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed")
        if chunk == b'\n':
            break
        data += chunk
    
    message_str = data.decode('utf-8')
    return ProtocolMessage.parse(message_str)
