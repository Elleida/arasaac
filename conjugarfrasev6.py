# import flask to get the request data
from flask import Flask, request 
import pyfreeling

from pattern.es import conjugate,PRETERITE, PRESENT, FUTURE, IMPERFECT, SG, PL, PROGRESSIVE, INDICATIVE, SUBJUNCTIVE
from pattern.es import MALE, FEMALE, NEUTRAL, PLURAL , FEMININE, MASCULINE, SINGULAR


VOCALES = ("a", "e", "i", "o", "u")
is_vowel = lambda ch: ch in VOCALES
def normalize(vowel):
    return {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}.get(vowel, vowel)

def quitar_tildes(palabra):
    return "".join([normalize(vowel) for vowel in palabra])

pronombres = {
        'yo': [1, SG],
        'tú': [2, SG],
        "él": [3, SG],
        "ella": [3, SG],
        "usted": [3, SG],
        "nosotros": [1, PL],
        "vosotros": [2, PL],
        "ellos": [3, PL],
        "ellas": [3, PL],
        "ustedes": [3, PL],
        "todo": [3, PL],
        "me": [1, SG],
        "te": [2, SG],
        "lo": [3, SG],
        "le": [3, SG],
        "nos": [1, PL],
        "os": [2, PL],
        "les": [3, PL]
    }

presente=["hoy","actualmente","ahora","ya"]

pasado=["ayer","pasado","anterior","anteayer","anoche"]

pasado_imperfecto=["antes"]

futuro=["pasado mañana","mañana","futuro","próximo",'después']

verbos3p=["llover",'nevar', 'granizar', 'nublar', 'oscurecer', 'diluviar', 'lloviznar', 'tronar', 'relampaguear']

verboscopulativos=['ser','estar','parecer']

verbosconjugados=['querer']

verbosgerundios=['estar','ir','seguir','llevar','andar','venir','continuar']

verbossubjuntivos=['desear','admirar','esperar','doler','celebrar','perdonar','disfrutar','dudar','sentir','temer','buscar','dejar','hacer','querer','rogar','exigir','rogar','mandar','pedir']

atonicafemeninos=['acta','alma','águila','agua','arte','ala','arma','aula','habla','aula','hada','hambre','África','Asia',
                  'ágora','alga','álgebra','alza','ama','anca','ancla','ánfora','ánima','ansia','arca','área','arpa','asma',
                  'asta','Austria','aya','haba','hampa','haya']
perifrasis=['tener que','haber que']

subjuntivos=['aunque','como']#,'que','si']

oracionesfinales=['para que', 'de que']

verbosexcepciones=['ser','haber']

conjuncion3p=['pero']

conjuncionestemporalespresente=['mientras','cuando']

fraseshechas=['cómo estás','es una tontería','lo siento','me gusta','no me gusta','te quiero',
        'no lo sé','no lo entiendo','cuántos años cumples','cuántos años tienes',
        'dónde vives','dónde vas','qué te gusta','cómo es tu familia',
        'tienes animales','qué te gusta ver en la tele','qué aficiones tienes',
        'qué música te gusta','qué deporte te gusta','cuál es tu comida favorita',
        'cuál es tu color preferido','qué hace','qué haces','qué dice','qué dices'
        ]
fraseshechascontinua=['para qué sirve','sirve para']

def Analizador():

    print('Init models')   
    

# inicilizamos freeling
#    DATA = "/usr/local"+"/share/freeling/"
    DATA = "/usr"+"/share/freeling/"
# Init locales
    pyfreeling.util_init_locale("default")

# create options set for maco analyzer. Default values are Ok, except for data files.
    LANG="es"
    op= pyfreeling.maco_options(LANG)
    op.set_data_files( "", 
                   DATA + "common/punct.dat",
                   DATA + LANG + "/dicc.src",
                   DATA + LANG + "/afixos.dat",
                   "",
                   DATA + LANG + "/locucions.dat", 
                   DATA + LANG + "/np.dat",
                   DATA + LANG + "/quantities.dat",
                   DATA + LANG + "/probabilitats.dat")

# create analyzers
    tk=pyfreeling.tokenizer(DATA+LANG+"/tokenizer.dat")
    sp=pyfreeling.splitter(DATA+LANG+"/splitter.dat")
    mf=pyfreeling.maco(op)
# create tagger
    tagger = pyfreeling.hmm_tagger(DATA + LANG +"/tagger.dat",True,2)

# activate morpho modules to be used in next call

    mf.set_active_options (False,  # UserMap 
                          True,  # NumbersDetection,  
                          True,  # PunctuationDetection,   
                          False,  # DatesDetection,    
                          True,  # DictionarySearch,  
                          True,  # AffixAnalysis,  
                          False, # CompoundAnalysis, 
                          True,  # RetokContractions,
                          True,  # MultiwordsDetection,  
                          True,  # NERecognition,     
                          False, # QuantitiesDetection,  
                          True); # ProbabilityAssignment     

 
    return tk,sp,mf,tagger

def leer_nombres():
    nombresf=[]
    nombresm=[]
    with open('nombresfemeninos.csv', 'r') as f:
        for line in f:
            nombresf.append(line.replace(' ','_').lower().strip())
    with open('nombresmasculinos.csv', 'r') as f:
        for line in f:
            nombresm.append(line.replace(' ','_').lower().strip())
    return nombresm,nombresf

def lematiza(tk,sp,mf,tagger,texto):
    l = tk.tokenize(texto)
    ls = sp.split(l)
    ls = mf.analyze(ls)	
    ls = tagger.analyze(ls)
    data=[]
    lemas=''
    for s in ls :
        ws = s.get_words()
        lemas=' '.join([w.get_lemma() for w in ws ])
    for w in ws:
        if w.get_lemma() in verbosexcepciones:
            tag='VSN0000'
        else:
            tag=w.get_tag()
        lema=w.get_lemma()
