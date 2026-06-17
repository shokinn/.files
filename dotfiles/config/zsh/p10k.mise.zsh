#
# {{@@ header() @@}}
#

# Powerlevel10k prompt segments for mise
# [Feature request: add segment for mise](https://github.com/romkatv/powerlevel10k/issues/2212)
# Source: https://github.com/2KAbhishek/dots2k/blob/main/config/zsh/prompt/p10k.mise.zsh
# Usage in ~/.zshrc:
#   [[ -f ~/.config/zsh/p10k.mise.zsh ]] && source ~/.config/zsh/p10k.mise.zsh

() {
  function prompt_mise() {
    local plugins=("${(@f)$(mise ls --current --offline 2>/dev/null | awk '!/\(symlink\)/ && $3!="~/.tool-versions" && $3!="~/.config/mise/config.toml" && $3!="(missing)" {if ($1) print $1, $2}')}")
    local plugin

    for plugin in "${plugins[@]}"; do
      local parts=("${(@s/ /)plugin}")
      local tool_raw="${parts[1]}"
      local version="${parts[2]}"

      [[ -z "$tool_raw" || -z "$version" ]] && continue

      # P10k segment state/icon names must be zsh-identifier-safe.
      # Example: aqua:raviqqe/muffet -> AQUA_RAVIQQE_MUFFET
      local tool="${(U)tool_raw}"
      tool="${tool//[^A-Z0-9_]/_}"

      p10k segment -r -i "${tool}_ICON" -s "$tool" -t "$version"
    done
  }

  # Colors
  typeset -g POWERLEVEL9K_MISE_BACKGROUND=1

  typeset -g POWERLEVEL9K_MISE_DOTNET_CORE_BACKGROUND=93
  typeset -g POWERLEVEL9K_MISE_ELIXIR_BACKGROUND=129
  typeset -g POWERLEVEL9K_MISE_ERLANG_BACKGROUND=160
  typeset -g POWERLEVEL9K_MISE_FLUTTER_BACKGROUND=33
  typeset -g POWERLEVEL9K_MISE_GO_BACKGROUND=81
  typeset -g POWERLEVEL9K_MISE_HASKELL_BACKGROUND=99
  typeset -g POWERLEVEL9K_MISE_JAVA_BACKGROUND=196
  typeset -g POWERLEVEL9K_MISE_JULIA_BACKGROUND=34
  typeset -g POWERLEVEL9K_MISE_LUA_BACKGROUND=33
  typeset -g POWERLEVEL9K_MISE_NODE_BACKGROUND=34
  typeset -g POWERLEVEL9K_MISE_PERL_BACKGROUND=33
  typeset -g POWERLEVEL9K_MISE_PHP_BACKGROUND=93
  typeset -g POWERLEVEL9K_MISE_POSTGRES_BACKGROUND=33
  typeset -g POWERLEVEL9K_MISE_PYTHON_BACKGROUND=33
  typeset -g POWERLEVEL9K_MISE_RUBY_BACKGROUND=196
  typeset -g POWERLEVEL9K_MISE_RUST_BACKGROUND=208
  typeset -g POWERLEVEL9K_MISE_AQUA_RAVIQQE_MUFFET_BACKGROUND=33

  # Substitute the default asdf prompt element
  typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=("${POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS[@]/asdf/mise}")
}
