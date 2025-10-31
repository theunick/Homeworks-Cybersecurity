#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define BYTES_PER_MB (1024 * 1024)

void generate_file(const char *filename, int size_mb) {
    FILE *fp;
    unsigned char *buffer;
    size_t total_bytes = size_mb * BYTES_PER_MB;
    size_t chunk_size = BYTES_PER_MB; // Write 1MB at a time
    
    printf("Generating %s (%d MB)...\n", filename, size_mb);
    printf("Generating %s (%d MB)...\n", filename, size_mb);
    
    fp = fopen(filename, "wb");
    if (fp == NULL) {
        perror("Error opening file");
        return;
    }
    
    buffer = (unsigned char *)malloc(chunk_size);
    if (buffer == NULL) {
        perror("Memory allocation failed");
        fclose(fp);
        return;
    }
    
    srand(time(NULL));
    
    for (size_t i = 0; i < total_bytes; i += chunk_size) {
        size_t write_size = (i + chunk_size > total_bytes) ? (total_bytes - i) : chunk_size;
        
        // Fill buffer with random data
        for (size_t j = 0; j < write_size; j++) {
            buffer[j] = rand() % 256;
        }
        
        if (fwrite(buffer, 1, write_size, fp) != write_size) {
            perror("Error writing to file");
            free(buffer);
            fclose(fp);
            return;
        }
    }
    
    free(buffer);
    fclose(fp);
    
    printf("✓ Successfully created %s (%d MB)\n", filename, size_mb);
}

int main() {
    printf("=================================================================\n");
    printf("  Generating Test Files with Multiple Sizes\n");
    printf("=================================================================\n\n");
    
    // Generate files of increasing sizes: 1 MB, 5 MB, 10 MB, 50 MB, 100 MB
    generate_file("testfile_1MB.bin", 1);
    generate_file("testfile_5MB.bin", 5);
    generate_file("testfile_10MB.bin", 10);
    generate_file("testfile_50MB.bin", 50);
    generate_file("testfile_100MB.bin", 100);
    
    printf("\n=================================================================\n");
    printf("  All test files generated successfully!\n");
    printf("=================================================================\n");
    
    return 0;
}
