#!/usr/bin/env python3
"""
Script to generate performance comparison charts for cryptographic algorithms
Used for HW02 - Cybersecurity course
Author: Nicolas Leone
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from the encryption/decryption tests (in microseconds)
# Results from HW02_Nicolas_Leone_1986354.c execution

# File sizes
file_names = ['16B', '20KB', '2MB']
algorithms = ['AES-128-CBC', 'SM4-128-CBC', 'Camellia-128-CBC']

# Encryption times (microseconds)
encryption_times = {
    '16B': [3, 7, 3],
    '20KB': [15, 166, 120],
    '2MB': [1045, 15788, 8843]
}

# Decryption times (microseconds)
decryption_times = {
    '16B': [1, 2, 1],
    '20KB': [5, 130, 89],
    '2MB': [241, 11365, 6564]
}

import matplotlib.pyplot as plt
import numpy as np

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')

# Data for 16B file (in microseconds)
algorithms = ['AES-128-CBC', 'SM4-128-CBC', 'Camellia-128-CBC']
encryption_16B = [2, 485, 3]
decryption_16B = [1, 2, 1]

# === Generate one graph per file size ===
print("Generating performance charts...\n")

for file_size in file_names:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = np.arange(len(algorithms))
    width = 0.35
    
    # Get encryption and decryption times for this file size
    enc_times = encryption_times[file_size]
    dec_times = decryption_times[file_size]
    
    # Create bars
    bars1 = ax.bar(x_pos - width/2, enc_times, width, label='Encryption', 
                   color='#e67e22', alpha=0.85, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x_pos + width/2, dec_times, width, label='Decryption', 
                   color='#9b59b6', alpha=0.85, edgecolor='black', linewidth=1.2)
    
    # Customize the plot
    ax.set_xlabel('Algorithm', fontsize=13, fontweight='bold')
    ax.set_ylabel('Time (microseconds)', fontsize=13, fontweight='bold')
    ax.set_title(f'Encryption vs Decryption Performance - {file_size} File', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms, fontsize=11)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add a subtle background color
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    filename = f'performance_{file_size}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Generated: {filename}")
    plt.close()

print("\n" + "="*50)
print("All charts generated successfully!")
print("="*50)
print("\nGenerated files:")
print("  1. performance_16B.png")
print("  2. performance_20KB.png")
print("  3. performance_2MB.png")
print("\nYou can now include these charts in your LaTeX document!")
