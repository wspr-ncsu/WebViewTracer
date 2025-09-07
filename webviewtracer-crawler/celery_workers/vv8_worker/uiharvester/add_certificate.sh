subjectHash=`openssl x509 -inform DER -subject_hash_old -in burp.der | head -n 1`
openssl x509 -in burp.der -inform DER -outform PEM -out $subjectHash.0

echo $subjectHash.0
chmod +x cert14.sh

adb push $subjectHash.0 /data/local/tmp
adb push cert14.sh /data/local/tmp

adb shell "su -c './data/local/tmp/cert14.sh'"