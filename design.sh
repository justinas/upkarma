#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
KD="$DIR/karma_design"

echo "Building CSS"
if [ "$1" == "full" ]
then
    # things that rarely change
    (lessc $KD/less/bootstrap.less > $KD/static/bootstrap.css && \
    lessc $KD/less/responsive.less > $KD/static/bootstrap-responsive.css && \
    lessc $KD/less/styler.less > $KD/static/styler.css) || echo "failure!" && exit 1
    (yui-compressor $KD/static/bootstrap.css > $KD/static/bootstrap.min.css && \
    yui-compressor $KD/static/bootstrap-responsive.css > $KD/static/bootstrap-responsive.min.css) \
    || echo "failure!" && exit 1
fi

lessc $KD/less/upkarma.less > $KD/static/upkarma.css || (echo "failure!" && exit 1)


echo "Collecting static"
$DIR/manage.py collectstatic --noinput
