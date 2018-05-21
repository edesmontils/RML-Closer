RML-Closer projet V. 0.1
© P.Serrano-Alvarado, E. Desmontils, Université de Nantes, mai 2018

#Positionnement de l’environnement (Jena, Joda-time…)+ nécessite Ant
source env-ed

#Pour compiler
ant

#Combining two semantic files
java -cp $CLASSPATH:RML-Closer.jar Fus file1.ttl file2.ttl
#  or
riot --out N3 file1.ttl file2.ttl > file.ttl

java -cp $CLASSPATH:RML-Closer.jar Apply em.n3 EM2EM.rml rf

- Help -
Apply OntoFile RMLFile mode
mode = xy : 
x : d(l),l(ite),o(wl),r(dfs)
y : n(o), r(dfs), f(ull), t(rans), and only for 'o' type m(icro), (m)i(ni)
