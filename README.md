# ShokiNNs dotfiles

I manage my dotfiles using [dotdrop](https://github.com/deadc0de6/dotdrop).

## How to install

1. Install [Homebrew](https://brew.sh/)
2. Install `coreutils` via Homebrew.
3. Install [pyenv](https://github.com/pyenv/pyenv)
  a. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
  b. Add pyenv temporarly to your path: `export PATH=$(pyenv root)/shims:${PATH}`
  c. Install the latest python version via pyenv
  d. Create a new virtual-env caleld `dotdrop` via `pyenv virtualenv <just installed python verison> dotdrop`
4. Initialize pyenv; run `pyenv init` for instructions
5. Activate the `dotdrop` virtualenv by using `pyenv shell dotdrop`
6. Clone dotfiles, install dependencies for dotdrop and install dotfiles.  
```shell
git clone https://github.com/shokinn/.files ~/.files \
&& cd ~/.files \
&& git submodule update --init \
&& cd .. \
&& pip install -r ~/.files/dotdrop/requirements.txt \
&& eval $(grep -v "^#" ~/.files/.env.public) ~/.files/dotdrop.sh install
```

## Documentation

~~Maybe you should [take a look to my documentation](https://docs.pphg.tech/) to understand how I use my dotfiles.~~
My documentation is currently quite outdated and should not be considered for help.