#        if tag[0]=='V' and tag[3]!='0':
#            tag=tag[0:2]+'N0000'
#            data.append([lema,lema,tag])
#        else:
        data.append([w.get_form().replace('_',' '),lema,tag])
    return ls,lemas,data

def get_pronombre(data,pi,p):
    out=[1,SG]
    pout=-1
    np=0
    for pos,item in enumerate(data):
        if pos >= pi and pos <= p:
            if 'PP' in item[2]: 
                pro=pronombres[item[1]]
                if pout>-1:
                    if pro[0]==1:
                        out=pro
                    if pro[0]==2 and out[0]==3:
                        out=pro
                else:
                    out=pro
                pout=pos
                np=np+1
    if np>1:
        out[1]=PL
    return out,pout

def get_preposicion(data,pi,pf):
    out=[]#pf
    n=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if pi>0 and 'SP' in item[2][0:2]: 
                out.append(pos)
                n=False
            if 'N' in item[2][0] or 'VMG' in item[2][0:3]: 
                n=True
            if n and 'SP' in item[2][0:2]: 
                out.append(pos)
#                return pos
    out.append(pf)
    return out

def get_conjuncionsubordinante(data,pi,pf):
    out=[]#pf
    n=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if 'CS' in item[2]: 
                out.append(pos)
                return out
    return out

def get_verbo(data,pi,p):
#    fp=0
    nv=0
    vc=0
    posv=0
    ritem=[]
    for pos,item in enumerate(data):
        if pos >= pi and pos <=p:
#            if item[2][0]=='F':
#                fp=fp+1
            if any(x in item[1] for x in verbosconjugados):
                posv=pos
                vc=1
                ritem=item
            if 'VM' in item[2][0:2] and nv==0 and vc==0 and item[2][2]!='P':
                nv=nv+1
                posv=pos
                ritem=item
            if (('VM' in item[2]) or ('VS' in item[2]) or ('VA' in item[2])) and (item[2][3:7]=='0000'): # and (nv==0):
                if vc==1:
                    return ritem[1],posv
                else:
                    return item[1],pos#-fp
#  a veces el verbo no está marcado como tal, por ejemplo en oraciones 
#  con verbos copulativos
            if any(x in item[1] for x in verboscopulativos):
                return item[1],pos#-fp
    if nv>0:
        return ritem[1],posv
    return '',-1

def get_sujetointerrogativa(data,pi,pf):

    out=[3,SG]
    if data[pi][2][0]=='F':
        pi=pi+1
    if data[pi][2][0:2]=='SP':
        pi=pi+1
    pos0=pi+2
    if data[pi+2][2]!='Fp':
        if data[pi+1][2][0:1]=='V':
            if data[pi+2][2][0:2]=='PP':
                out[0]=int(data[pi+2][2][2])
                if data[pi+2][2][4] =='P':
                    out[1]=PL
            elif data[pi][2][0:2]=='PT' and data[pi][2][4]=='P':
                out[1]=PL
        if data[pi+1][2][0:2]=='PP':
            out[0]=int(data[pi+1][2][2])
            if data[pi+1][2][4] =='P':
                out[1]=PL
    else:
        if data[pi][2][4]=='P':
            out[1]=PL
    return out,pos0

def get_sujeto(data,pi,p,debug=False):
    out=[1,SG]
    pos0=-1
    pout=-1
    ns=0
    nc=0
    np=0
    ndet=False
    nd='N'
    nums='N'
    for pos,item in enumerate(data):
        if pos >= pi and pos <= p:
            if ('CC' in item[2][0:2]):
                nc=nc+1
            if 'D' in item[2][0]:
                nd=item[2][4]
                ndet=True
            if ndet and (('VM' in item[2][0:3]) or ('AQ' in item[2][0:2])):
                out[0]=3
                pos0=pos
            if ('NP' in item[2][0:2]) or ('NC' in item[2][0:2]):
                ns=ns+1
                if np==0:
                    if 'P' in item[2][2:]:
                        out=[3, PL]
                        pos0=pos
                    else:
                        out=[3, SG]
                        pos0=pos   
                nums=item[2][3]        
            if 'PP' in item[2][0:2] or 'PI' in item[2][0:2]:
                pro=pronombres[item[1]]
                if pout>-1:
                    if pro[0]==1:
                        out=pro
                    if pro[0]==2 and out[0]==3:
                        out=pro
                else:
                    out=pro
                pout=pos
                np=np+1      
            if 'Z' in item[2][0]:
                if item[1]!='1':
                    out=[3,PL]
                else:
                    out=[3,SG]
                pos0=pos       
            if 'SP' in item[2][0:2] and (ns>0 or np>0):
                return out,pos0
      
    if pout>pos0:
        pos0=pout
    if (ns>1)and(nc>0):
        out=[3,PL]    
    if np>1:
        out[1]=PL
    if np==1 and ns>=1 and nc>0: #ns>=1
        out[1]=PL
    if nums=='N' and nd!='N':
        out[1]=PL
        if nd=='S':
            out[1]=SG
    return out,pos0

def get_numerofrases(data):
    nf=1
    pf=0
    pp=-1
    pi=0
    p=[]
    comma=False
    fs=False

    for pos,item in enumerate(data):
        if 'CS' in item[2][0:2] and pos>0:
            pf=4
            if comma:
                pp=pos-1
            else:
                pp=pos+1
            fs=True
        if (pf==0) and ('V' in item[2][0]):
            pf=1
        if (pf==1) and ('C' in item[2][0]):
            pf=2
            pp=pos
        if (pf==1) and (('P' in item[2][0])):# or ('S' in item[2][0])):
            pf=2
            pp=pos+1#-1
        # comentado porque crea problemas, p.e. el coche ser muy grande pero la perdíz ser rojo.
        # muy es "RG", corta la frase ahí y la siguiente como aun un pero "CC" la detecta como sujeto
        # múltiple y rojo pasa a ser plural.
