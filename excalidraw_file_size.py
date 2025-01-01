from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def get_file_size(file_path):
    return file_path.stat().st_size

def get_excalidraw_files(directory):
    return list(directory.rglob("*.excalidraw"))

def main():
    if len(sys.argv) < 2:
        print("Usage: python excalidraw_file_size.py <directory>")
        sys.exit(1)
    directory = Path(sys.argv[1])
    excalidraw_files = get_excalidraw_files(directory)
    
    with ThreadPoolExecutor() as executor:
        file_sizes = list(executor.map(get_file_size, excalidraw_files))
    
    excalidraw_files_with_sizes = sorted(
        zip(excalidraw_files, file_sizes),
        key=lambda x: (x[0].parent, x[1]),
        reverse=True
    )
    
    data = [(size / (1024 * 1024), str(file.parent), file.name) for file, size in excalidraw_files_with_sizes]
    df = pd.DataFrame(data, columns=["Size (MB)", "Directory", "File Name"])
    
    # Print DataFrame in a more readable format
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(df)
    
    output_csv = directory / "excalidraw_file_sizes.csv"
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()