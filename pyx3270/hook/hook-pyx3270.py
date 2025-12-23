import os

from PyInstaller.utils.hooks import get_package_paths

# Caminho do pacote instalado
package_path, _ = get_package_paths('pyx3270')

# Caminho da pasta bin dentro do pacote
bin_dir = os.path.join(package_path, 'pyx3270', 'bin')

datas = []

if os.path.isdir(bin_dir):
    for root, _, files in os.walk(bin_dir):
        for file in files:
            full_path = os.path.join(root, file)
            # Caminho relativo a partir da pasta bin (ex: windows/wc3270.exe)
            rel_path = os.path.relpath(full_path, bin_dir)
            # Corrige o destino para ser uma pasta, não um arquivo
            target_dir = os.path.join(
                'pyx3270', 'bin', os.path.dirname(rel_path)
            )
            datas.append((full_path, target_dir))

__all__ = ['datas']
