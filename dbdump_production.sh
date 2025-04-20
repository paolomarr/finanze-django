#!/bin/bash

# DEFAULTS
PRODUCTION_CONTAINER_NAME=${PRODUCTION_CONTAINER_NAME:-finanze-django-db-1}
LOCAL_CONTAINER_NAME=${LOCAL_CONTAINER_NAME:-finanzeapp-db-1}

function usage() {
    cat << EOF
Usage: `basename $0` (dump|restore DUMP_FILE)
EOF
}
function error() {
    echo "[ERROR] $1" >&2
}
posidx=0
function parse_positional() {
    case $posidx in
        0) COMMAND="$1";;
        *) parse_subcommand_opt $COMMAND "$1";;
    esac
    let "posidx += 1"
}
subcommand_idx=0
function  parse_subcommand_opt() {
    local_cmd="$1"
    opt="$2"
    case $local_cmd in
        dump) 
            error "Unknown option for command $local_cmd"
            usage
            exit 1 
            ;;
        restore)
            case "$subcommand_idx" in
                0) DUMP_FILE="$opt";;
                *) error "Too many parameters for command $local_cmd"; usage; exit 1;;
            esac
            ;;
    esac
    let "subcommand_idx += 1"
}
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v) VERBOSE=1;;
        -c|--container-name)CONTAINER_NAME="$2"; shift;;
        -*) error "Unknown option $1"; usage; exit 1;;
        *) parse_positional "$1";;
    esac
    shift
done
# docker exec -it finanze-django-db-1 pg_dump --data-only --inserts --column-inserts -U postgres postgres > $OUTPUT

if [[ -n "$VERBOSE" ]]; then
    set -x
fi

if [[ -n "$CONTAINER_NAME" ]]; then # whatever the command (dump/restore), override both the related names
    PRODUCTION_CONTAINER_NAME=$CONTAINER_NAME
    LOCAL_CONTAINER_NAME=$CONTAINER_NAME
fi

case "$COMMAND" in
    dump)
        DATE=`date "+%Y%m%d"`
        OUTPUT=/tmp/finanze_db.$DATE.tar

        docker exec -it $PRODUCTION_CONTAINER_NAME pg_dump -c -C -F t -U postgres postgres -f $OUTPUT
        docker cp $PRODUCTION_CONTAINER_NAME:$OUTPUT $OUTPUT

        echo $OUTPUT >&2
        ;;
    restore)
        [[ -f $DUMP_FILE ]] || {
            error "Invalid dump file path: $DUMP_FILE"
            exit 1
        }
        DEST=/tmp/`basename $DUMP_FILE`
        docker cp $DUMP_FILE $LOCAL_CONTAINER_NAME:$DEST
        docker exec -it $LOCAL_CONTAINER_NAME pg_restore -d postgres -U postgres -c $DEST
        ;;
    *)
        error "Unknown command $COMMAND".
        usage
        exit 1
        ;;
esac

