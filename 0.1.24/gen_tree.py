import os

import mkdocs_gen_files

# --- Configurações ---
IGNORED_NAMES = {
    'venv',
    'htmlcov',
    '__pycache__',
    'site',
    'docs',
    'mkdocs',
    'log',
    'dist',
    '.egg',
}
IGNORED_EXTENSIONS = {'.log', '.git'}
SVG_PATH = './docs/assets/svgs'


# --- Carregar SVGs ---
def load_svg_icons(path):
    icons = {}
    for filename in os.listdir(path):
        if filename.endswith('.svg'):
            name = os.path.splitext(filename)[0]
            with open(
                os.path.join(path, filename), 'r', encoding='utf-8'
            ) as f:
                icons[name] = f.read()
    return icons


ICONS = load_svg_icons(SVG_PATH)
ICON_FOLDER = ICONS.get('folder', '')
ICON_FILE = ICONS.get('file', '')
CARET = '<span class="caret">▶</span>'


def get_icon_for_extension(ext):
    extension_map = {
        '.typed': 'pytyped',
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html-5',
        '.css': 'css-3',
        '.md': 'markdown',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sh': 'bash',
        '.txt': 'file-text',
        '.c': 'c',
        '.cpp': 'cpp',
        '.java': 'java',
        '.go': 'gopher',
        '.php': 'php',
        '.rb': 'ruby',
        '.ts': 'typescript',
        '.tsx': 'react',
        '.jsx': 'react',
        '.vue': 'vue',
        '.r': 'r-lang',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.cs': 'csharp',
        '.fs': 'fsharp',
        '.dart': 'dart',
        '.erl': 'erlang',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.eex': 'elixir',
        '.leex': 'elixir',
        '.h': 'c',
        '.hpp': 'cpp',
        '.m': 'objective-c',
        '.mm': 'objective-c',
        '.pl': 'perl',
        '.pm': 'perl',
        '.t': 'perl',
        '.rs': 'rust',
        '.scala': 'scala',
        '.sbt': 'sbt',
        '.sc': 'scala',
        '.sql': 'mysql',
        '.xml': 'xml',
        '.xaml': 'xaml',
        '.svg': 'svg',
        '.png': 'file-image',
        '.jpg': 'file-image',
        '.jpeg': 'file-image',
        '.gif': 'file-image',
        '.bmp': 'file-image',
        '.tiff': 'file-image',
        '.ico': 'file-image',
        '.webp': 'file-image',
        '.pdf': 'file-pdf',
        '.doc': 'file-word',
        '.docx': 'file-word',
        '.xls': 'file-excel',
        '.xlsx': 'file-excel',
        '.ppt': 'file-powerpoint',
        '.pptx': 'file-powerpoint',
        '.zip': 'file-zip',
        '.tar': 'file-zip',
        '.gz': 'file-zip',
        '.bz2': 'file-zip',
        '.rar': 'file-zip',
        '.7z': 'file-zip',
        '.log': 'file-text',
        '.ini': 'file-text',
        '.cfg': 'file-text',
        '.conf': 'file-text',
        '.env': 'file-text',
        '.toml': 'file-text',
        '.csproj': 'visual-studio',
        '.sln': 'visual-studio',
        '.vb': 'visual-studio',
        '.vbs': 'visual-studio',
        '.cmd': 'terminal',
        '.bat': 'terminal',
        '.ps1': 'terminal',
        '.psm1': 'terminal',
        '.psd1': 'terminal',
        '.ps1xml': 'terminal',
        '.psc1': 'terminal',
        '.pssc': 'terminal',
        '.vhd': 'virtual-machine',
        '.vhdx': 'virtual-machine',
        '.vmdk': 'virtual-machine',
        '.vdi': 'virtual-machine',
        '.ova': 'virtual-machine',
        '.ovf': 'virtual-machine',
        '.pcap': 'wireshark',
        '.pcapng': 'wireshark',
        '.saz': 'fiddler',
        '.har': 'fiddler',
        '.crx': 'chrome',
        '.xpi': 'firefox',
        '.safariextz': 'safari',
        '.opx': 'opera',
        '.crdownload': 'chrome',
        '.part': 'firefox',
        '.download': 'safari',
        '.dmg': 'apple',
        '.app': 'apple',
        '.ipa': 'apple',
        '.apk': 'android',
        '.xapk': 'android',
        '.apkm': 'android',
        '.apks': 'android',
        '.aab': 'android',
        '.exe': 'microsoft-windows',
        '.msi': 'microsoft-windows',
        '.dll': 'microsoft-windows',
        '.sys': 'microsoft-windows',
        '.deb': 'debian',
        '.rpm': 'redhat',
        '.jar': 'java',
        '.war': 'java',
        '.ear': 'java',
        '.class': 'java',
        '.jsp': 'java',
        '.jspx': 'java',
        '.asp': 'iis',
        '.aspx': 'iis',
        '.ascx': 'iis',
        '.ashx': 'iis',
        '.asmx': 'iis',
        '.axd': 'iis',
        '.webinfo': 'iis',
        '.config': 'iis',
        '.sitemap': 'iis',
        '.master': 'iis',
        '.skin': 'iis',
        '.browser': 'iis',
        '.slk': 'excel',
        '.xla': 'excel',
        '.xlam': 'excel',
        '.xlt': 'excel',
        '.xltm': 'excel',
        '.xltx': 'excel',
        '.xlw': 'excel',
        '.csv': 'excel',
        '.prn': 'excel',
        '.dif': 'excel',
        '.dsn': 'excel',
        '.dqy': 'excel',
        '.rqy': 'excel',
        '.oqy': 'excel',
        '.pot': 'powerpoint',
        '.potm': 'powerpoint',
        '.potx': 'powerpoint',
        '.ppa': 'powerpoint',
        '.ppam': 'powerpoint',
        '.pps': 'powerpoint',
        '.ppsm': 'powerpoint',
        '.ppsx': 'powerpoint',
        '.sldm': 'powerpoint',
        '.sldx': 'powerpoint',
        '.thmx': 'powerpoint',
        '.dot': 'word',
        '.dotm': 'word',
        '.dotx': 'word',
        '.wbk': 'word',
        '.wiz': 'word',
        '.rtf': 'word',
        '.odt': 'word',
        '.ott': 'word',
        '.fodt': 'word',
        '.uot': 'word',
        '.eml': 'email',
        '.msg': 'email',
        '.mbox': 'email',
        '.mbx': 'email',
        '.emlx': 'email',
        '.vcf': 'vcard',
        '.vcard': 'vcard',
        '.ics': 'calendar',
        '.ical': 'calendar',
        '.ifb': 'calendar',
        '.icalendar': 'calendar',
        '.torrent': 'bittorrent',
        '.rss': 'rss',
        '.gem': 'rubygems',
        '.gemspec': 'rubygems',
        '.lock': 'lock',
        '.pem': 'key',
        '.key': 'key',
        '.crt': 'key',
        '.cer': 'key',
        '.der': 'key',
        '.pfx': 'key',
        '.p12': 'key',
        '.p7b': 'key',
        '.p7c': 'key',
        '.p7s': 'key',
        '.crl': 'key',
        '.csr': 'key',
        '.pub': 'key',
        '.asc': 'key',
        '.gpg': 'key',
        '.sig': 'key',
        '.pgp': 'key',
        '.license': 'license',
        '.lic': 'license',
        '.readme': 'readme',
        '.authors': 'authors',
        '.changelog': 'changelog',
        '.contributing': 'contributing',
        '.code_of_conduct': 'code-of-conduct',
        '.github': 'github-icon',
        '.gitignore': 'git',
        '.gitattributes': 'git',
        '.gitmodules': 'git',
        '.gitkeep': 'git',
        '.gitlab-ci.yml': 'gitlab',
        '.travis.yml': 'travis-ci',
        '.jenkinsfile': 'jenkins',
        '.drone.yml': 'drone',
        '.codefresh.yml': 'codefresh',
        '.wercker.yml': 'wercker',
        '.shippable.yml': 'shippable',
        '.coveralls.yml': 'coveralls',
        '.codeclimate.yml': 'codeclimate',
        '.hound.yml': 'houndci',
        '.styleci.yml': 'styleci',
        '.scrutinizer.yml': 'scrutinizer',
        '.codecov.yml': 'codecov',
        '.sol': 'solidity',
        '.vy': 'vyper',
        '.ligo': 'ligo',
        '.rel': 'reasonml',
        '.re': 'reasonml',
        '.ml': 'ocaml',
        '.mli': 'ocaml',
        '.clj': 'clojure',
        '.cljc': 'clojure',
        '.edn': 'clojure',
        '.elm': 'elm',
        '.hrl': 'erlang',
        '.es': 'erlang',
        '.escript': 'erlang',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.hx': 'haxe',
        '.hxml': 'haxe',
        '.lisp': 'lisp',
        '.lsp': 'lisp',
        '.cl': 'lisp',
        '.fasl': 'lisp',
        '.nim': 'nim',
        '.nimble': 'nim',
        '.nims': 'nim',
        '.android-icon': 'android-icon',
        '.android': 'android-icon',
        '.angular-icon': 'angular-icon',
        '.angular': 'angular-icon',
        '.backbone-icon': 'backbone-icon',
        '.backbone': 'backbone-icon',
        '.bash': 'bash',
        '.bem-2': 'bem-2',
        '.bem': 'bem-2',
        '.browserify-icon': 'browserify-icon',
        '.browserify': 'browserify-icon',
        '.centos-icon': 'centos-icon',
        '.centos': 'centos-icon',
        '.chrome': 'chrome',
        '.clojure': 'clojure',
        '.codepen-icon': 'codepen-icon',
        '.codepen': 'codepen-icon',
        '.coreos-icon': 'coreos-icon',
        '.coreos': 'coreos-icon',
        '.css-3': 'css-3',
        '.css-3_official': 'css-3_official',
        '.dribbble-icon': 'dribbble-icon',
        '.dribbble': 'dribbble-icon',
        '.ember': 'ember',
        '.erlang': 'erlang',
        '.flickr': 'flickr-icon',
        '.git': 'git-icon',
        '.instagram': 'instagram-icon',
        '.javascript': 'javascript',
        '.kotlin': 'kotlin',
        '.magneto': 'magneto',
        '.markdown': 'markdown',
        '.meteor': 'meteor-icon',
        '.mysql': 'mysql',
        '.nodejs': 'nodejs-icon',
        '.npm': 'npm-2',
        '.processwire': 'processwire-icon',
        '.python': 'python',
        '.react': 'react',
        '.ruby': 'ruby',
        '.rubygems': 'rubygems',
        '.rust': 'rust',
        '.tumblr': 'tumblr-icon',
        '.vimeo': 'vimeo-icon',
        '.wordpress': 'wordpress-icon',
    }
    icon_name = extension_map.get(ext, 'any')
    return ICONS.get(icon_name, ICON_FILE)


