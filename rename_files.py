import argparse
import os
from pathlib import Path


def rename_files(folder, preview=True):
    # Get all files (excluding subdirectories)
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort()

    # Check for potential conflicts first
    new_names = set()
    for index, _ in enumerate(files, start=1):
        if str(index) in new_names:
            print(f"错误：检测到潜在的文件名冲突：{index}")
            return False
        new_names.add(str(index))

    # Preview or perform the renaming
    for index, filename in enumerate(files, start=1):
        _, ext = os.path.splitext(filename)
        new_filename = f"{index}{ext}"
        
        src = os.path.join(folder, filename)
        dst = os.path.join(folder, new_filename)
        
        if preview:
            print(f"预览：'{filename}' -> '{new_filename}'")
        else:
            try:
                if os.path.exists(dst) and src.lower() != dst.lower():
                    print(f"错误：目标文件已存在：'{dst}'")
                    return False
                os.rename(src, dst)
                print(f"重命名：'{filename}' -> '{new_filename}'")
            except Exception as e:
                print(f"重命名文件时出错：'{src}' -> '{dst}'")
                print(f"错误信息：{str(e)}")
                return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="将指定目录下所有文件按顺序重命名（保留扩展名），例如 1.png, 2.jpg, …"
    )
    parser.add_argument("folder", help="目标文件夹路径")
    parser.add_argument("--execute", action="store_true", 
                      help="执行重命名操作（不带此参数则仅预览）")
    args = parser.parse_args()
    
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"错误：'{folder}' 不是一个有效的目录。")
        exit(1)
    
    success = rename_files(folder, preview=not args.execute)
    if not success:
        exit(1)

if __name__ == "__main__":
    main()