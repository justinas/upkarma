#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
KD="$DIR/../karma_design"

# binary name differs between distros
yui() {
    (which yui-compressor 2> /dev/null && yui-compressor $@) \
        || yuicompressor $@
}

echo "Building CSS"
if [ "$1" == "full" ]
then
    # things that rarely change
    lessc $KD/less/bootstrap.less > $KD/static/bootstrap.css
    lessc $KD/less/responsive.less > $KD/static/bootstrap-responsive.css
    lessc $KD/less/styler.less > $KD/static/styler.css

    yui $KD/static/bootstrap.css > $KD/static/bootstrap.min.css
    yui $KD/static/bootstrap-responsive.css > $KD/static/bootstrap-responsive.min.css
fi

lessc $KD/less/upkarma.less > $KD/static/upkarma.css
