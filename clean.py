import os
import shutil

def clean():
    print("開始清理...")
    
    # 刪除目錄
    dirs = ['__pycache__', 'release', 'build', 'dist']
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"已刪除目錄: {d}")
    
    # 刪除檔案
    files = ['README.md', 'build.py', 'build_exe.py', '擴視機.spec']
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"已刪除檔案: {f}")
    
    print("\n保留的檔案：")
    keep_files = [
        'main.py',
        'camera_module.py',
        'image_processor.py',
        'settings_dialog.py',
        'translations.py',
        'keyboard_controller.py',
        'requirements.txt',
        '使用指南.txt',
        '啟動程式.bat'
    ]
    
    for f in keep_files:
        if os.path.exists(f):
            print(f"- {f}")
    
    # 最後刪除清理腳本自己
    os.remove(__file__)

if __name__ == '__main__':
    clean() 