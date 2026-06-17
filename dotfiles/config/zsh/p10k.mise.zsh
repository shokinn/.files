#
# {{@@ header() @@}}
#

# Powerlevel10k prompt segments for mise
# [Feature request: add segment for mise](https://github.com/romkatv/powerlevel10k/issues/2212)
# Source: https://github.com/2KAbhishek/dots2k/blob/main/config/zsh/prompt/p10k.mise.zsh
# Usage in ~/.zshrc:
#   [[ -f ~/.config/zsh/p10k.mise.zsh ]] && source ~/.config/zsh/p10k.mise.zsh

() {
  function _prompt_mise_has_visual_identifier() {
    local tool="$1"
    local icon_name="${tool}_ICON"
    local icon_override="POWERLEVEL9K_${icon_name}"
    local state_visual_identifier="POWERLEVEL9K_MISE_${tool}_VISUAL_IDENTIFIER_EXPANSION"
    local segment_visual_identifier="POWERLEVEL9K_MISE_VISUAL_IDENTIFIER_EXPANSION"
    local parameter value

    for parameter in "$state_visual_identifier" "$segment_visual_identifier" "$icon_override"; do
      if (( ${+parameters[$parameter]} )); then
        value="${(P)parameter}"
        [[ -n "$value" ]] && return 0
        return 1
      fi
    done

    if (( ${+functions[print_icon]} )); then
      [[ -n "$(print_icon "$icon_name")" ]] && return 0
    elif (( ${+functions[_p9k_init_icons]} )); then
      _p9k_init_icons
      (( ${+icons[$icon_name]} )) && [[ -n "${icons[$icon_name]}" ]] && return 0
    fi

    return 1
  }

  function _prompt_mise_fallback_label() {
    local label="${1:t}"
    label="${label##*:}"
    print -r -- "${label:-$1}"
  }

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

      if _prompt_mise_has_visual_identifier "$tool"; then
        p10k segment -r -i "${tool}_ICON" -s "$tool" -t "$version"
      else
        p10k segment -r -s "$tool" -t "$(_prompt_mise_fallback_label "$tool_raw") $version"
      fi
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
