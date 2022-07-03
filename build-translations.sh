# Loop through lines in LINGUAS file and generate .po files for each language
while read -r line
do
  mkdir -p ./zapzap/locales/${line}/LC_MESSAGES/
  # create template POT
  xgettext --from-code=UTF-8 --keyword=_ --output=./zapzap/locales/${line}/LC_MESSAGES/zapzap.pot --files-from=./zapzap/locales/POTFILES
  # See if file already exists
  if [ -f ./zapzap/locales/${line}/LC_MESSAGES/zapzap.po ] 
  then
    echo "Skipping ${line}"
    # update PO file
    msgmerge -o ./zapzap/locales/${line}/LC_MESSAGES/zapzap.po ./zapzap/locales/${line}/LC_MESSAGES/zapzap.po ./zapzap/locales/${line}/LC_MESSAGES/zapzap.pot
  else
    echo "Generating ${line}"
    # create PO file
    xgettext --from-code=UTF-8 --keyword=_ --output=./zapzap/locales/${line}/LC_MESSAGES/zapzap.po --files-from=./zapzap/locales/POTFILES
  fi
  # create MO
  msgfmt ./zapzap/locales/${line}/LC_MESSAGES/zapzap.po -o ./zapzap/locales/${line}/LC_MESSAGES/zapzap.mo
done < ./zapzap/locales/languages