for file in ./zapzap/view/*.ui
do
  export OUTPUT_FILE="./zapzap/view/$(echo ${file} | sed "s/.*\///" | sed "s/.ui/.py/")"
  echo "Generating ${OUTPUT_FILE}"
  python3 -m PyQt6.uic.pyuic -o $OUTPUT_FILE -x $file
  sed -i 's/_translate = QtCore.QCoreApplication.translate//g' $OUTPUT_FILE
  sed -i 's/_translate(".*", /_(/g' $OUTPUT_FILE
  sed -i '1i\from gettext import gettext as _' $OUTPUT_FILE
done