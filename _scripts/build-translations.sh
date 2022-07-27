# Loop through lines in LINGUAS file and generate .po files for each language
while read -r line
do
  # será criado apenas para colocar os .mo
  mkdir -p ./zapzap/po/${line}/LC_MESSAGES/
  # create template POT
  xgettext --from-code=UTF-8 --keyword=_ --output=./po/zapzap.pot --files-from=./po/POTFILES
  # See if file already exists
  if [ -f ./po/${line}.po ] 
  then
    echo "Skipping ${line}"
    # update PO file
    msgmerge -o ./po/${line}.po ./po/${line}.po ./po/zapzap.pot
  else
    echo "Generating ${line}"
    # create PO file
    xgettext --from-code=UTF-8 --keyword=_ --output=./po/${line}.po --files-from=./po/POTFILES
  fi
  # create MO
  msgfmt ./po/${line}.po -o ./zapzap/po/${line}/LC_MESSAGES/zapzap.mo

done < ./po/LINGUAS