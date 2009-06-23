"""
Encryption module that uses the Java Cryptography Extensions (JCE).

This requires either JRE 1.4.2 or later, or the JCE jars installed on your classpath.

Note that in default installations of the Java Runtime Environment,
the maximum key length is limited to 128 bits due to US export
restrictions. This makes the generated keys incompatible with the ones generated by pycryptopp,
which has no such restrictions. To fix this, download the "Unlimited Strength
Jurisdiction Policy Files" from Sun, which will allow encryption using 256 bit AES keys.
"""
from javax.crypto import Cipher
from javax.crypto.spec import SecretKeySpec, IvParameterSpec

import jarray

# Initialization vector filled with zeros
_iv = IvParameterSpec(jarray.zeros(16, 'b'))

def aesEncrypt(data, key):
    cipher = Cipher.getInstance('AES/CTR/NoPadding')
    skeySpec = SecretKeySpec(key, 'AES')
    cipher.init(Cipher.ENCRYPT_MODE, skeySpec, _iv)
    return cipher.doFinal(data).tostring()


def getKeyLength():
    maxlen = Cipher.getMaxAllowedKeyLength('AES/CTR/NoPadding')
    return min(maxlen, 256) / 8
