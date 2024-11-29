# ShokiNNs dotfiles

I manage my dotfiles using [dotdrop](https://github.com/deadc0de6/dotdrop).

## How to install

### Script

```shell
[[ ! $(command -v brew) ]] && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
  ; brew update \
  && brew install coreutils libmagic uv \
  && uv tool install --allow-python-downloads --python 3.11 dotdrop \
  && git clone https://github.com/shokinn/.files ~/.files \
  && ~/.local/bin/dotdrop --cfg=~/.files/config.yaml install
```

### Manual

1. Install [Homebrew](https://brew.sh/)
2. Install `coreutils`, `libmagic` and `uv` via Homebrew.
3. Install `drotdrop` via `uv` (`uv tool install --allow-python-downloads --python 3.11 dotdrop`).
4. Clone dotfiles, install dependencies for dotdrop and install dotfiles.  
```shell
git clone https://github.com/shokinn/.files ~/.files \
&& ~/.local/bin/dotdrop --cfg=~/.files/config.yaml install
```

## Documentation

~~Maybe you should [take a look to my documentation](https://docs.pphg.tech/) to understand how I use my dotfiles.~~
My documentation is currently quite outdated and should not be considered for help.
