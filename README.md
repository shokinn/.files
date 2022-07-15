# ShokiNNs dotfiles

I manage my dotfiles using [dotdrop](https://github.com/deadc0de6/dotdrop).

## How to install

1. Install [Homebrew](https://brew.sh/)
2. Install `coreutils` via Homebrew.
3. Install [pyenv](https://github.com/pyenv/pyenv)
4. Install the latest python version via pyenv
5. Configure the latest python version as system (global) default
6. Clone dotfiles, install dependencies for dotdrop and install dotfiles.  
```shell
git clone https://github.com/shokinn/.files ~/.files \
&& cd ~/.files \
&& git submodule update --init \
&& cd .. \
&& pip install --user -r ~/.files/dotdrop/requirements.txt \
&& eval $(grep -v "^#" ~/.files/.env.public) ~/.files/dotdrop.sh install
```

## Documentation

~~Maybe you should [take a look to my documentation](https://docs.pphg.tech/) to understand how I use my dotfiles.~~
My documentation is currently quite outdated and should not be considered for help.
