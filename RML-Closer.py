import rdflib
from rdflib.namespace import RDF

from rdflib import RDF, RDFS, Namespace

RR = Namespace("http://www.w3.org/ns/r2rml#")
RML = Namespace("http://semweb.mmlab.be/ns/rml#")
QL = Namespace("http://semweb.mmlab.be/ns/ql#")

#==================================================
#==================================================

class RMLCloser(object):
	"""docstring for RMLCloser"""
	def __init__(self):
		super(RMLCloser, self).__init__()
		self.mappings = None
		self.onto = rdflib.Graph()
		self.rml = rdflib.Graph()
		self.rules1 = set()
		self.rules2 = set()

	def init(self):
		self.mappings = dict()
		for m,s in self.rml.subject_objects(RR.subjectMap) :
			l = set()
			for o in self.rml.objects(m,RR.predicateObjectMap) :
				l.add(o)
			self.mappings[m] = (s,l)
		
	def enrich(self) :
		if self.mappings is None : self.init()
		change = True
		while change :
			change = False
			for (m, (s,l)) in self.mappings.items() :
				for r in self.rules1 :
					change = change or r(m,s,l)
				for pom in l :
					for p in self.rml.objects(pom,RR['predicate']) :
						for r in self.rules2 :
							change = change or r(m,s,l,pom,p)
		

	def loadRML(self,fileName) :
		self.rml.parse(fileName,format="n3")
		print("RML graph has %s statements." % len(self.rml))

	def loadOnto(self,fileName) :
		self.onto.parse(fileName,format="n3")
		print("Ontology graph has %s statements." % len(self.onto))



#==================================================
#==================================================

class RDFSCloser(RMLCloser):
	"""docstring for RDFSCloser"""
	def __init__(self):
		super(RDFSCloser, self).__init__()
		self.rules1 = (self.subsomptionRule, )
		self.rules2 = (self.subpropertyRule, self.domainRule, self.rangeRule)

	# ===========================================================================================
	# Gestion de la subsomption des concepts
	# ===========================================================================================
	# [
	# (?m rr:subjectMap ?s) (?s rr:class ?C) 
	# (?C rdfs:subClassOf ?D) 
	# -> 
	# (?s rr:class ?D)
	# ]
	def subsomptionRule(self,m,s,lpom) :
		change = False
		for c in self.rml.objects(s,RR['class']) :
			for d in self.onto.objects(c,RDFS.subClassOf) :
				t = (s,RR['class'],d)
				print("(subClass) find: ",t)
				if t not in self.rml :
					print("added")
					self.rml.add(  t  )
					change = True		
		return change

	# ===========================================================================================
	# Gestion de la subsomption des relations
	# ===========================================================================================
	# [
	# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) 
	# (?p rdfs:subPropertyOf ?q)
	# -> 
	# (?s rr:predicate ?q)
	# ]
	def subpropertyRule(self,m,s,lpom, pom, p):
		change = False
		for q in self.onto.objects(p,RDFS.subPropertyOf) :
			t = (pom,RR['predicate'],q)
			print("(subProperty) find: ",t)
			if t not in self.rml :
				print("added")
				self.rml.add(  t  )
				change = True
		return change


	# ===========================================================================================
	# Domains
	#{ ?x ?pred ?y . ?pred rdfs:domain ?c . } 
	#	=> { ?x a ?c . } .
	# [
	# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) (?m rr:subjectMap ?s)
	# (?p rdfs:domain ?d) noValue(?s rr:class ?d)
	# -> 
	# (?s rr:class ?d)
	# ]
	def domainRule(self,m,s,lpom,pom,p) :
		change = False

		for d in self.onto.objects(p,RDFS.domain) :
			t = (s,RR['class'],d)
			print("(domain) find: ",t)
			if t not in self.rml :
				print("added")
				self.rml.add(  t  )
				change = True
		return change

	# ===========================================================================================
	# Ranges
	#{ ?x ?pred ?y . ?pred rdfs:range ?c . } 
	#	=> { ?y a ?c . } .
	# [
	# (?m rr:predicateObjectMap ?pom) (?po rr:predicate ?p) (?p rdfs:range ?d)
	# (?pom rr:objectMap ?o) (?o rr:parentTriplesMap ?m2)
	# (?m2 rr:subjectMap ?s2)  noValue(?s rr:class ?d)
	# ->
	# (?s2 rr:class ?d)
	# ]
	def rangeRule(self,m,s,lpom,pom,p):
		change = False
		for d in self.onto.objects(p,RDFS.range) :
			for o in self.rml.objects(pom,RR.objectMap) :
				for m2 in self.rml.objects(o,RR.parentTriplesMap) :
					(s2,_) = self.mappings[m2]
					t = (s2,RR['class'],d)
					print("(range) find: ",t)
					if t not in self.rml :
						print("added")
						self.rml.add(  t  )
						change = True
		return change


#==================================================
#==================================================

class OWLLiteCloser(RDFSCloser):
	"""docstring for OWLLiteCloser"""
	def __init__(self):
		super(OWLLiteCloser, self).__init__()



#==================================================
#==================================================
#==================================================
if __name__ == "__main__":
	print("main sweep")
	cl = RDFSCloser()
	cl.loadOnto("file:em-rdfs.n3")
	cl.loadRML("file:EM2EM.rml")

	cl.enrich()

	print('==============')


	s = cl.rml.serialize(format='n3')
	print(s.decode('UTF-8'))

