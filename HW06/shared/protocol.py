"""
Rock-Paper-Scissors Commitment Protocol
Implements a cryptographically secure commit-reveal scheme to prevent cheating.
"""

import hashlib
import secrets
import json

# Game moves
ROCK = "rock"
PAPER = "paper"
SCISSORS = "scissors"
VALID_MOVES = {ROCK, PAPER, SCISSORS}

# Protocol message types
MSG_COMMIT = "COMMIT"
MSG_MOVE = "MOVE"
MSG_REVEAL = "REVEAL"
MSG_RESULT = "RESULT"
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
            value: The value to commit to (e.g., "rock")
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


class GameLogic:
    """Rock-Paper-Scissors game logic."""
    
    @staticmethod
    def is_valid_move(move):
        """Check if a move is valid."""
        return move in VALID_MOVES
    
    @staticmethod
    def determine_winner(move1, move2):
        """
        Determine the winner between two moves.
        
        Args:
            move1: First player's move
            move2: Second player's move
            
        Returns:
            1 if player 1 wins, 2 if player 2 wins, 0 for tie
        """
        if move1 == move2:
            return 0  # Tie
        
        winning_combinations = {
            (ROCK, SCISSORS),
            (SCISSORS, PAPER),
            (PAPER, ROCK)
        }
        
        if (move1, move2) in winning_combinations:
            return 1  # Player 1 wins
        else:
            return 2  # Player 2 wins
    
    @staticmethod
    def get_result_message(winner, alice_move, bob_move):
        """Generate a human-readable result message."""
        if winner == 0:
            return f"TIE! Both played {alice_move}"
        elif winner == 1:
            return f"ALICE WINS! {alice_move} beats {bob_move}"
        else:
            return f"BOB WINS! {bob_move} beats {alice_move}"


class ProtocolMessage:
    """Helper class for creating and parsing protocol messages."""
    
    @staticmethod
    def create(msg_type, **kwargs):
        """
        Create a protocol message.
        
        Args:
            msg_type: Type of message (COMMIT, MOVE, REVEAL, RESULT, ERROR)
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
