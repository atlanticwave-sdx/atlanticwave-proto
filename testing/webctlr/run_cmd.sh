URL=$1
POST_URL=$2
COOKIES=$3
CHANGED_VAL=$4


CURL_BIN="curl -s -c $COOKIES -b $COOKIES -e $URL"

#echo  "Django Auth: get csrftoken ..."
#echo  "    $CURL_BIN $URL"
$CURL_BIN $URL > /dev/null
DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | sed 's/^.*csrftoken\s*//')"

#echo  " do something while logged in ..."
#echo  "    $CURL_BIN -d \"$DJANGO_TOKEN&$CHANGED_VAL\" -X POST $POST_URL"

$CURL_BIN \
    -d "$DJANGO_TOKEN&$CHANGED_VAL" \
    -X POST $POST_URL

rm $COOKIES
