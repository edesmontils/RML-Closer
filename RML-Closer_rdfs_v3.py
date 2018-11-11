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

# s = onto.serialize(format='n3')
# print(s.decode('UTF-8'))

rml = rdflib.Graph()
rml.parse("file:EM2EM.rml",format="n3")
# s = rml.serialize(format='n3')
# print(s.decode('UTF-8'))


RR = Namespace("http://www.w3.org/ns/r2rml#")
RML = Namespace("http://semweb.mmlab.be/ns/rml#")
QL = Namespace("http://semweb.mmlab.be/ns/ql#")


mappings = dict()
for m,s in rml.subject_objects(RR.subjectMap) :
	l = set()
	for o in rml.objects(m,RR.predicateObjectMap) :
		l.add(o)
	mappings[m] = (s,l)

# print(mappings)

change = True
while change :
	change = False

	for (m, (s,l)) in mappings.items() :

		# ===========================================================================================
		# Gestion de la subsomption des concepts
		# ===========================================================================================

		# [
		# (?m rr:subjectMap ?s) (?s rr:class ?C) 
		# (?C rdfs:subClassOf ?D) 
		# -> 
		# (?s rr:class ?D)
		# ]

		for c in rml.objects(s,RR['class']) :
			for d in onto.objects(c,RDFS.subClassOf) :
				t = (s,RR['class'],d)
				print("(subClass) find: ",t)
				if t not in rml :
					print("added")
					rml.add(  t  )
					change = True



		for pom in l :
			for p in rml.objects(pom,RR['predicate']) :
				# ===========================================================================================
				# Gestion de la subsomption des relations
				# ===========================================================================================

				# [
				# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) 
				# (?p rdfs:subPropertyOf ?q)
				# -> 
				# (?s rr:predicate ?q)
				# ]

				for q in onto.objects(p,RDFS.subPropertyOf) :
					t = (pom,RR['predicate'],q)
					print("(subProperty) find: ",t)
					if t not in rml :
						print("added")
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

				for d in onto.objects(p,RDFS.domain) :
					t = (s,RR['class'],d)
					print("(domain) find: ",t)
					if t not in rml :
						print("added")
						rml.add(  t  )
						change = True


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

				for d in onto.objects(p,RDFS.range) :
					for o in rml.objects(pom,RR.objectMap) :
						for m2 in rml.objects(o,RR.parentTriplesMap) :
							(s2,_) = mappings[m2]
							t = (s2,RR['class'],d)
							print("(range) find: ",t)
							if t not in rml :
								print("added")
								rml.add(  t  )
								change = True			


print('==============')


s = rml.serialize(format='n3')
print(s.decode('UTF-8'))

