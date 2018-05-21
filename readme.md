
# RML-Closer projet 
V. 0.1
© P.Serrano-Alvarado, E. Desmontils, Université de Nantes, mai 2018

#Positionnement de l’environnement (Jena, Joda-time…)+ nécessite Ant
```bash
source RML-Closer-env.sh
```

#Pour compiler
```bash
ant
```

#Combining two semantic files
```bash
java -cp $CLASSPATH:RML-Closer.jar Fus file1.ttl file2.ttl
```
or
```bash
riot --out N3 file1.ttl file2.ttl > file.ttl
```

```bash
java -cp $CLASSPATH:RML-Closer.jar Apply em.n3 EM2EM.rml rf
```
```
- Help -
Apply OntoFile RMLFile mode
mode = xy : 
- x = Ontology type : d(l),l(ite),o(wl),r(dfs)
- y = Jena rule mode : n(o), r(dfs), f(ull), t(rans), and only for 'o' type m(icro), (m)i(ni)
```
