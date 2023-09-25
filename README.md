**conjugarfrase.py** <br>
script de python que permite solo conjugar verbos. <br>
**conjugarfrase2.py** <br>
script de python que permite conjugar verbos y ajustar la concordancia de genero y número de la frase. <br>
**conjugarfrase3.py** <br>
script de python que permite conjugar verbos y ajustar la concordancia de genero y número de la frase. <br>
Versión 20230306 <br>
Esta versión soluciona algunos problemas encontrado sen conjugarfrase2.py <br>
**conjugarfrasev1.py** <br>
script de python que permite conjugar verbos y ajustar la concordancia a los sustantivos <br>
**conjugarfrasev2.py** <br>
mejoras sobre la versión v1 con el tratamiento de gerundios <br>
**conjugarfrasev3.py** <br>
mejoras sobre la versión v2 con el tratamiento de verbos conjugados, quita el punto final y devuelve todo en mayúsculas si la entrada estaba toda en mayúsculas <br>
**conjugarfrasev4.py** <br>
mejoras sobre la versión v3 con la inclusión de frases hechas y la conjugación de frases interrogativas tipo  <br>
QUIÉN + VERBO <br>
QUIÉNES + VERBO <br>
QUÉ/DÓNDE/CÓMO/CUÁNTOS/POR QUÉ + VERBO + PRONOMBRE <br>
**conjugarfrasev5.py** <br>
mejoras sobre la versión v4. El analizador morfológico ha sido entrenado con escritura normal (mayúsculas y minúsculas). Ahora todas las palabras se pasan a minúsuculas lo que provoca ciertos errores con verbos conjugados y nombres propios que se etiquetan como verbos. Esta versión intenta resolver este problema.  <br>
**conjugarfrasev6.py** <br>
mejoras sobre la versión v5. No conjuga verbos después de querer, p.p 'yo quiero correr' y no pone punto al final de la frase  <br>
**conjugarfrasev7.py** <br>
mejoras sobre la versión v6. Se solucionan ciertos errores del lematizador, p.e. "dios ser grande", la palabra "dios" la etiqueta como interjección. Ahora si no va con los símbolos le asigna nombre propio. También se ha solucionado oraciones reflexivas afirmativas y negativas " yo saber lo" 
 se flexiona "yo lo sé" o "yo no saber lo" se flexiona "yo no lo sé"
**nombresfemeninos.csv** <br>
fichero con el listado de nombres femeninos utilizados para detectar el género (sacado de la web del ine) <br>
**nombresmasculinos.csv** <br>
fichero con el listado de nombres masculinos utilizados para detectar el género (sacado de la web del ine) <br>
**es_verbs.txt** <br>
este fichero pertenece al paquete pattern. Se ha modificado con la conjugación de algunos verbos irregulares. <br>
Tiene que sustituir al existente en el directorio pythonX.X\site-packages\pattern\text\es <br>
<br>
**Requerimientos** <br>
flask <br>
pattern2.6 <br>
freeling 4.2 <br>