#        if (pf==1) and ('R' in item[2][0]):
#            pf=2
#            pp=pos

        if ('Fc' in item[2][0:2]) and (pf==1):
            pf=2
            pp=pos
            comma=True

        if (pf==2) and ('V' in item[2][0]):
            pf=3

        if pf>=3:
            nf=nf+1
            if pf==4:
                pf=0
            else:
                pf=1
            p.append((pi,pp-1))
            if comma:# or fs:
                pi=pp+1
            else:
                pi=pp
            comma=False
            fs=False

    p.append((pi,pos))
    return p,nf

def nombre_compuesto(data,p):
    posv=p
    for pos,item in enumerate(data):
        if pos < p:
            posv=posv+item[1].count('_')
    return posv

def get_tiempo(data,pi,pf):
    tiempo=PRESENT
    textlem=' '.join(x[0].lower() for x in data[pi:pf+1]) 
    if any(x in textlem for x in futuro):
        tiempo=FUTURE
    if any(x in textlem for x in pasado) and (tiempo==PRESENT):
        tiempo=PRETERITE
    if any(x in textlem for x in pasado_imperfecto) and (tiempo==PRESENT):
        tiempo=IMPERFECT
    return tiempo

def get_numeroadverbiostiempo(textlem):
    na=0
    if any(x in textlem for x in presente):
        na=na+1
    if any(x in textlem for x in futuro):
        na=na+1
    if any(x in textlem for x in pasado):
        na=na+1
    if any(x in textlem for x in pasado_imperfecto):
        na=na+1   
    return na

def es_frasecopulativa(data,pi,pf):
    out=False
# en la frase copulativa solo puede haber un verbo
    nv=0
    for item in data[pi:pf]:
        if 'VM' in item[2][0:2] and 'P'!=item[2][2]:
            nv=nv+1
    if nv>1:
        return False
    textlem=' '.join(x[1] for x in data[pi:pf]) 
    if any(x in textlem for x in verboscopulativos):
        out=True
    return out

def cambia_verbo_gerundio(data,pi,pf,debug=False):
    vestar=False
    p=0
    for pos,item in enumerate(data):
        if pos >= pi and pos <=pf:

            if (not vestar and ('VMN' in item[2]) and any(x in item[1] for x in verbosgerundios)):
                vestar=True
                p=pos
            if vestar and ('VMN' in item[2]) and (pos==p+1):
                try:
                    verboconjugado=conjugate(item[1],PRESENT,mood=INDICATIVE,aspect=PROGRESSIVE)
                except:
                    verboconjugado=conjugate(item[1],PRESENT,mood=INDICATIVE,aspect=PROGRESSIVE)
                data[pos][0]=verboconjugado
                data[pos][1]=verboconjugado
                data[pos][2]="VMG0000"
    return data

def cambiageneroynumero(adjective, gender=MALE,debug=False):

    w = adjective.lower()
    # demostrativos
    if w=='este':
        if SINGULAR in gender and FEMALE in gender:   
            return 'esta'
        if PLURAL in gender and FEMALE in gender:
            return 'estas'
    if w=='ese':
        if SINGULAR in gender and FEMALE in gender:
            return 'esa'
    if w=='aquel':
        if SINGULAR in gender and FEMALE in gender:
            return 'aquella'
        if PLURAL in gender:
            if MALE in gender:
                return 'aquellos'
            if FEMALE in gender:
                return 'aquellas'
    if w=='aquellos':
        if SINGULAR in gender:
            if MALE in gender:
                return 'aquel'
            if FEMALE in gender:
                return 'aquella' 
    if w=='aquella':
        if SINGULAR in gender and MALE in gender:
            return 'aquel'
    # determinante posesivo mi - mis
    if PLURAL in gender and w=='mi':
        return 'mis'
    if SINGULAR in gender and w=='mis':
        return 'mi'
    if PLURAL in gender and w=='tu':
        return 'tus'
    if SINGULAR in gender and w=='tus':
        return 'tu'
    if PLURAL in gender and w=='su':
        return 'sus'
    if SINGULAR in gender and w=='sus':
        return 'su'
    if MALE in gender and SINGULAR in gender and w=='la':
        return 'el'
    if FEMALE in gender and SINGULAR in gender and w=='el':
        return 'la'
    if SINGULAR in gender and MALE in gender and w=='los':
        return 'el'
    if PLURAL in gender and FEMALE in gender:
        if w=='el':
            return 'las'
        if w=='los':
            return 'las'
    if PLURAL in gender and MALE in gender:
        if w=='el':
            return 'los'
        if w=='la':
            return 'los'
    if PLURAL in gender and FEMALE in gender:
        if w=='el':
            return 'las'
    if SINGULAR in gender and w=='muchas':
        return 'una'
    if SINGULAR in gender and w=='muchos':
        return 'un'
    if SINGULAR in gender and MALE in gender and (w=='una' or w=='unas' or w=='uno' or w=='unos'):  
        return 'un'
    if SINGULAR in gender and FEMALE in gender and w=='un':  
        return 'una'
    if SINGULAR in gender and w=='estos':
        return 'este'
    if PLURAL in gender and w.endswith("z"):
        return w[:-1]+"ces"
    if MALE in gender and PLURAL in gender and w.endswith("n"):
        return w[:-2]+normalize(w[-2])+"nes"
    if FEMALE in gender and PLURAL in gender and w.endswith("ón"):
        return w[:-2]+normalize(w[-2])+"nes"
    if FEMALE in gender and PLURAL in gender and w.endswith("n"):
        return w[:-2]+normalize(w[-2])+"nas"
    # normal => normales
    if PLURAL in gender and not is_vowel(w[-1:]) and not w.endswith(("es", "as", "os")):
        return w + "es"
    # chica alta  => chico alto
    if w.endswith("a"):
        if MALE in gender and PLURAL in gender:
            return w[:-1] + "os"
        if MALE in gender:
            return w[:-1] + "o"
        if PLURAL in gender:
            return w + "s"
    # el chico inteligente => los chicos inteligentes
    if PLURAL in gender and w.endswith(("a", "e")):
        return w + "s"
    # el chico alto => los chicos altos
    if w.endswith("o"):
        if FEMALE in gender and PLURAL in gender:
            return w[:-1] + "as"
        if FEMALE in gender:
            return w[:-1] + "a"
        if PLURAL in gender:
            return w + "s"
    if SINGULAR in gender:
        if w.endswith(("os", "as")):
            w = w[:-1]
    # horribles => horrible, humorales => humoral
        if w.endswith("es"):
            if len(w) >= 4 and not is_vowel(normalize(w[-3])) and not is_vowel(normalize(w[-4])):
                w=w[:-1]
            w=w[:-2]
    
    # español -> española
    if PLURAL in gender and w.endswith("ol"):
        return w[:-2] + "oles"
    if SINGULAR in gender and w.endswith("oles"):
        return w[:-4] + "ol"
    if SINGULAR in gender and FEMALE in gender and w.endswith("ol"):
        return w[:-2] + "ola"
    

    # bonitos => bonitas
    if w.endswith("os") and FEMALE in gender and PLURAL in gender:    
        w=w[:-2]+"as"
    # bonitas => bonitos
    if w.endswith("as") and MALE in gender and PLURAL in gender:    
            w=w[:-2]+"os"
    return w

