moduledir = join_paths(pkgdatadir, 'flash_cards')
gnome = import('gnome')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)


configure_file(
  input: 'flash-cards.in',
  output: 'flash-cards',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

sources = [
  'app.py',
  'about.py',
  'editcard.py',
  'flashcard.py',
]

install_emptydir(moduledir / 'css')
install_data('css/style.css',install_dir: join_paths(moduledir,'css'))
install_data(sources, install_dir: moduledir)
