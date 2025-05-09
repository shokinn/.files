# ShokiNNs dotfiles

I manage my dotfiles using [dotdrop](https://github.com/deadc0de6/dotdrop).

## How to install

### Script

```shell
[[ ! $(command -v brew) ]] && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
  ; brew update \
  && git clone https://github.com/shokinn/.files ~/.files \
  && brew bundle install --file=~/.files/misc/bootstrap.Brewfile \
  && sudo sh -c "echo \"/opt/homebrew/bin/zsh\" >> /etc/shells" \
  && chsh -s /opt/homebrew/bin/zsh \
  && uv tool install --allow-python-downloads --python 3.11 dotdrop \
  && echo "Enter profile name (leave empty for default): " \
  && read DOTDROP_PROFILE \
  && [[ -n ${DOTDROP_PROFILE} ]] && DOTDROP_PROFILE="-p ${DOTDROP_PROFILE}" || DOTDROP_PROFILE="" \
  && ~/.local/bin/dotdrop ${DOTDROP_PROFILE} --cfg=~/.files/config.yaml install \
  ; unset DOTDROP_PROFILE \
  && brew bundle install --file=~/.files/misc/Brewfile \
  && ${SHELL}
```

### Manual

1. Install [Homebrew](https://brew.sh/)
2. Install `coreutils`, `fzf`, `libmagic`, `mas`, `uv` and `zsh` via Homebrew.  
   ```shell
   brew bundle install --file=~/.files/misc/bootstrap.Brewfile
   ```
3. Install `drotdrop` via `uv` (`uv tool install --allow-python-downloads --python 3.11 dotdrop`).
4. Clone dotfiles, install dependencies for dotdrop and install dotfiles.  
   ```shell
   git clone https://github.com/shokinn/.files ~/.files \
   && ~/.local/bin/dotdrop --cfg=~/.files/config.yaml install
   ```
5. Install my default set of tools:  
   ```shell
   brew bundle install --file=~/.files/misc/Brewfile
   ```

## Documentation

~~Maybe you should [take a look to my documentation](https://docs.pphg.tech/) to understand how I use my dotfiles.~~
My documentation is currently quite outdated and should not be considered for help.