def get_generodeterminante(data,pi,pf):
    g="M"
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('DA' in item[2]) or ('DD' in item[2]):
                g=item[2][3]
    return g

def get_determinantegeneroynumero(data,pi,pf):
    dgn="XX"
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if 'D' in item[2][0]:
                dgn=item[2][3:5]
    return dgn

def get_sujetogeneroynumero(data,pi,pf):
    sgn="NN"
    gen='F'
    num='X'
    nn=False
    cc=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if 'CC' in item[2][0:2] and pos>pi:
                cc=True
            if 'Z' in item[2][0]:
                if item[1]!='1':
                    num='P'
                else:
                    num='S'
            if ('NP' in item[2][0:2]) or ('NC' in item[2][0:2]):
                sgn=item[2][2:4] 
                # en frases con sujetos múltiples si hay un sujeto masculino, el género es masculino
                if sgn[0]=='M':
                    gen='M'
                # si el género es común, se toma el género del determinante   
#                if sgn[0]=='C':
#                    sgn=get_generodeterminante(data,pi,pos)+sgn[1]
                if cc:
                    sgn=sgn[0]+'P'
                nn=True
            if ('PP' in item[2][0:2]) or ('PI' in item[2][0:2]):
                sgn=item[2][3:5] 
                # en frases con sujetos múltiples si hay un sujeto masculino, el género es masculino
                if sgn[0]=='M':
                    gen='M'
                # si el género es común, se toma el género del determinante   
                if sgn[0]=='C':
                    sgn=get_generodeterminante(data,pi,pos)+sgn[1]
                if cc:
                    sgn=sgn[0]+'P'
                # si no hya nombre y se detecta un adjetivo calificativo, se toma su género y número
            if not nn and 'AQ' in item[2][0:2]:
                sgn=item[2][3:5]           
            if 'V' in item[2][0] and pos>pi:
                if num!='X':
                    sgn=sgn[0]+num
                if gen=='M':
                    sgn='M'+sgn[1]
                return sgn
    return sgn

def get_sustantivogeneroynumero(data,pi,pf):
    sgn="NN"
    gen='F'
    num='X'
    nn=False
    cc=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if 'CC' in item[2][0:2] and pos>pi:
                cc=True
            if 'Z' in item[2][0]:
                if item[1]!='1':
                    num='P'
                else:
                    num='S'
            if ('NP' in item[2][0:2]) or ('NC' in item[2][0:2]):
                sgn=item[2][2:4] 
                # en frases con sujetos múltiples si hay un sujeto masculino, el género es masculino
                if sgn[0]=='M':
                    gen='M'
                # si el género es común, se toma el género del determinante   
#                if sgn[0]=='C':
#                    sgn=get_generodeterminante(data,pi,pos)+sgn[1]
#                if cc:
#                    sgn=sgn[0]+'P'
                nn=True
            if ('PP' in item[2][0:2]) or ('PI' in item[2][0:2]):
                sgn=item[2][3:5] 
                # en frases con sujetos múltiples si hay un sujeto masculino, el género es masculino
                if sgn[0]=='M':
                    gen='M'
                # si el género es común, se toma el género del determinante   
                if sgn[0]=='C':
                    sgn=get_generodeterminante(data,pi,pos)+sgn[1]
                if cc:
                    sgn=sgn[0]+'P'
                # si no hya nombre y se detecta un adjetivo calificativo, se toma su género y número
            if not nn and 'AQ' in item[2][0:2]:
                sgn=item[2][3:5]           
            if 'V' in item[2][0] and pos>pi:
                if num!='X':
                    sgn=sgn[0]+num
                if gen=='M':
                    sgn='M'+sgn[1]
                return sgn
    return sgn

