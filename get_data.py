import os
import shutil

TARGETS = ['M1228', 'M1239', 'R1203', 'T1228', 'T1239', 'T1249']

def copy_output_files():
    base_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Casp_assessment/Targets'))
    dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'DATA'))
    for target in TARGETS:
        src_dir = os.path.join(base_src, target, 'Output')
        if not os.path.isdir(src_dir):
            print(f"Output directory not found for {target}: {src_dir}")
            continue
        for fname in os.listdir(src_dir):
            src_file = os.path.join(src_dir, fname)
            dest_file = os.path.join(dest_dir, fname)
            try:
                shutil.copy2(src_file, dest_file)
                print(f"Copied {src_file} to {dest_file}")
            except Exception as e:
                print(f"Failed to copy {src_file}: {e}")

if __name__ == "__main__":
    copy_output_files()
