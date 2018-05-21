import java.io.*;
import java.util.*;

import org.xml.sax.*;
import javax.xml.parsers.SAXParserFactory; 
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser; 
import org.xml.sax.helpers.DefaultHandler;

import org.apache.jena.rdf.model.*;
import org.apache.jena.util.*;
import org.apache.jena.atlas.logging.*;
import org.apache.jena.ontology.*;
import org.apache.jena.query.*;

import org.apache.jena.vocabulary.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

  /**
   * @author ed
   */
public class Step {
	private String base="";
	static protected OntModel owlmodel = null;

	public String ns_rr   = "http://www.w3.org/ns/r2rml#" ;
	public String ns_rml   = "http://semweb.mmlab.be/ns/rml#" ;
	public String ns_ql   = "http://semweb.mmlab.be/ns/ql#" ;

	public Step() {}


	// "apply" applique une requete SPARQL dans l'env. de l'ontologie

	protected Model apply(Model m, String queryString) {
		Query query = QueryFactory.create(queryString);
		QueryExecution qexec = QueryExecutionFactory.create(query, m);
		Model resultModel = qexec.execConstruct();
		qexec.close();
		return resultModel ;
	}

	public Statement getUniqueSt(Model m, String ns, String prop) {
		StmtIterator sts = m.listStatements(null,
			                                m.createProperty(ns,prop),
			                                (RDFNode)null);
		if (sts.hasNext()) {
			Statement st = sts.nextStatement() ;
			return st;
		} else return null;
	}
	
	public Set<Statement> getAllSt(Model m, String ns, String prop) {
		StmtIterator sts = m.listStatements(null,
			                                m.createProperty(ns,prop),
			                                (RDFNode)null);
		Set<Statement> ens = new HashSet<Statement>();
		while (sts.hasNext()) {
			Statement st = sts.nextStatement() ;
			ens.add(st);
		} 
		return ens;
	}
	
	public Set<Statement> getAllSt(Model m, Resource r) {
		StmtIterator sts = m.listStatements(r,
			                                null,
			                                (RDFNode)null);
		Set<Statement> ens = new HashSet<Statement>();
		while (sts.hasNext()) {
			Statement st = sts.nextStatement() ;
			ens.add(st);
		} 
		return ens;
	}


	public static void printStatements(Model m, Resource s, Property p, Resource o) {
		PrintUtil.registerPrefix("x", "http://www.codesupreme.com/#");
		for (StmtIterator i = m.listStatements(s,p,o); i.hasNext(); ) {
			Statement stmt = i.nextStatement();
			System.out.println(" - " + PrintUtil.print(stmt));
		}
	}
	
	public static void main(String[] argv) {
		Step s = new Step();
	}
}