def get_adjetivogeneroynumero(data,pi,pf):
    agn="XX"
    verbo=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('V' in item[2][0]):
               verbo=True
            if ('A' in item[2][0]):
               agn=item[2][3:5]    
            if verbo and ('N' in item[2][0]):
               agn=item[2][2:4]
            if verbo and ('VMP' in item[2]):
               agn=item[2][6]+item[2][5]
    return agn

def get_numbers(data,pi,pf):
    num="X"
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('Z' in item[2][0]):
                num=item[1]
    return num

def get_haysp(data,pi,pf):
    sp=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('SP' in item[2][0:2]):
                sp=True
                return pos,sp
    return -1,sp

def cambiaconcordancia(data,pi,pf,gender):
    verbo=False
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('V' in item[2][0]):
                verbo=True
            if ('A' in item[2][0]):
                if SINGULAR in gender:
                    item[0]=item[1] # ponemos el lema
                agn=cambiageneroynumero(item[0],gender=gender)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:3]+gender[0].upper()+gender[1].upper()+data[pos][2][5:]
            if verbo and ('N' in item[2][0]):
                if SINGULAR in gender:
                    item[0]=item[1] # ponemos el lema
                agn=cambiageneroynumero(item[0],gender=gender)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:2]+gender[0].upper()+gender[1].upper()+data[pos][2][4:]   
            if verbo and ('VMP' in item[2]):
                agn=cambiageneroynumero(item[0],gender=gender)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:4]+gender[0].upper()+gender[1].upper()                
    return data

def cambiaconcordanciasustantivo(data,pi,pf,gender,debug=False):
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('VMP' in item[2]):
                agn=cambiageneroynumero(item[0],gender=gender,debug=debug)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:5]+gender[0].upper()+gender[1].upper()
            if ('N' in item[2][0]) and (item[2][2:4]!=gender[0:2].upper()):
                if SINGULAR in gender and NEUTRAL not in gender:
                    item[0]=item[1] # ponemos el lema)
                agn=cambiageneroynumero(item[0],gender=gender,debug=debug)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:2]+gender[0].upper()+gender[1].upper()+data[pos][2][4:]
    return data

def cambiaconcordanciasadjetivo(data,pi,pf,gender,debug=False):
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if ('VMP' in item[2]):
                agn=cambiageneroynumero(item[0],gender=gender,debug=debug)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:5]+gender[0].upper()+gender[1].upper()
            if ('A' in item[2][0]) and (item[2][2:4]!=gender[0:2].upper()):
                if SINGULAR in gender:
                    item[0]=item[1] # ponemos el lema)
                
                agn=cambiageneroynumero(item[0],gender=gender,debug=debug)
#                st.write('cambiaconcordanciasadjetivo:',item[0],gender,agn)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:3]+gender[0].upper()+gender[1].upper()+data[pos][2][5:]
            if ('N' in item[2][0]) and (item[2][2:4]!=gender[0:2].upper()):
                if SINGULAR in gender:
                    item[0]=item[1] # ponemos el lema)
                agn=cambiageneroynumero(item[0],gender=gender,debug=debug)
                data[pos][0]=agn
                data[pos][2]=data[pos][2][0:2]+gender[0].upper()+gender[1].upper()+data[pos][2][4:]
    return data


def cambiaconcordanciadeterminante(data,pi,pf,gender,debug=False):
    for pos,item in enumerate(data):
        if pos>=pi and pos <=pf:
            if 'D' in item[2][0] or 'PD' in item[2][0:2]:
                dgn=cambiageneroynumero(item[0],gender=gender)
                data[pos][0]=dgn
                data[pos][2]=data[pos][2][0:3]+gender[0].upper()+gender[1].upper()+data[pos][2][5:]
    return data

def concordanciacopulativa(data,pi,pf,posps,posv,debug=False):
    sgn=get_sujetogeneroynumero(data,pi,posps[0])
    dgn=get_determinantegeneroynumero(data,pi,posps[0])
# ahora miramos la concordancia del adjetivo o atributo y su determinante
    dagn=get_determinantegeneroynumero(data,posv,pf[0])
    agn=get_adjetivogeneroynumero(data,posv,pf[0])
    if sgn[0]=='C' and dgn[0]!='X':
        sgn=dgn
    if agn[0]!='C':
        gender=sgn[0].lower()
    else:
        gender=agn[0].lower()
    if sgn[1]!='N':
        if sgn[1]=='P':
            gender=gender+PLURAL
        else:
            gender=gender+SINGULAR
    else:
        gender=gender+NEUTRAL
    data=cambiaconcordanciadeterminante(data,posv,pf[0],gender,debug=debug)
    data=cambiaconcordanciasadjetivo(data,posv,pf[0],gender,debug=debug)
#    st.write(data)    

    return data

