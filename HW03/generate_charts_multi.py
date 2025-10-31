#!/usr/bin/env python3
"""
Script to generate performance comparison charts for multiple file sizes
Used for HW03 - Cybersecurity course
Author: Nicolas Leone - Student ID: 1986354
"""

import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import sys
import glob

def read_all_results():
    """Read all results_*.csv files"""
    results = {}
    
    for csv_file in sorted(glob.glob("results_testfile_*.csv")):
        # Extract file size from filename
        size_str = csv_file.replace("results_testfile_", "").replace(".csv", "")
        
        algorithms = []
        avg_enc = []
        avg_dec = []
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    algorithms.append(row['Algorithm'])
                    avg_enc.append(float(row['Avg_Encryption_us']))
                    avg_dec.append(float(row['Avg_Decryption_us']))
            
            results[size_str] = {
                'algorithms': algorithms,
                'encryption': avg_enc,
                'decryption': avg_dec
            }
            print(f"✓ Loaded: {csv_file} ({size_str})")
        except Exception as e:
            print(f"✗ Error reading {csv_file}: {e}")
    
    return results

def extract_size_mb(size_str):
    """Extract numeric size in MB from size string"""
    return int(size_str.replace("MB.bin", ""))

def create_scaling_chart(results):
    """Create chart showing how performance scales with file size"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Sort by file size
    sorted_sizes = sorted(results.keys(), key=extract_size_mb)
    
    # Extract data for each algorithm
    algorithms = results[sorted_sizes[0]]['algorithms']
    colors = ['#e67e22', '#3498db', '#2ecc71', '#9b59b6']
    markers = ['o', 's', '^', 'D']
    
    file_sizes_mb = [extract_size_mb(s) for s in sorted_sizes]
    
    # Plot encryption performance scaling
    for i, algo in enumerate(algorithms):
        enc_times = []
        for size in sorted_sizes:
            idx = results[size]['algorithms'].index(algo)
            enc_times.append(results[size]['encryption'][idx] / 1000.0)  # Convert to ms
        
        ax1.plot(file_sizes_mb, enc_times, marker=markers[i], linewidth=2, 
                markersize=8, label=algo, color=colors[i])
    
    ax1.set_xlabel('File Size (MB)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Encryption Time (milliseconds)', fontsize=13, fontweight='bold')
    ax1.set_title('Encryption Performance Scaling', fontsize=15, fontweight='bold', pad=20)
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_facecolor('#f8f9fa')
    
    # Plot decryption performance scaling
    for i, algo in enumerate(algorithms):
        dec_times = []
        for size in sorted_sizes:
            idx = results[size]['algorithms'].index(algo)
            dec_times.append(results[size]['decryption'][idx] / 1000.0)  # Convert to ms
        
        ax2.plot(file_sizes_mb, dec_times, marker=markers[i], linewidth=2,
                markersize=8, label=algo, color=colors[i])
    
    ax2.set_xlabel('File Size (MB)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Decryption Time (milliseconds)', fontsize=13, fontweight='bold')
    ax2.set_title('Decryption Performance Scaling', fontsize=15, fontweight='bold', pad=20)
    ax2.legend(fontsize=10, loc='upper left')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_facecolor('#f8f9fa')
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    filename = 'performance_scaling.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def create_throughput_chart(results):
    """Create chart showing throughput for different file sizes"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    sorted_sizes = sorted(results.keys(), key=extract_size_mb)
    algorithms = results[sorted_sizes[0]]['algorithms']
    
    x = np.arange(len(sorted_sizes))
    width = 0.2
    colors = ['#e67e22', '#3498db', '#2ecc71', '#9b59b6']
    
    for i, algo in enumerate(algorithms):
        throughputs = []
        for size in sorted_sizes:
            size_mb = extract_size_mb(size)
            idx = results[size]['algorithms'].index(algo)
            avg_time_us = results[size]['encryption'][idx]
            throughput = (size_mb / (avg_time_us / 1000000.0))
            throughputs.append(throughput)
        
        offset = (i - len(algorithms)/2 + 0.5) * width
        bars = ax.bar(x + offset, throughputs, width, label=algo, 
                     color=colors[i], alpha=0.85, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax.set_xlabel('File Size', fontsize=13, fontweight='bold')
    ax.set_ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
    ax.set_title('Encryption Throughput Across Different File Sizes', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_sizes, fontsize=11)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = 'throughput_scaling.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def create_comparison_heatmap(results):
    """Create heatmap showing relative performance"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    sorted_sizes = sorted(results.keys(), key=extract_size_mb)
    algorithms = results[sorted_sizes[0]]['algorithms']
    
    # Create matrices for encryption and decryption
    enc_matrix = []
    dec_matrix = []
    
    for size in sorted_sizes:
        enc_row = []
        dec_row = []
        for algo in algorithms:
            idx = results[size]['algorithms'].index(algo)
            enc_row.append(results[size]['encryption'][idx] / 1000.0)  # ms
            dec_row.append(results[size]['decryption'][idx] / 1000.0)  # ms
        enc_matrix.append(enc_row)
        dec_matrix.append(dec_row)
    
    enc_matrix = np.array(enc_matrix)
    dec_matrix = np.array(dec_matrix)
    
    # Plot encryption heatmap
    im1 = ax1.imshow(enc_matrix.T, aspect='auto', cmap='YlOrRd', interpolation='nearest')
    ax1.set_xticks(np.arange(len(sorted_sizes)))
    ax1.set_yticks(np.arange(len(algorithms)))
    ax1.set_xticklabels(sorted_sizes, fontsize=10)
    ax1.set_yticklabels(algorithms, fontsize=10)
    ax1.set_xlabel('File Size', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Algorithm', fontsize=12, fontweight='bold')
    ax1.set_title('Encryption Time Heatmap (ms)', fontsize=14, fontweight='bold', pad=15)
    
    # Add text annotations
    for i in range(len(algorithms)):
        for j in range(len(sorted_sizes)):
            text = ax1.text(j, i, f'{enc_matrix[j, i]:.1f}',
                          ha="center", va="center", color="black", fontsize=9, fontweight='bold')
    
    plt.colorbar(im1, ax=ax1, label='Time (ms)')
    
    # Plot decryption heatmap
    im2 = ax2.imshow(dec_matrix.T, aspect='auto', cmap='YlGnBu', interpolation='nearest')
    ax2.set_xticks(np.arange(len(sorted_sizes)))
    ax2.set_yticks(np.arange(len(algorithms)))
    ax2.set_xticklabels(sorted_sizes, fontsize=10)
    ax2.set_yticklabels(algorithms, fontsize=10)
    ax2.set_xlabel('File Size', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Algorithm', fontsize=12, fontweight='bold')
    ax2.set_title('Decryption Time Heatmap (ms)', fontsize=14, fontweight='bold', pad=15)
    
    # Add text annotations
    for i in range(len(algorithms)):
        for j in range(len(sorted_sizes)):
            text = ax2.text(j, i, f'{dec_matrix[j, i]:.1f}',
                          ha="center", va="center", color="black", fontsize=9, fontweight='bold')
    
    plt.colorbar(im2, ax=ax2, label='Time (ms)')
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    filename = 'performance_heatmap.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def main():
    print("="*70)
    print("  Generating Multi-Size Performance Charts")
    print("  HW03 - Cybersecurity Course")
    print("  Student: Nicolas Leone (1986354)")
    print("="*70)
    print()
    
    # Read all results
    print("Reading results from CSV files...")
    results = read_all_results()
    
    if not results:
        print("\n✗ No results files found!")
        print("  Please run the tests first with: ./run_all_tests.sh")
        sys.exit(1)
    
    print(f"\nFound results for {len(results)} file sizes")
    print()
    
    # Generate charts
    print("Generating charts...\n")
    create_scaling_chart(results)
    create_throughput_chart(results)
    create_comparison_heatmap(results)
    
    print("\n" + "="*70)
    print("All charts generated successfully!")
    print("="*70)
    print("\nGenerated files:")
    print("  1. performance_scaling.png - Performance vs file size (log-log)")
    print("  2. throughput_scaling.png - Throughput comparison")
    print("  3. performance_heatmap.png - Performance heatmaps")
    print("\nYou can now include these charts in your LaTeX document!")

if __name__ == '__main__':
    main()
