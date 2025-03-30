import PyInstaller.__main__

PyInstaller.__main__.run([
    'translate.py',
    '--onefile',
    '--windowed',
    '--noconsole',
    #'--icon=icon.ico',  # إذا كان لديك أيقونة
    # '--add-data=media_folders.db;.'
])