def concordanciasustantivodeterminante(data,pi,pf,debug=False):
    sgn=get_sustantivogeneroynumero(data,pi,pf)
    dgn=get_determinantegeneroynumero(data,pi,pf)
    agn=get_adjetivogeneroynumero(data,pi,pf)
    num=get_numbers(data,pi,pf)
    if dgn!='XX':
        if sgn!='NN':
            if dgn!=sgn or (dgn!=agn and agn!='XX'):
                if sgn[0]!=dgn[0]:
                    if sgn[0]!='C' and dgn[0]!='C':
                        gender=sgn[0].lower()
    #                    if dgn[0]=='C':
    #                        gender=sgn[0].lower()
                    else:
                    #    gender='c'
                        gender=dgn[0].lower()
                else:
                    gender=sgn[0].lower()
                if sgn[1]!='N':
                    if sgn[1]=='P':
                        gender=gender+PLURAL
                    else:
                        gender=gender+SINGULAR
                else:
                    gender=gender+NEUTRAL
                if gender[0:2]!=dgn.lower():
                    data=cambiaconcordanciadeterminante(data,pi,pf,gender,debug)
    #            data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
                if agn!='XX':
                    data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
        else:
            if dgn!=agn and agn!='XX':
                if agn[0]!=dgn[0]:
                    if agn[0]!='C' and dgn[0]!='C':
                        gender=agn[0].lower()
    #                    if dgn[0]=='C':
    #                        gender=sgn[0].lower()
                    else:
                    #    gender='c'
                        gender=dgn[0].lower()
                else:
                    gender=agn[0].lower()
                if agn[1]!='N':
                    if agn[1]=='P':
                        gender=gender+PLURAL
                    else:
                        gender=gender+SINGULAR
                else:
                    gender=gender+NEUTRAL
                if gender[0:2]!=dgn.lower():
                    data=cambiaconcordanciadeterminante(data,pi,pf,gender,debug)            
    else:
        gender=NEUTRAL
        if agn[0]!='C':
            if sgn[0]=='F':
                gender=FEMALE
            if sgn[0]=='M':
                gender=MALE
        if num!='X':
            if num=='1':
                    gender=gender+SINGULAR
            if num!='1':
                    gender=gender+PLURAL
            data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
            data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
        else:
            if sgn!=agn and sgn!='00' and agn!='XX':
                if sgn[1]=='P':
                    gender=gender+PLURAL
                if sgn[1]=='S':
                    gender=gender+SINGULAR
                if sgn[1]=='N':
                    gender=gender+NEUTRAL
                data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
                data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
    return data

def concordanciadeterminantesustantivo(data,pi,pf,debug=False):
    sgn=get_sujetogeneroynumero(data,pi,pf)
    dgn=get_determinantegeneroynumero(data,pi,pf)
    agn=get_adjetivogeneroynumero(data,pi,pf)
    num=get_numbers(data,pi,pf)
    if dgn!='XX':
        if dgn!=sgn or dgn!=agn:
            if sgn[0]!=dgn[0]:
                if sgn[0]!='C':
                    gender=dgn[0].lower()
                    if dgn[0]=='C':
                        gender=sgn[0].lower()
                else:
                    gender='c'
            else:
                gender=dgn[0].lower()
            if sgn[1]!='N':
                if dgn[1]=='P':
                    gender=gender+PLURAL
                else:
                    gender=gender+SINGULAR
            else:
                gender=gender+NEUTRAL
            data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
            data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
    else:
        gender=NEUTRAL
        if agn[0]!='C':
            if sgn[0]=='F':
                gender=FEMALE
            if sgn[0]=='M':
                gender=MALE
        if num!='X':
            if num=='1':
                    gender=gender+SINGULAR
            if num!='1':
                    gender=gender+PLURAL
            data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
            data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
        else:
            if sgn!=agn and sgn!='00' and agn!='XX':
                if sgn[1]=='P':
                    gender=gender+PLURAL
                if sgn[1]=='S':
                    gender=gender+SINGULAR
                if sgn[1]=='N':
                    gender=gender+NEUTRAL
                data=cambiaconcordanciasustantivo(data,pi,pf,gender,debug)
                data=cambiaconcordanciasadjetivo(data,pi,pf,gender,debug)
    return data

def concordanciaexcepcionfemenino(data,pi,pf,debug):

    if data[pi][1]=='alguno':
        data[pi][1]='algún'
    if data[pi][1]=='uno':
        data[pi][1]='un'
    if data[pi][1]=='ninguno':
        data[pi][1]='ningún'
    if data[pi][0][0].isupper():
        data[pi][0]=data[pi][1][0].upper()+data[pi][1][1:]
    else:
        data[pi][0]=data[pi][1]
    data[pi][2]=data[pi][2][0:3]+'F'+data[pi][2][4:]
    data[pf][2]=data[pf][2][0:2]+'F'+data[pf][2][3:]
    return data

def concordanciadeterminantenombre(data,pi,pf,debug=False):
    pos=pi
    while pos<(pf-1):
        item=data[pos]
        if item[2][0]=='D':
            if data[pos+1][2][0]=='N' or data[pos+1][2][0]=='V':
                if data[pos+1][0] in atonicafemeninos:
                    data=concordanciaexcepcionfemenino(data,pos,pos+1,debug)
                else:
                    data=concordanciasustantivodeterminante(data,pos,pos+1,debug)
#                    data=concordanciadeterminantesustantivo(data,pos,pos+1,debug)
        pos=pos+1   
    return data

def concordancianombreadjetivo(data,pi,pf,debug=False):
    pos=pi
    while pos<(pf-1):
        item=data[pos]
        if item[2][0]=='N':
            if data[pos+1][2][0]=='A':
                if data[pos+1][2][3]=='C':
                    gender='c'
                else:
                    gender=item[2][2].lower()
                if item[2][3]=='P':
                    gender=gender+PLURAL
                if item[2][3]=='S':
                    gender=gender+SINGULAR
                if item[2][3]=='N':
                    gender=gender+NEUTRAL
                data=cambiaconcordanciasadjetivo(data,pos+1,pos+2,gender)
        pos=pos+1   
    return data

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def buscanombrespropios(data,nombres_masculinos,nombres_femeninos,pi,pf):
    posv=pf
    lema=''
    for pos,item in enumerate(data):
        if pos >= pi and pos <= pf:
            if lema!='D' and (item[2][0]!="V" or pos==pi or lema=='C' or lema=='F'):
                if pos<=posv:
