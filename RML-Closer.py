import rdflib
from rdflib.namespace import RDF

from rdflib import RDF, RDFS, OWL, Namespace, BNode

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
		self.rules1 = set() # rules r(m,s,l)
		self.rules2 = set() # rules r(m,s,l,pom,p)

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
		# print("RML graph has %s statements." % len(self.rml))

	def loadOnto(self,fileName) :
		self.onto.parse(fileName,format="n3")
		# print("Ontology graph has %s statements." % len(self.onto))

	def setRML(self, r) :
		assert instanceof(r,rdflib.Graph), "(setRML) r must be an rdflib.Graph"
		self.rml = r

	def setOnto(self, o) :
		assert instanceof(o,rdflib.Graph), "(setOnto) o must be an rdflib.Graph"
		self.onto = o

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
				# print("(subClass) find: ",t)
				if t not in self.rml :
					# print("added")
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
			# print("(subProperty) find: ",t)
			if t not in self.rml :
				# print("added")
				self.rml.add(  t  )
				change = True
		return change


	# ===========================================================================================
	# Domains
	#{ ?x ?pred ?y . ?pred rdfs:domain ?c . } 
	#	=> { ?x a ?c . } .
	# ===========================================================================================
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
			# print("(domain) find: ",t)
			if t not in self.rml :
				# print("added")
				self.rml.add(  t  )
				change = True
		return change

	# ===========================================================================================
	# Ranges
	#{ ?x ?pred ?y . ?pred rdfs:range ?c . } 
	#	=> { ?y a ?c . } .
	# ===========================================================================================
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
				ptm = self.rml.objects(o,RR.parentTriplesMap)

				for m2 in ptm :
					(s2,_) = self.mappings[m2]
					t = (s2,RR['class'],d)
					# print("(range) find: ",t)
					if t not in self.rml :
						# print("added")
						self.rml.add(  t  )
						change = True

				if not change:
					print("nnnnnnnnn")
					nrule = BNode()
		return change


#==================================================
#==================================================

