# b-berry-bin

## A personal $HOME/bin tracking repo

### Install Python Requirements

```bash
pip install -r requirements.txt
```

### Bash Config

- Source this repo's `.bashlg` config in your `~$HOME/.bashrc`:

```bash
if [ -f $HOME/bin/.bashlg ]; then
  source $HOME/bin/.bashlg
  export PATH="$HOME/bin/:$PATH"
fi

```

### Python Geocoding

- Quick geocode query:

`lg-geocode.py -q 'foo' 'bar' 'zee'`

- Generate KML:LookAt(s):

`lg-geocode.py -k 'foo' 'bar' 'zee'`

- Generate CZML:Billboard(s):

`lg-geocode.py -b 'foo.png' -c 'foo' 'bar' 'zee'`
