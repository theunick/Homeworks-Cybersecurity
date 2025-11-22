#!/usr/bin/env python3
"""
DRBG Benchmark Suite
Compares three Cryptographically Secure Pseudo-Random Number Generators:
- ChaCha20-based DRBG
- AES-CTR based DRBG
- HMAC-DRBG

Author: Nicolas Leone (1986354)
Date: November 2025
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib
import os
import time
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple


class ChaCha20DRBG:
    """ChaCha20-based Deterministic Random Bit Generator"""
    
    def __init__(self, seed=None):
        """
        Initialize ChaCha20 DRBG
        
        Args:
            seed: Optional 32-byte seed. If None, generates from os.urandom()
        """
        if seed is None:
            seed = os.urandom(32)
        elif len(seed) < 32:
            seed = seed.ljust(32, b'\x00')
        
        self.key = seed[:32]
        self.nonce = os.urandom(16)
        self.counter = 0
    
    def generate(self, num_bits: int) -> str:
        """
        Generate pseudo-random bits
        
        Args:
            num_bits: Number of bits to generate
            
        Returns:
            Binary string of generated bits
        """
        num_bytes = (num_bits + 7) // 8
        
        # Create ChaCha20 cipher
        cipher = Cipher(
            algorithms.ChaCha20(self.key, self.nonce),
            mode=None,
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Generate random bytes by encrypting zeros
        plaintext = b'\x00' * num_bytes
        random_bytes = encryptor.update(plaintext)
        
        # Convert to binary string
        binary_string = ''.join(format(byte, '08b') for byte in random_bytes)
        
        return binary_string[:num_bits]


class AESCTR_DRBG:
    """AES-CTR based Deterministic Random Bit Generator"""
    
    def __init__(self, seed=None):
        """
        Initialize AES-CTR DRBG
        
        Args:
            seed: Optional 32-byte seed. If None, generates from os.urandom()
        """
        if seed is None:
            seed = os.urandom(32)
        elif len(seed) < 32:
            seed = seed.ljust(32, b'\x00')
        
        self.key = seed[:32]
        self.counter = 0
    
    def generate(self, num_bits: int) -> str:
        """
        Generate pseudo-random bits using AES in CTR mode
        
        Args:
            num_bits: Number of bits to generate
            
        Returns:
            Binary string of generated bits
        """
        num_bytes = (num_bits + 7) // 8
        
        # Use counter as nonce for CTR mode
        nonce = self.counter.to_bytes(16, 'big')
        
        # Create AES-CTR cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CTR(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt zeros to get random output
        plaintext = b'\x00' * num_bytes
        random_bytes = encryptor.update(plaintext) + encryptor.finalize()
        
        self.counter += 1
        
        # Convert to binary string
        binary_string = ''.join(format(byte, '08b') for byte in random_bytes)
        
        return binary_string[:num_bits]


class HMAC_DRBG:
    """HMAC-based Deterministic Random Bit Generator (NIST SP 800-90A)"""
    
    def __init__(self, seed=None):
        """
        Initialize HMAC-DRBG according to NIST SP 800-90A
        
        Args:
            seed: Optional seed material. If None, generates from os.urandom()
        """
        if seed is None:
            seed = os.urandom(32)
        
        # Initialize K and V according to NIST specification
        self.K = b'\x00' * 32  # 256 bits
        self.V = b'\x01' * 32  # 256 bits
        
        # Perform initial update with seed
        self._update(seed)
    
    def _update(self, provided_data=None):
        """
        Update internal state (K and V)
        
        Args:
            provided_data: Optional additional input for update
        """
        # K = HMAC(K, V || 0x00 || provided_data)
        self.K = hmac.new(
            self.K,
            self.V + b'\x00' + (provided_data if provided_data else b''),
            hashlib.sha256
        ).digest()
        
        # V = HMAC(K, V)
        self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
        
        if provided_data is not None:
            # K = HMAC(K, V || 0x01 || provided_data)
            self.K = hmac.new(
                self.K,
                self.V + b'\x01' + provided_data,
                hashlib.sha256
            ).digest()
            
            # V = HMAC(K, V)
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
    
    def generate(self, num_bits: int) -> str:
        """
        Generate pseudo-random bits
        
        Args:
            num_bits: Number of bits to generate
            
        Returns:
            Binary string of generated bits
        """
        num_bytes = (num_bits + 7) // 8
        output = b''
        
        # Generate output by repeatedly applying HMAC
        while len(output) < num_bytes:
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
            output += self.V
        
        # Update state after generation
        self._update()
        
        # Convert to binary string
        binary_string = ''.join(format(byte, '08b') for byte in output)
        
        return binary_string[:num_bits]


def benchmark_drbg(drbg_class, name: str, lengths: List[int], num_runs: int = 5) -> Dict:
    """
    Benchmark a DRBG implementation
    
    Args:
        drbg_class: DRBG class to benchmark
        name: Name of the DRBG
        lengths: List of sequence lengths to test
        num_runs: Number of runs per length for averaging
        
    Returns:
        Dictionary containing benchmark results
    """
    results = {
        'name': name,
        'lengths': lengths,
        'times': [],
        'memory': [],
        'zeros_pct': [],
        'ones_pct': []
    }
    
    print(f"\nBenchmarking {name}...")
    
    for length in lengths:
        print(f"  Testing length: {length:,} bits")
        
        # Measure time (average over multiple runs)
        times = []
        for run in range(num_runs):
            drbg = drbg_class()
            start = time.perf_counter()
            bits = drbg.generate(length)
            end = time.perf_counter()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        results['times'].append(avg_time)
        
        # Measure memory (single run)
        tracemalloc.start()
        drbg = drbg_class()
        bits = drbg.generate(length)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_mb = peak / (1024 * 1024)
        results['memory'].append(memory_mb)
        
        # Count 0s and 1s
        zeros = bits.count('0')
        ones = bits.count('1')
        
        zeros_pct = (zeros / length) * 100
        ones_pct = (ones / length) * 100
        
        results['zeros_pct'].append(zeros_pct)
        results['ones_pct'].append(ones_pct)
        
        print(f"    Time: {avg_time:.4f}s, Memory: {memory_mb:.2f}MB, "
              f"0s: {zeros_pct:.2f}%, 1s: {ones_pct:.2f}%")
    
    return results


def plot_results(all_results: List[Dict], output_dir: str = '.'):
    """
    Generate comparison plots
    
    Args:
        all_results: List of benchmark results for each DRBG
        output_dir: Directory to save plots
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    lengths = all_results[0]['lengths']
    length_labels = [f"$10^{{{int(np.log10(l))}}}$" for l in lengths]
    
    # 1. Time Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, result in enumerate(all_results):
        ax.plot(range(len(lengths)), result['times'], 
                marker='o', linewidth=2, markersize=8,
                label=result['name'], color=colors[i])
    
    ax.set_xlabel('Sequence Length (bits)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Execution Time Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(lengths)))
    ax.set_xticklabels(length_labels)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/time_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Memory Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, result in enumerate(all_results):
        ax.plot(range(len(lengths)), result['memory'], 
                marker='s', linewidth=2, markersize=8,
                label=result['name'], color=colors[i])
    
    ax.set_xlabel('Sequence Length (bits)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory (MB)', fontsize=12, fontweight='bold')
    ax.set_title('Memory Consumption Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(lengths)))
    ax.set_xticklabels(length_labels)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/memory_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Distribution Comparison (0s and 1s)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    x = np.arange(len(lengths))
    width = 0.25
    
    for i, result in enumerate(all_results):
        offset = (i - 1) * width
        ax1.bar(x + offset, result['zeros_pct'], width, 
                label=result['name'], color=colors[i], alpha=0.8)
        ax2.bar(x + offset, result['ones_pct'], width, 
                label=result['name'], color=colors[i], alpha=0.8)
    
    # Add reference line at 50%
    ax1.axhline(y=50, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Expected (50%)')
    ax2.axhline(y=50, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Expected (50%)')
    
    for ax, title in [(ax1, 'Percentage of 0s'), (ax2, 'Percentage of 1s')]:
        ax.set_xlabel('Sequence Length (bits)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(length_labels)
        ax.legend(fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([49, 51])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/distribution_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Combined Performance Chart (Time vs Memory)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, result in enumerate(all_results):
        # Normalize both metrics to 0-100 scale for comparison
        norm_times = [(t / max(result['times'])) * 100 for t in result['times']]
        norm_memory = [(m / max(result['memory'])) * 100 for m in result['memory']]
        
        # Calculate combined score (lower is better)
        combined = [(t + m) / 2 for t, m in zip(norm_times, norm_memory)]
        
        ax.plot(range(len(lengths)), combined, 
                marker='D', linewidth=2, markersize=8,
                label=result['name'], color=colors[i])
    
    ax.set_xlabel('Sequence Length (bits)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Performance Score', fontsize=12, fontweight='bold')
    ax.set_title('Combined Performance (Time + Memory)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(lengths)))
    ax.set_xticklabels(length_labels)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/combined_performance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlots saved to {output_dir}/")


def generate_summary_table(all_results: List[Dict]) -> str:
    """
    Generate LaTeX table with summary statistics
    
    Args:
        all_results: List of benchmark results
        
    Returns:
        LaTeX table code
    """
    latex = "\\begin{table}[H]\n\\centering\n\\small\n"
    latex += "\\begin{tabular}{@{}lcccc@{}}\n\\toprule\n"
    latex += "\\textbf{DRBG} & \\textbf{Avg Time (s)} & \\textbf{Avg Memory (MB)} & "
    latex += "\\textbf{0s (\\%)} & \\textbf{1s (\\%)} \\\\ \\midrule\n"
    
    for result in all_results:
        avg_time = sum(result['times']) / len(result['times'])
        avg_memory = sum(result['memory']) / len(result['memory'])
        avg_zeros = sum(result['zeros_pct']) / len(result['zeros_pct'])
        avg_ones = sum(result['ones_pct']) / len(result['ones_pct'])
        
        latex += f"{result['name']} & {avg_time:.4f} & {avg_memory:.2f} & "
        latex += f"{avg_zeros:.2f} & {avg_ones:.2f} \\\\\n"
    
    latex += "\\bottomrule\n\\end{tabular}\n"
    latex += "\\caption{Average performance metrics across all sequence lengths}\n"
    latex += "\\label{tab:summary}\n\\end{table}\n"
    
    return latex


def main():
    """Main benchmark execution"""
    print("=" * 60)
    print("DRBG Benchmark Suite")
    print("Nicolas Leone (1986354)")
    print("=" * 60)
    
    # Test sequence lengths: 10^4, 10^5, 10^6, 10^7
    lengths = [10**4, 10**5, 10**6, 10**7]
    
    # Benchmark all three DRBGs
    drbgs = [
        (ChaCha20DRBG, "ChaCha20-DRBG"),
        (AESCTR_DRBG, "AES-CTR DRBG"),
        (HMAC_DRBG, "HMAC-DRBG")
    ]
    
    all_results = []
    
    for drbg_class, name in drbgs:
        result = benchmark_drbg(drbg_class, name, lengths, num_runs=5)
        all_results.append(result)
    
    # Generate plots
    print("\nGenerating comparison plots...")
    plot_results(all_results)
    
    # Generate summary table
    print("\nGenerating summary table...")
    table_latex = generate_summary_table(all_results)
    
    with open('summary_table.tex', 'w') as f:
        f.write(table_latex)
    
    print("\n" + "=" * 60)
    print("Benchmark Complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - time_comparison.png")
    print("  - memory_comparison.png")
    print("  - distribution_comparison.png")
    print("  - combined_performance.png")
    print("  - summary_table.tex")
    print("\nRun 'make pdf' to generate the complete report.")


if __name__ == "__main__":
    main()