class OWLLiteCloser(RDFSCloser):
	"""docstring for OWLLiteCloser"""
	def __init__(self):
		super(OWLLiteCloser, self).__init__()
		self.rules1 += (self.sameAsClassRule, self.equivalentClassRule)
		self.rules2 += (self.sameAsPropertyRule, self.equivalentPropertyRule)

	# ===========================================================================================
	# sameAs : 
	#{ ?s a ?C . ?C owl:sameAs ?D . } => { ?s a ?D .} .
	# ===========================================================================================
	# [ 
	# (?m rr:subjectMap ?s) (?s rr:class ?C) 
	# (?C owl:sameAs ?D)  noValue(?s rr:class ?D)
	# -> 
	# (?s rr:class ?D)
	# ]
	def sameAsClassRule(self,m,s,lpom) :
		change = False
		for c in self.rml.objects(s,RR['class']) :
			for d in self.onto.objects(c,OWL.sameAs) :
				t = (s,RR['class'],d)
				# print("(sameAs Class) find: ",t)
				if t not in self.rml :
					# print("added")
					self.rml.add(  t  )
					change = True		
		return change

	# ===========================================================================================
	# equivalentClass
	#{ ?x a ?class . ?class owl:equivalentClass ?equiv . } 
	#	=> { ?x a ?equiv . } .
	# ===========================================================================================
	# [
	# (?m rr:subjectMap ?s) (?s rr:class ?C) 
	# (?C owl:equivalentClass ?D) noValue(?s rr:class ?D)
	# -> 
	# (?s rr:class ?D)
	# ]
	def equivalentClassRule(self,m,s,lpom) :
		change = False
		for c in self.rml.objects(s,RR['class']) :
			for d in self.onto.objects(c,OWL.equivalentClass) :
				t = (s,RR['class'],d)
				# print("(equivalentClass) find: ",t)
				if t not in self.rml :
					# print("added")
					self.rml.add(  t  )
					change = True		
		return change

	# ===========================================================================================
	# sameAs : { ?s ?p ?o . ?p owl:sameAs ?x . } => { ?s ?x ?o .} .
	# ===========================================================================================
	# [
	# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) 
	# (?p owl:sameAs ?q)  noValue(?s rr:predicate ?q)
	# -> 
	# (?s rr:predicate ?q)
	# ]
	def sameAsPropertyRule(self,m,s,lpom, pom, p):
		change = False
		for q in self.onto.objects(p,OWL.sameAs) :
			t = (pom,RR['predicate'],q)
			# print("(sameAs Property) find: ",t)
			if t not in self.rml :
				# print("added")
				self.rml.add(  t  )
				change = True
		return change

	# ===========================================================================================
	# equivalentProperty
	#{ ?x ?pred ?y . ?pred owl:equivalentProperty ?equiv . } 
	#	=> { ?x ?equiv ?y . } .
	# ===========================================================================================
	# [
	# (?m rr:predicateObjectMap ?s) (?s rr:predicate ?p) 
	# (?p owl:equivalentProperty ?q) noValue(?s rr:predicate ?q) 
	# -> 
	# (?s rr:predicate ?q)
	# ]
	def equivalentPropertyRule(self,m,s,lpom, pom, p):
		change = False
		for q in self.onto.objects(p,OWL.equivalentProperty) :
			t = (pom,RR['predicate'],q)
			# print("(equivalent Property) find: ",t)
			if t not in self.rml :
				# print("added")
				self.rml.add(  t  )
				change = True
		return change

	# ===========================================================================================
	# Gestion des caractéristiques des propriétés
	# ===========================================================================================

	# {?P owl:inverseOf ?Q. ?S ?P ?O} => {?O ?Q ?S}.
	#
	# Inverses.
	#{ ?x owl:inverseOf ?y . } 
	#	=> { ?x a owl:Property . ?y a owl:Property . } .
	#{ ?x ?pred ?y . ?pred owl:inverseOf ?inverse . } 
	#	=> { ?y ?inverse ?x . } .



	# {?P a owl:SymmetricProperty. ?S ?P ?O} => {?O ?P ?S}.
	#
	# Symmetric properties
	#{ ?pred a owl:SymmetricProperty . } 
	#	=> { ?pred a owl:Property . } .
	#{ ?pred a owl:SymmetricProperty . ?x ?pred ?y . } 
	#	=> { ?y ?pred ?x .} .


	# Transitive prop. : pas gérable à ce niveau ! 
	# Devrait être fait lors de la construction de la requête interne (TP2Query) ou après...
	# {?P a owl:TransitiveProperty. ?X ?P ?O. ?S ?P ?X} => {?S ?P ?O}.
	#
	# Transitive properties
	#{ ?pred a owl:TransitiveProperty . } 
	#	=> { ?pred a owl:Property . } .
	#{ ?pred a owl:TransitiveProperty . ?x ?pred ?y . ?y ?pred ?z . } 
	#	=> { ?x ?pred ?z .} .


	# Functional Properties
	#{ ?pred a owl:FunctionalProperty . } 
	#	=> { ?pred a owl:Property . } .
	#{ ?pred a owl:FunctionalProperty . ?x ?pred ?y . ?x ?pred ?z . } 
	#	=> { ?y owl:sameAs ?z . } .

	# Inverse Functional Properties
	#{ ?pred a owl:InverseFunctionalProperty . } 
	#	=> { ?pred a owl:Property . } .
	#{ ?pred a owl:InverseFunctionalProperty . ?x ?pred ?y . ?z ?pred ?y . } 
	#	=> { ?x owl:sameAs ?z . } .


#==================================================
#==================================================
#==================================================
if __name__ == "__main__":
	print("main sweep")
	cl = OWLLiteCloser()
	cl.loadOnto("file:example/em-owl.n3")
	cl.loadRML("file:example/EM2EM.rml")

	cl.enrich()

	print('==============')


	s = cl.rml.serialize(format='n3')
	print(s.decode('UTF-8'))