def generate_tree_html(path='.', level=0, max_level=3):
    if level > max_level:
        return ''
    try:
        entries = sorted(os.listdir(path))
    except FileNotFoundError:
        return ''

    entries = [
        e
        for e in entries
        if not e.startswith('.')
        and not any(ext in e for ext in IGNORED_NAMES)
        and not any(e.lower().endswith(ext) for ext in IGNORED_EXTENSIONS)
    ]
    if not entries:
        return ''

    html = '<ul class="file-tree">\n'
    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            html += (
                f'<li class="folder">'
                f'<div class="folder-header">{CARET}<span class="folder-icon">'
                f'{ICON_FOLDER}</span><span class="folder">{entry}</span>'
                f'</div>{generate_tree_html(full_path, level + 1, max_level)}'
                f'</li>\n'
            )
        else:
            ext = os.path.splitext(entry)[1].lower()
            icon = get_icon_for_extension(ext)
            html += (
                f'<li><span class="icon">{icon}</span>'
                f'<span class="file">{entry}</span></li>\n'
            )
    html += '</ul>\n'
    return html


def main():
    html_tree = generate_tree_html('.')
    html_tree = f'<div class="tree-container">\n{html_tree}\n</div>'
    with mkdocs_gen_files.open('estrutura.md', 'w+', encoding='utf-8') as f:
        f.write(html_tree)


main()
