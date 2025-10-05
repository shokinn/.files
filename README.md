# ShokiNNs dotfiles

I manage my dotfiles using [dotdrop](https://github.com/deadc0de6/dotdrop).

## How to install

### Script

> [!IMPORTANT]  
> Copy ssh public/private key for age, to encrypt/decrypt files to `~/.age/phg-age-dotfiles` and `~/.age/phg-age-dotfiles.pub`
> Otherwise empty files will be created instead.

```shell
[[ ! $(command -v brew) ]] && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" \
  ; eval "$(/opt/homebrew/bin/brew shellenv)" \
  && brew update \
  && git clone https://github.com/shokinn/.files ~/.files \
  && brew bundle install --file=~/.files/bootstrap/Brewfile \
  && sudo sh -c "echo \"/opt/homebrew/bin/zsh\" >> /etc/shells" \
  && chsh -s /opt/homebrew/bin/zsh \
  && uv tool install --allow-python-downloads --python 3.11 dotdrop \
  && echo "Enter profile name (leave empty for default): " \
  && read DOTDROP_PROFILE \
  && [[ -n ${DOTDROP_PROFILE} ]] && DOTDROP_PROFILE="-p${DOTDROP_PROFILE}" || DOTDROP_PROFILE="" \
  && ~/.local/bin/dotdrop ${DOTDROP_PROFILE} --cfg=~/.files/config.yaml install \
  ; unset DOTDROP_PROFILE \
  && export HOMEBREW_CASK_OPTS="--appdir=${HOME}/Applications" \
  && brew bundle install --file=~/.files/config/brew/Brewfile \
  && mkdir -p ~/workspace/{privat,work} \
  && ${SHELL} -c ~/.files/bootstrap/.macos \
  && ${SHELL}
```

### Manual

1. Install [Homebrew](https://brew.sh/)
2. Install `age`, `coreutils`, `fzf`, `libmagic`, `mas`, `uv` and `zsh` via Homebrew.  
   ```shell
   brew bundle install --file=~/.files/bootstrap/Brewfile
   ```
3. Install `drotdrop` via `uv` (`uv tool install --allow-python-downloads --python 3.11 dotdrop`).
4. Copy ssh public/private key for age, to encrypt/decrypt files to `~/.age/phg-age-dotfiles` and `~/.age/phg-age-dotfiles.pub`
5. Clone dotfiles, install dependencies for dotdrop and install dotfiles.  
   ```shell
   git clone https://github.com/shokinn/.files ~/.files \
   && ~/.local/bin/dotdrop --cfg=~/.files/config.yaml install
   ```
6. Install my default set of tools:  
   ```shell
   brew bundle install --file=~/.files/config/brew/Brewfile
   ```

## Encrypted files

### Initially import a dot file as encrypted file

```shell
dotdrop import --transw=_encrypt --transr=_decrypt <file>
```

Installs/updates will now be automatically decrypted/encrypted.

### Decrypt a dotfile manually

```shell
age --decrypt -i ~/.age/phg-age-dotfiles -o <ouput paht for decrypted file> <path to encrypted file>
```

### Encrypt a dotfile manually

```shell
cat <path to plain file> | age -a -R ~/.age/phg-age-dotfiles.pub > <path to encrypted file>
```

### Edit an encrypted dotfile

1. Install [age-edit](https://github.com/dbohdan/age-edit)

#### Manual command

**Default editor:**

```shell
age-edit -t /tmp/ -M -a ~/.age/phg-age-dotfiles <path to file to edit>
```

**VS Code as editor:**

```shell
age-edit -e "${HOME}/.local/bin/codew" -t /tmp/ -M -a ~/.age/phg-age-dotfiles <path to file to edit>
```

#### Aliases for file editing

- `ade` uses the default editor
- `cade` uses vs code for editing the file

Both aliases are configured via my `.zshrc`.

## Backup/Restore settings for macOS native user preferences

See here for a defaults documentation: <https://macos-defaults.com/>

### App list

| App    | Domain                                      |
| ------ | ------------------------------------------- |
| Alfred | `com.runningwithcrayons.Alfred-Preferences` |
| Ice    | `com.jordanbaird.Ice`                       |
| Moom   | `com.manytricks.Moom`                       |

### Backup settings

```shell
defaults export <domain> ~/.files/config/plist/<app>.plist
```

### Restore settings

```shell
defaults import <domain>  ~/.files/config/plist/<app>.plist
```

## Documentation

~~Maybe you should [take a look to my documentation](https://docs.pphg.tech/) to understand how I use my dotfiles.~~
My documentation is currently quite outdated and should not be considered for help.