#            if pos==pi:
                    if quitar_tildes(item[0].lower()) in nombres_femeninos:
                        data[pos][2]='NPFS0000'
                    if quitar_tildes(item[0].lower()) in nombres_masculinos:
                        data[pos][2]='NPMS0000'
            else:
                posv=pos
            lema=item[2][0]
            if 'NP' in item[2]:
                if '00000' in item[2]:
                    if quitar_tildes(item[0].lower()) in nombres_femeninos:
                        data[pos][2]=data[pos][2][0:2]+'FS0000'
                    else:
                        data[pos][2]=data[pos][2][0:2]+'MS0000'
    return data

def es_perifrasis(data,posv):
    if posv>=2:
        txt=''
        for pos in range(posv-2,posv):
            txt=txt+data[pos][1] + ' '
        txt=txt.strip()
        if txt in perifrasis:
            return True
    return False

def comprobarverbocopulativo(data,pi,pf):
    for p in range(pi,pf):
        if data[p][1] in verboscopulativos:
            if data[p][2][0]=='N' and data[p-1][2][0]!='D':
                data[p][2]='VMN0000'
                return data
    return data

def es_oracionfinal(data,pi,posv,debug=False):
    txt=' '.join([item[1] for item in data[pi:pi+2]])
    if txt in oracionesfinales:
        return True
    return False

def es_interrogativa(data,pi,pf):
    for p in range(pi,pf):
        if data[p][2][0:2] == 'PT':
            return True
    return False

def corregirverbocomer(texto,data):
    pos=-1
    if 'como' in texto:
        for p in range(len(data)):
            if data[p][0]=='como':
                pos=p
            if data[p][2][0]=='V':
                return data
        if pos>=0:
            data[pos][2]='VMN0000'
            data[pos][1]='comer'
    return data


def flexionafrase(texto,debug=False):
# remove blank spaces at the beginning and end of the text
    texto=texto.strip()
# check if we have to inflect the text
    conjugar=True
    txttmp= [s for s in texto.lower() if s.isalpha() or s.isspace()]
    txttmp=''.join(txttmp)
    for item in fraseshechas:
        if item == txttmp:
            return texto, texto
    if conjugar:
        for item in fraseshechascontinua:
            ti=len(item)
            if item == txttmp[0:ti]:
                conjugar=False
                break

#            return texto, texto

# insert a dot at the end of the text if it does not have one
    if len(texto)>0 and '.' not in texto[-1]:
        texto=texto+'.'
# split the input text into control and sentences. The control, if present, is in the first position
    txt=texto.split(']')
    if len(txt)>1:
        textlem = txt[1]
        tiempo=''
        if txt[0][1:]=='PP':
            tiempo = PRETERITE
        if txt[0][1:]=='PI':    
            tiempo = IMPERFECT
        if txt[0][1:]=='F':
            tiempo = FUTURE
    else:
        textlem = txt[0]
        tiempo = ''
    textlem=textlem.lower()
# the lematizer splits some words in two, so we have to join them at the end
    if " del " in textlem:
        replacedel=True
    else:
        replacedel=False
    if " al " in textlem:
        replaceael=True
    else:
        replaceael=False
    textlem=textlem.replace(' del ',' de el ')
    textlem=textlem.replace(' al ', ' a el ')
#    comas=findOccurrences(textlem, ',')
#   the comma is treated as a word, so we have to separate it from the word
    textlem=textlem.replace(', ',' , ')
    textlem = textlem.strip()
    textconj=''
    penum=[3,SG]
    penumant=[1,SG]
#   read the list of spanish names
    listanombresm,listanombresf=leer_nombres()
    mood=INDICATIVE
    tipofrase='ENU'
    if len(textlem)>1:


#   First we lemmatize.
        ls,lema,data=lematiza(tk,sp,mf,tagger,textlem)
#   exceptions: yo como ayer ... como is tagged as a CS instead of a VM (verb)
        data=corregirverbocomer(textlem,data)
#   We check if the firs word in a proper name as some times the lemmatizer does not recognize it
        data=buscanombrespropios(data,listanombresm,listanombresf,0,len(textlem))#0)
#   We search for the number of segments in the input text
#   A segment is a group of words that can be a subject, a verb, an object, etc. and it can be separated by a comma or a conjunction
#   The conjuncion is asigned to the next segment
        p,nfrases=get_numerofrases(data)
        nadv=0
#   If there are more than one segment, we count the number of adverbs of time. We will use this information to decide the time of the verb
        if nfrases>1:
            nadv=get_numeroadverbiostiempo(textlem.lower())
        nextverbsubj=False
#   process each segment
        for n in range(0, nfrases):
#   take the first and last position of the segment
            pi=p[n][0]
            pf=p[n][1]
            if es_interrogativa(data,pi,pf):
                tipofrase='INT'

#   Check if there are proper names in the segment
            data=buscanombrespropios(data,listanombresm,listanombresf,pi,pf)
#   Sometimes the segmentator leave the conjuncion in the previous segment, so we have to check if the first word is a conjuncion
            if n>0:
                poscs=get_conjuncionsubordinante(data,pi-1,pf-1)
            else:
                poscs=get_conjuncionsubordinante(data,pi,pf-1)
            if len(poscs)>0:
                if data[poscs[0]][1] in conjuncionestemporalespresente:
                    tiempo=PRESENT
                    nextverbsubj=True
# esto hay que mejorarlo, buscar los adverbios de tiempo en cada segmento
            if len(tiempo)==0:
                tiempo=get_tiempo(data,0,pf)
            if nadv>1:
                tiempo=get_tiempo(data,pi,pf)

#   Detect if there are two verbs in the segment and one of then belongs to the list of gerund verbs.
#   If so, we change the second verb by the gerund
            data=cambia_verbo_gerundio(data,pi,pf,debug)
#   We search for the verb and the position in the segment            
            verbo,posv=get_verbo(data,pi,pf)
