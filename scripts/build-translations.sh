# Loop through lines in LINGUAS file and generate .po files for each language
while read -r line
do
  mkdir -p ./zapzap/po/${line}/LC_MESSAGES/
  # create template POT
  xgettext --from-code=UTF-8 --keyword=_ --output=./zapzap/po/zapzap.pot --files-from=./zapzap/po/POTFILES
  # See if file already exists
  if [ -f ./zapzap/po/${line}/LC_MESSAGES/zapzap.po ] 
  then
    echo "Skipping ${line}"
    # update PO file
    msgmerge -o ./zapzap/po/${line}/LC_MESSAGES/zapzap.po ./zapzap/po/${line}/LC_MESSAGES/zapzap.po ./zapzap/po/zapzap.pot
  else
    echo "Generating ${line}"
    # create PO file
    xgettext --from-code=UTF-8 --keyword=_ --output=./zapzap/po/${line}/LC_MESSAGES/zapzap.po --files-from=./zapzap/po/POTFILES
  fi
  # create MO
  msgfmt ./zapzap/po/${line}/LC_MESSAGES/zapzap.po -o ./zapzap/po/${line}/LC_MESSAGES/zapzap.mo
done < ./zapzap/po/LINGUAS