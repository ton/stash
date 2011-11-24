_stash()
{
    # The word that needs to be auto completed.
    cur=${COMP_WORDS[COMP_CWORD]}

    # Previous word on the command line, needs to be a stash switch.
    prev=${COMP_WORDS[COMP_CWORD-1]}

    # All command line options that can be auto completed.
    opts=( -r --remove -s --show -a --apply )

    case "${opts[@]}" in *"${prev}"*)
        patches=`ls $HOME/.patches/`
        COMPREPLY=( $(compgen -W "${patches}" -- ${cur}) )
        return 0
    esac
}

complete -F _stash stash
complete -F _stash stash.py
