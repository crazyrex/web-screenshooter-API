#!/usr/bin/env bash

. progressbar.sh

BACKEND="http://foo.sockhost.net:1448"

if [[ "$3" == "-o" ]] && [[ ! -z "$4" ]];
then
    output="$4"
else
    output="screenshot.png"
fi

function capture_web_screen
{
    web_url="$1"
    output="$2"
    curl -s -X -k POST "${BACKEND}/web-screenshot/make" -X PUT -d '{"url": "'"${web_url}"'"}' > "${output}"
}

function batch_captures
{
    json_file="$1"
    output="$2"
    batch_id=$(curl -s -X -k POST "${BACKEND}/web-screenshot/batch" -X POST -d @"${json_file}" | jq '.["batch_id"]')
    echo "Started batch with ID ${batch_id}"

    preparebar 25 "#"

    completion_progress=0
    is_zipped=0

    while [[ "${completion_progress}" != "100" ]];
    do
        status=$(curl -s -X GET "$BACKEND/web-screenshot/batch/${batch_id}/status")
        completion_progress=$(echo "${status}" | jq '.["percentage_completed"]')
        progressbar ${completion_progress} 100
        sleep 0.2
    done
    echo ""
    echo -e "Backend finished getting screenshots, now it is zipping the results\c"
    while [[ "$is_zipped" == "0" ]];
    do
        status=$(curl -s -X GET "$BACKEND/web-screenshot/batch/${batch_id}/status")
        is_zipped=$(echo "${status}" | jq '.["is_zipped"]')
        echo -e ".\c"
        sleep 0.5
    done
    echo ""
    echo "Done. Retrieving the zip file..."
    curl -X GET "$BACKEND/web-screenshot/batch/${batch_id}" > "${output}"
    #curl -s -X DELETE "$BACKEND/web-screenshot/batch/${batch_id}"
    echo "Finished"
}

case $1 in
    capture)
      web_url="$2"
      echo "Capturing screen of ${web_url}..."
      capture_web_screen "${web_url}" "${output}"
      echo "Done. Saved in ${output}"
      ;;
    batch)
      web_urls_json_file="$2"
      echo "Capturing screen of URLs from JSON file ${web_urls_json_file}..."
      batch_captures "${web_urls_json_file}" "${output}"
      echo "Done. Saved in ZIP format inside ${output}"
      ;;
      *)
      echo "Usage: webscreen capture https://www.google.com/ -o image.png"
      echo "Usage: webscreen batch json_urls_file -o images_result.zip"
esac

