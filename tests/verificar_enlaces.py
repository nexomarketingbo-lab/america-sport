"""Pruebas del agente America Sport.

Comprueba que el prompt tenga los datos clave y que cada enlace, filtro y
escenario típico muestre productos en americasportbolivia.com.

Uso: python3 tests/verificar_enlaces.py [kapso/workflow-america-sport.json]
"""
import json,re,sys,time,urllib.parse,subprocess,concurrent.futures as cf
path=sys.argv[1] if len(sys.argv)>1 else 'kapso/workflow-america-sport.json'
d=json.load(open(path,encoding='utf-8')); d=d.get('data') or d['workflow']['definition']; nodes=d.get('nodes') or d['definition']['nodes']
ag=[n for n in nodes if n['data']['node_type']=='agent'][0]['data']['config']; sp=ag['system_prompt']
B='https://americasportbolivia.com/index.php'
def count(u):
    for intento in range(3):
        n=_count(u)
        if n: return n
        time.sleep(2)
    return 0
def _count(u):
    out=subprocess.run(['curl','-sS','-L','--max-time','30',u],capture_output=True).stdout.decode('utf-8','replace')
    return len(set(re.findall(r'codigo=(\d+)',out)))
res={'ok':0,'fail':[]}
def check(label,u):
    n=count(u); return (label,u,n)
# 1. Contenido obligatorio en el prompt
must={'Dirección':'Calle Colón #130','Horario L-S':'9:00 a 20:00','Horario domingo':'10:00 a 14:00','Pago QR':'QR','Sin devoluciones':'no hay devoluciones','Cambios tardes':'todas las tardes','Sin uniformes':'No** hacemos uniformes','Envíos':'Sí hacemos envíos','Maps':'maps.app.goo.gl/MiKgaevYmwHoAXeU9','WhatsApp':'72181658','Regla de enlaces':'siempre mandar enlace','Herramienta handoff':'handoff_to_human','No inventar precios':'Nunca inventes'}
print('== 1. Contenido del prompt guardado en Kapso ==')
for k,v in must.items(): print(('OK  ' if v in sp else 'FALLA'),k)
print('Quedan [COMPLETAR]:', sp.count('[COMPLETAR'),'| longitud:',len(sp))
print('Herramientas:',sorted(ag.get('enabled_default_tools',[])),'| modelo:',ag.get('provider_model_id'))
# 2. Enlaces literales del prompt
links=sorted(set(re.findall(r'https://americasportbolivia\.com/index\.php\?[^\s)`"·]+',sp)))
# 3. Cada valor de las listas (familias, marcas)
fam=re.search(r'\*\*Calzado:\*\*(.*?)Ejemplos',sp,re.S).group(1)
famvals=sorted(set(v.strip() for v in re.findall(r'([A-Z%0-9]+(?:%20[A-Z]+)?)',re.sub(r'\*\*\w+:\*\*','',fam)) if len(v.strip())>2))
mar=re.search(r'## Marcas principales\n(.*?)\n',sp).group(1)
marvals=[v.strip() for v in mar.split('·')]
gru=re.findall(r'\?grupo=([A-Z%0-9]+)',sp)
jobs=[('enlace',u) for u in links]+[('familia '+v,f'{B}?familia={v}') for v in famvals]+[('marca '+v,f'{B}?marca={v}') for v in marvals]+[('grupo '+v,f'{B}?grupo={v}') for v in sorted(set(gru+['RUNING','VESTIR']))]
# 4. Escenarios típicos de clientes -> enlace que el bot debería armar
esc={'¿Tienen chuteras Adidas?':'marca=ADIDAS&familia=CHUTERAS','Zapatillas Nike para mujer':'marca=NIKE&familia=ZAPATILLAS&genero=MUJER','Zapatillas para correr de hombre':'grupo=RUNNING&familia=ZAPATILLAS&genero=HOMBRE','Chuteras para niño':'familia=CHUTERAS&genero=NI%C2%A5OS','Pelota de fútbol':'grupo=FUTBOL&familia=PELOTAS','Pelota de básquet':'grupo=BASQUET&familia=PELOTAS','Mochilas Totto':'marca=TOTTO&familia=MOCHILAS','Crocs':'familia=CROCS','Sandalias de mujer':'familia=SANDALIAS&genero=MUJER','Poleras Puma':'marca=PUMA&familia=POLERAS','Short de hombre':'familia=SHORT&genero=HOMBRE','Calzas de mujer':'familia=CALZAS&genero=MUJER','Guantes de arquero':'grupo=FUTBOL&familia=GUANTES','Raquetas de tenis':'grupo=TENIS&familia=RAQUETAS','Pesas/mancuernas gimnasio':'familia=MANCUERNAS','Gorras Nike':'marca=NIKE&familia=GORRAS','Zapatillas New Balance':'marca=NEW%20BALANCE&familia=ZAPATILLAS','Canilleras':'familia=CANILLERAS','Buzos para niños':'familia=BUSOS&genero=NI%C2%A5OS','Natación (gorros, lentes)':'grupo=NATACION','Ofertas':'oferta=1'}
jobs+=[('escenario: '+k,f'{B}?{v}') for k,v in esc.items()]
with cf.ThreadPoolExecutor(1) as ex: out=list(ex.map(lambda j:check(*j),jobs))
for sec in ['enlace','familia','marca','grupo','escenario']:
    rows=[o for o in out if o[0].startswith(sec)]
    bad=[o for o in rows if o[2]==0]
    print(f'\n== {sec}: {len(rows)-len(bad)}/{len(rows)} con productos ==')
    for o in (rows if sec=='escenario' else bad): print(f'  {"OK " if o[2] else "0 !!"} {o[2]:>3}  {o[0]}  {o[1].split("?")[1]}')
