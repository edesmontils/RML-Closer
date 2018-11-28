import rdflib
from rdflib.namespace import RDF
from rdflib import RDF, RDFS, Namespace


onto = rdflib.Graph()
onto.parse("file:em-rdfs.n3",format="n3")

print("graph has %s statements." % len(onto))
# prints graph has 79 statements.

for subj, pred, obj in onto:
   if (subj, pred, obj) not in onto:
       raise Exception("It better be!")

s = onto.serialize(format='n3')
print(s.decode('UTF-8'))

rml = rdflib.Graph()
rml.parse("file:EM2EM.rml",format="n3")
s = rml.serialize(format='n3')
print(s.decode('UTF-8'))


RR = Namespace("http://www.w3.org/ns/r2rml#")
RML = Namespace("http://semweb.mmlab.be/ns/rml#")
QL = Namespace("http://semweb.mmlab.be/ns/ql#")

# ===========================================================================================
# Gestion de la subsomption des concepts
# ===========================================================================================

# [
# (?m rr:subjectMap ?s) (?s rr:class ?C) 
# (?C rdfs:subClassOf ?D) 
# -> 
# (?s rr:class ?D)
# ]
res = rdflib.Graph()

change = True
while change :
	change = False

	for m,s in rml.subject_objects(RR.subjectMap) :
		for c in rml.objects(s,RR['class']) :
			for d in onto.objects(c,RDFS.subClassOf) :
				t = (s,RR['class'],d)
				if t not in rml :
					rml.add(  t  )
					change = True

# ===========================================================================================
# Gestion de la subsomption des relations
# ===========================================================================================

# [
# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) 
# (?p rdfs:subPropertyOf ?q)
# -> 
# (?s rr:predicate ?q)
# ]

change = True
while change :
	change = False
	
	for m,s in rml.subject_objects(RR.predicateObjectMap) :
		for p in rml.objects(s,RR['predicate']) :
			for q in onto.objects(p,RDFS.subPropertyOf) :
				t = (s,RR['predicate'],q)
				if t not in rml :
					rml.add(  t  )
					change = True



# ===========================================================================================
# Domains
#{ ?x ?pred ?y . ?pred rdfs:domain ?c . } 
#	=> { ?x a ?c . } .

# [
# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) (?m rr:subjectMap ?t)
# (?p rdfs:domain ?c) noValue(?t rr:class ?c)
# -> 
# (?t rr:class ?c)
# ]

rml += onto
qres = rml.query(
	"""
	Construct { ?t rr:class ?c}
	WHERE { ?m rr:predicateObjectMap ?s . ?s rr:predicate ?p . ?m rr:subjectMap ?t . ?p rdfs:domain ?c . }
	""", initNs = { "rr": RR , "rdfs":RDFS }
	)

print('==============')
print(len(qres))
for t in qres : 
	if t not in rml:
		rml.add(  t  )
		print("## adding ##",t)

# ===========================================================================================
# Ranges
#{ ?x ?pred ?y . ?pred rdfs:range ?c . } 
#	=> { ?y a ?c . } .

# [
# (?m rr:predicateObjectMap ?po) (?po rr:predicate ?p) (?p rdfs:range ?C)
# (?po rr:objectMap ?o) (?o rr:parentTriplesMap ?m2)
# (?m2 rr:subjectMap ?s)  noValue(?s rr:class ?C)
# ->
# (?s rr:class ?C)
# ]

qres = rml.query(
	"""
	Construct { ?s rr:class ?C}
	WHERE { ?m rr:predicateObjectMap ?po . ?po rr:predicate ?p . ?p rdfs:range ?C . ?po rr:objectMap ?o . 
	?o rr:parentTriplesMap ?m2 . ?m2 rr:subjectMap ?s . }
	""", initNs = { "rr": RR , "rdfs":RDFS }
	)

print('==============')
print(len(qres))
for t in qres : 
	if t not in rml:
		rml.add(  t  )
		print("## adding ##",t)


print('==============')
rml -= onto

res.bind("rr",RR)
res.bind("rml",RML)

s = rml.serialize(format='n3')
print(s.decode('UTF-8'))