#   We search for the prepositions "SP" before and after the verb
#   The gender and number concordance is fixed by the name

#   Before the verb
            posps=get_preposicion(data,pi,posv)
#   After the verb
            pospc=get_preposicion(data,posv+1,pf)

#            if debug:
#                st.write('Preposiciones después del verbo:',posps,pospc)
#            npospc=len(pospc)
#   Check the concordance of the determinant and sustantivs
            data=concordanciadeterminantenombre(data,pi,pf,debug)
 
#   Check the concordance of the adjective and sustantivs
            data=concordancianombreadjetivo(data,pi,pf,debug)
            pp=posv+1

#   Concordance in segments with preposition after the verb 
            for pos in pospc:
                if pos>=pp:
                    data=concordanciasustantivodeterminante(data,pp,pos,debug)
                    pp=pos+1
#   If it is a copulative sentence we have to check the concordance of the subject and the attribute
#   Sometimes the analyzer does not recognize the verb ser/parecer/estar as a verb and it is tagged as a sustantive
#   We have to check if the verb is a sustantive and it is preceded by a determinante. If so, we change the tag to verb
            data=comprobarverbocopulativo(data,pi,pf)
            if es_frasecopulativa(data,pi,pf):
                cgs=concordanciacopulativa(data,pi,pospc,posps,posv,debug)
#   We serach for the subject and the position in the segment
            pos=-1
            if posv>=0:
                if tipofrase=='INT':
                    penum,pos=get_sujetointerrogativa(data,pi,posv+2)
                if tipofrase=='ENU':
                    penum,pos=get_sujeto(data,pi,posv,debug)
#   By default the mood is indicative, but if it is a the previous verb require a subjunctive mood for the next verb, we change the mood
            if nextverbsubj:
                mood=SUBJUNCTIVE
            else:
#   If the verb is in the list of verbs that require subjunctive mood, we change the mood
                mood=INDICATIVE
                for pp in range(pi,posv):
                    if data[pp][1]=='aunque':
                        mood=SUBJUNCTIVE

                if pos==-1:
                    if posv>0 and data[posv-1][1] in subjuntivos:
                        mood=SUBJUNCTIVE
#   [PP] yo ir al quisco, pero estar cerrado --> yo fui al quiosco, pero estaba cerrado
#   The second segment hasn't a subject, by default the verb is conjugated in the 3rd person singular
#   if the main sentence is in past perfect, the second sentence is in past imperfect
                    if data[pi][0] in conjuncion3p:
                        penum=[3,SG]
                        if tiempo==PRETERITE:
                            tiempo=IMPERFECT
                    else:
                        penum=penumant
                    if verbo in verbos3p:
                        penum=[3,SG]
                if es_oracionfinal(data,pi-2,posv,debug):
                    mood=SUBJUNCTIVE
                    nextverbsubj=True
            if posv>=0:
                penumant=penum
#   Check is it is a perifrasis verbale
                if not es_perifrasis(data,posv):
#   At this moment there is only the present of the subjunctive (improve in the future with the past) 
                    if mood==SUBJUNCTIVE: 
                        tiempo=PRESENT
#   for some reason the first call to "conjugate" gives an error, but the second time it works
                    try:
                        if conjugar:
                            verboconjugado=conjugate(verbo,tiempo,penum[0],penum[1],mood=mood)
                        else:
                            verboconjugado=data[posv][0]
                    except:
                        if conjugar:
                            verboconjugado=conjugate(verbo,tiempo,penum[0],penum[1],mood=mood)
                        else:
                            verboconjugado=data[posv][0]
                    data[posv][0]=verboconjugado
#   if the previous segment was in subjunctive mood and the next segment has a copulative conjunction, we have follow in subjunctive mood
                    if nextverbsubj and n<nfrases-1 and data[pf+1][2]!='CC':
                        nextverbsubj=False
#   Check if verb requires subjunctive mood in the next segment
#   verb + que + subjuntive
            if not nextverbsubj:
                if posv+1<=pf and data[posv][1] in verbossubjuntivos and data[posv+1][1]=='que':
                    nextverbsubj=True
#   Test if the previous segment ends in "para" and the next segment starts with "que". In this case the verb of the next segment is in subjunctive mood
            if es_oracionfinal(data,pf,posv,debug):
                nextverbsubj=True

        if len(data)>0:
            textconj=' '.join(x[0] for x in data)   
            textconj=textconj.replace(' ,',',').replace(' .','.')
            textconj=textconj[0:-1]
            if replacedel:
                textconj=textconj.replace(' de el ', ' del ')
            if replaceael:
                textconj=textconj.replace(' a el ', ' al ')

    return textconj

# ................................................................


# inicializamos el Analizador Morfológico
tk,sp,mf,tagger = Analizador()
# creamos un fichero log donde escribiremos la frases sin flexionar y la frase flexionada
fout=open('logflexionarV3.txt','a')
# create the Flask app
app = Flask(__name__)

# create a route for the app
@app.route('/flexionar', methods=['GET'])
def frase():
    # get the text from the request
    text = request.args.get('frase').replace('"','')
    txt=text.split(']')
    mayusculas=False
    texto=text
    if len(txt)==2 and txt[1].isupper():
        texto=txt[0]+']'+txt[1].lower()
    if len(txt)==1 and txt[0].isupper():
        texto=txt[0].lower()
        mayusculas=True
    textconj=flexionafrase(texto)
    if mayusculas:
        textconj=textconj.upper()
    if len(text)>0:
        print(text,'-->',textconj)
        fout.write(texto+'-->'+textconj+'\n')
        fout.flush()
    return textconj

# run the app
if __name__ == '__main__':
    app.run(port=8506,host='0.0.0.0')