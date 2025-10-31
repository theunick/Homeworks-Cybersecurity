#!/usr/bin/env python3
"""
Script to generate performance comparison charts for cryptographic algorithms
Used for HW03 - Cybersecurity course
Author: Nicolas Leone - Student ID: 1986354
"""

import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

def read_results(filename='results.csv'):
    """Read results from CSV file"""
    algorithms = []
    avg_enc = []
    avg_dec = []
    min_enc = []
    max_enc = []
    min_dec = []
    max_dec = []
    
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                algorithms.append(row['Algorithm'])
                avg_enc.append(float(row['Avg_Encryption_us']))
                avg_dec.append(float(row['Avg_Decryption_us']))
                min_enc.append(float(row['Min_Enc_us']))
                max_enc.append(float(row['Max_Enc_us']))
                min_dec.append(float(row['Min_Dec_us']))
                max_dec.append(float(row['Max_Dec_us']))
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        print("Please run the C program first to generate results.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading results: {e}")
        sys.exit(1)
    
    return algorithms, avg_enc, avg_dec, min_enc, max_enc, min_dec, max_dec

def create_comparison_chart(algorithms, avg_enc, avg_dec):
    """Create bar chart comparing encryption and decryption times"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_pos = np.arange(len(algorithms))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x_pos - width/2, avg_enc, width, label='Encryption', 
                   color='#e67e22', alpha=0.85, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x_pos + width/2, avg_dec, width, label='Decryption', 
                   color='#9b59b6', alpha=0.85, edgecolor='black', linewidth=1.2)
    
    # Customize the plot
    ax.set_xlabel('Algorithm Configuration', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Time (microseconds)', fontsize=13, fontweight='bold')
    ax.set_title('Encryption vs Decryption Performance - Average of 5 Runs', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms, fontsize=10, rotation=15, ha='right')
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set background colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = 'performance_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def create_encryption_chart(algorithms, avg_enc, min_enc, max_enc):
    """Create bar chart with error bars for encryption times"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_pos = np.arange(len(algorithms))
    
    # Calculate error bars (distance from average to min/max)
    yerr_lower = [avg - min_val for avg, min_val in zip(avg_enc, min_enc)]
    yerr_upper = [max_val - avg for avg, max_val in zip(avg_enc, max_enc)]
    
    # Create bars with error bars
    bars = ax.bar(x_pos, avg_enc, color='#3498db', alpha=0.85, 
                  edgecolor='black', linewidth=1.2, label='Average')
    ax.errorbar(x_pos, avg_enc, yerr=[yerr_lower, yerr_upper], 
                fmt='none', ecolor='red', capsize=5, capthick=2, 
                linewidth=2, label='Min/Max Range')
    
    # Customize the plot
    ax.set_xlabel('Algorithm Configuration', fontsize=13, fontweight='bold')
    ax.set_ylabel('Encryption Time (microseconds)', fontsize=13, fontweight='bold')
    ax.set_title('Encryption Performance with Min/Max Range (5 Runs)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms, fontsize=10, rotation=15, ha='right')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, avg, min_val, max_val) in enumerate(zip(bars, avg_enc, min_enc, max_enc)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(avg)}',
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set background colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = 'encryption_performance.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def create_decryption_chart(algorithms, avg_dec, min_dec, max_dec):
    """Create bar chart with error bars for decryption times"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_pos = np.arange(len(algorithms))
    
    # Calculate error bars
    yerr_lower = [avg - min_val for avg, min_val in zip(avg_dec, min_dec)]
    yerr_upper = [max_val - avg for avg, max_val in zip(avg_dec, max_dec)]
    
    # Create bars with error bars
    bars = ax.bar(x_pos, avg_dec, color='#2ecc71', alpha=0.85, 
                  edgecolor='black', linewidth=1.2, label='Average')
    ax.errorbar(x_pos, avg_dec, yerr=[yerr_lower, yerr_upper], 
                fmt='none', ecolor='red', capsize=5, capthick=2, 
                linewidth=2, label='Min/Max Range')
    
    # Customize the plot
    ax.set_xlabel('Algorithm Configuration', fontsize=13, fontweight='bold')
    ax.set_ylabel('Decryption Time (microseconds)', fontsize=13, fontweight='bold')
    ax.set_title('Decryption Performance with Min/Max Range (5 Runs)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms, fontsize=10, rotation=15, ha='right')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, avg) in enumerate(zip(bars, avg_dec)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(avg)}',
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set background colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = 'decryption_performance.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def create_throughput_chart(algorithms, avg_enc, avg_dec, file_size_mb):
    """Create chart showing throughput in MB/s"""
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Calculate throughput in MB/s
    enc_throughput = [(file_size_mb / (time / 1000000.0)) for time in avg_enc]
    dec_throughput = [(file_size_mb / (time / 1000000.0)) for time in avg_dec]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_pos = np.arange(len(algorithms))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x_pos - width/2, enc_throughput, width, label='Encryption', 
                   color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x_pos + width/2, dec_throughput, width, label='Decryption', 
                   color='#16a085', alpha=0.85, edgecolor='black', linewidth=1.2)
    
    # Customize the plot
    ax.set_xlabel('Algorithm Configuration', fontsize=13, fontweight='bold')
    ax.set_ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
    ax.set_title(f'Encryption/Decryption Throughput ({file_size_mb:.0f} MB File)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms, fontsize=10, rotation=15, ha='right')
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Set background colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = 'throughput_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

def main():
    print("="*60)
    print("  Generating Performance Charts")
    print("  HW03 - Cybersecurity Course")
    print("  Student: Nicolas Leone (1986354)")
    print("="*60)
    print()
    
    # Read results
    print("Reading results from CSV file...")
    algorithms, avg_enc, avg_dec, min_enc, max_enc, min_dec, max_dec = read_results()
    
    print(f"Found {len(algorithms)} algorithm configurations:")
    for i, algo in enumerate(algorithms):
        print(f"  {i+1}. {algo}")
    print()
    
    # Generate charts
    print("Generating charts...\n")
    create_comparison_chart(algorithms, avg_enc, avg_dec)
    create_encryption_chart(algorithms, avg_enc, min_enc, max_enc)
    create_decryption_chart(algorithms, avg_dec, min_dec, max_dec)
    
    # Calculate file size from first algorithm's average time (10 MB expected)
    file_size_mb = 10.0  # As specified in generate_testfile.c
    create_throughput_chart(algorithms, avg_enc, avg_dec, file_size_mb)
    
    print("\n" + "="*60)
    print("All charts generated successfully!")
    print("="*60)
    print("\nGenerated files:")
    print("  1. performance_comparison.png")
    print("  2. encryption_performance.png")
    print("  3. decryption_performance.png")
    print("  4. throughput_comparison.png")
    print("\nYou can now include these charts in your LaTeX document!")

if __name__ == '__main__':
    main()
