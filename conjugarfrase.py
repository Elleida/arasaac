import pyfreeling

from pattern.es import conjugate,PRETERITE, PRESENT, FUTURE, IMPERFECT, SG, PL

# import flask to get the request data
from flask import Flask, request 


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
        "ustedes": [3, PL]
    }

presente=["hoy","actualmente","ahora","ya"]

pasado=["ayer","pasado","anterior","anteayer","anoche",]

pasado_imperfecto=["antes"]

futuro=["pasado mañana","mañana","futuro","próximo",'después']

verbos3p=["llover"]

verboscopulativos=['ser','estar','parecer']


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

def lematiza(tk,sp,mf,tagger,texto):
    l = tk.tokenize(texto)
    ls = sp.split(l)
    ls = mf.analyze(ls)	
    ls = tagger.analyze(ls)
    data=[]
    for s in ls :
        ws = s.get_words()
        lemas=' '.join([w.get_lemma() for w in ws ])
    for w in ws:
        data.append([w.get_form().replace('_',' '),w.get_lemma(),w.get_tag()])
    return lemas,data
    
    
def get_pronombre(data,pi,p):
    out=[1,SG]
    pout=-1
    np=0
    for pos,item in enumerate(data):
        if pos > pi and pos < p:
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

def get_verbo(data,pi,p):
    fp=0
    for pos,item in enumerate(data):
        if pos > pi and pos >p:
            if item[2][0]=='F':
                fp=fp+1
            if (('VM' in item[2]) or ('VS' in item[2]) or ('VA' in item[2])) and (item[2][3:7]=='0000'):
                return item[1],pos-fp
    return '',-1

def get_sujeto(data,pi,p):
    out=[1,SG]
    pos0=-1
    pout=-1
    ns=0
    nc=0
    np=0
    for pos,item in enumerate(data):
        if pos > pi and pos < p:
            if ('CC' in item[2]):
                nc=nc+1
            if ('NP' in item[2]) or ('NC' in item[2]):
                ns=ns+1
                if np==0:
                    if 'P' in item[2][2:]:
                        out=[3, PL]
                        pos0=pos
                    else:
                        out=[3, SG]
                        pos0=pos           
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

    if pout>pos0:
        pos0=pout
    if (ns>1)and(nc>0):
        out=[3,PL]    
    if np>1:
        out[1]=PL
    if np==1 and ns>=1:
        out[1]=PL
    return out,pos0

def get_numerofrases(data):
    nf=1
    pf=0
    pp=-1
    p=[-1]
    for pos,item in enumerate(data):
        if (pf==0) and ('V' in item[2][0]):
            pf=1
        if (pf==1) and ('C' in item[2][0]):
            pf=2
            pp=pos
        if (pf==1) and ('P' in item[2][0]):
            pf=2
            pp=pos-1
        if (pf==1) and ('R' in item[2][0]):
            pf=2
            pp=pos
        if (pf==2) and ('V' in item[2][0]):
            pf=3
        if pf==3:
            nf=nf+1
            pf=1
            p.append(pp)
    p.append(pos)
    return p,nf

def nombre_compuesto(data,p):
    posv=p
    for pos,item in enumerate(data):
        if pos < p:
            posv=posv+item[1].count('_')
    return posv

def get_tiempo(data,pi,pf):
    tiempo=PRESENT
    textlem=' '.join(x[0].lower() for x in data[pi:pf]) 
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
    textlem=' '.join(x[1] for x in data[pi:pf]) 
#    st.write(textlem)
    if any(x in textlem for x in verboscopulativos):
        out=True
    return out

def get_sujetogeneroynumero(data,pi,pf):
    sgn="NN"
    for pos,item in enumerate(data):
        if pos > pi and pos < pf:
            if ('NP' in item[2]) or ('NC' in item[2]):
               sgn=item[2][2:4]     
    return sgn

def get_adjetivogeneroynumero(data,pi,pf):
    agn="NN"
    for pos,item in enumerate(data):
        if pos > pi and pos < pf:
            if ('A' in item[2][0]) or ('A' in item[2][0]):
               agn=item[2][3:5]     
    return agn

def pasaamasculino(data,pi,pf):
    return  

def pasaafemenino(data,pi,pf):
    return 

def pasaasingular(data,pi,pf):
    return 

def pasaaplural(data,pi,pf):
    return 

def concordancia(data,pi,pf):
    sgn=get_sujetogeneroynumero(data,pi,pf)
    agn=get_adjetivogeneroynumero(data,pi,pf)
    if (sgn[0]=='M') and (agn[0]=='F'):
        data=pasaamasculino(data,pi,pf)
    if (sgn[0]=='F') and (agn[0]=='M'):
        data=pasaafemenino(data,pi,pf)
    if (sgn[1]=='S') and (agn[1]=='P'):
        data=pasaasingular(data,pi,pf)
    if (sgn[0]=='P') and (agn[0]=='S'):
        data=pasaaplural(data,pi,pf)
    return data

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def conjugafrase(texto):

    if texto.isupper():
        texto=texto.lower()
    textlem=texto
    textlem=textlem.replace(' del ',' de el ')
    textlem=textlem.replace(' al ', ' a el ')
    comas=findOccurrences(textlem, ',')

    textlem=textlem.replace(', ',' ')
    textlem = textlem.strip()
    print(textlem)
    textconj=''
    if len(textlem)>1:
        lema,data=lematiza(tk,sp,mf,tagger,textlem)
        p,nfrases=get_numerofrases(data)
        nadv=0
        if nfrases>1:
            nadv=get_numeroadverbiostiempo(textlem.lower())

        for n in range(0, nfrases):
            pi=p[n]
            if nadv>1:
                tiempo=get_tiempo(data,pi+1,p[n+1]+1)
            else:
                tiempo=get_tiempo(data,0,p[nfrases]+1)

            verbo,posv=get_verbo(data,pi,p[n])
            pos=-1
            if posv>=0:
                if pos==-1:
                    penum,pos=get_sujeto(data,pi,posv)
            if pos==-1:
                if verbo in verbos3p:
                    penum=[3,SG]
                if n>0:
                    penum=penumant


            if posv>=0:
                penumant=penum
                print(verbo,tiempo,penum[0],penum[1])
                try: 
                    verboconjugado=conjugate(verbo,tiempo,penum[0],penum[1])
                except:
                    verboconjugado=conjugate(verbo,tiempo,penum[0],penum[1])

                posv=nombre_compuesto(data,posv)
                data[posv][0]=verboconjugado
                if es_frasecopulativa(data,pi+1,p[n+1]+1):
                    cgs=concordancia(data,pi+1,p[n+1]+1)
            else:
                print('No se ha detectado verbo')
        print(data)
        textconj=' '.join(x[0] for x in data)            
    return textconj


# inicializamos el Analizador Morfológico
tk,sp,mf,tagger = Analizador()

# create the Flask app
app = Flask(__name__)

# create a route for the app
@app.route('/flexionar', methods=['GET'])
def frase():
    # get the text from the request
    text = request.args.get('frase').replace('"','')
    print(text)
    textconj=conjugafrase(text)
    return textconj

# run the app
if __name__ == '__main__':
    app.run(port=8503,host='0.0.0.0')


        

