import java.io.*;
import java.util.*;

import org.joda.time.*;

import org.apache.jena.rdf.model.*;
import org.apache.jena.util.*;
import org.apache.jena.atlas.logging.*;
import org.apache.jena.ontology.*;
import org.apache.jena.query.*;
import org.apache.jena.datatypes.* ;

import org.apache.jena.reasoner.*;
import org.apache.jena.reasoner.rulesys.*;
import org.apache.jena.vocabulary.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

  /**
   * @author ed
   */
public class Apply extends Step {

	OntModelSpec oms ;
	String rulesFile ;

	public Apply(char reasonnerType, char reasonnerMode) {
		super();

		// type in : d(l),l(ite),o(wl),r(dfs)
		// mode in : n(o), r(dfs), f(ull), t(rans), 
		//   and only for 'o' : m(icro), (m)i(ni)
		switch(reasonnerType) {
			case 'd' :
				switch(reasonnerMode) {
					case 'n' : 
						oms = OntModelSpec.OWL_DL_MEM; // A specification for OWL DL models that are stored in memory and do no additional entailment reasoning
						break;
					case 'r' :
						oms = OntModelSpec.OWL_DL_MEM_RDFS_INF; // A specification for OWL DL models that are stored in memory and use the RDFS inferencer for additional entailments
						break;
					case 'f' :
						oms = OntModelSpec.OWL_DL_MEM_RULE_INF; // A specification for OWL DL models that are stored in memory and use the OWL rules inference engine for additional entailments
						break;
					case 't':
						oms = OntModelSpec.OWL_DL_MEM_TRANS_INF; // A specification for OWL DL models that are stored in memory and use the transitive inferencer for additional entailments
						break;
					default : break;
				}
				rulesFile = "owl-rules.jr" ;
				break;
			case 'l' :
				switch(reasonnerMode) {
					case 'n' : 
						oms = OntModelSpec.OWL_LITE_MEM; // A specification for OWL Lite models that are stored in memory and do no entailment additional reasoning
						break;
					case 'r' :
						oms = OntModelSpec.OWL_LITE_MEM_RDFS_INF; // A specification for OWL Lite models that are stored in memory and use the RDFS inferencer for additional entailments
						break;
					case 'f' :
						oms = OntModelSpec.OWL_LITE_MEM_RULES_INF; // A specification for OWL Lite models that are stored in memory and use the OWL rules inference engine for additional entailments
						break;
					case 't':
						oms = OntModelSpec.OWL_LITE_MEM_TRANS_INF; // A specification for OWL Lite models that are stored in memory and use the transitive inferencer for additional entailments
						break;
					default : break;
				}
				rulesFile = "owl-lite-rules.jr" ;
				break;
			case 'o' :
				switch(reasonnerMode) {
					case 'n' : 
						oms = OntModelSpec.OWL_MEM; // A specification for OWL models that are stored in memory and do no additional entailment reasoning
						break;
					case 'r' :
						oms = OntModelSpec.OWL_MEM_RDFS_INF; // A specification for OWL models that are stored in memory and use the RDFS inferencer for additional entailments
						break;
					case 'f' :
						oms = OntModelSpec.OWL_MEM_RULE_INF; // A specification for OWL models that are stored in memory and use the OWL rules inference engine for additional entailments
						break;
					case 't':
						oms = OntModelSpec.OWL_MEM_TRANS_INF; // A specification for OWL models that are stored in memory and use the transitive inferencer for additional entailments
						break;
					case 'm':
						oms = OntModelSpec.OWL_MEM_MICRO_RULE_INF; // A specification for OWL models that are stored in memory and use the micro OWL rules inference engine for additional entailments
						break;
					case 'i':
						oms = OntModelSpec.OWL_MEM_MINI_RULE_INF; // A specification for OWL models that are stored in memory and use the mini OWL rules inference engine for additional entailments
						break;
					default : break;
				}
				rulesFile = "owl-rules.jr" ;
				break;
			case 'r' :
				switch(reasonnerMode) {
					case 'n' : 
						oms = OntModelSpec.RDFS_MEM; // A specification for RDFS ontology models that are stored in memory and do no additional entailment reasoning
						break;
					case 'f' :
						oms = OntModelSpec.RDFS_MEM_RDFS_INF; // A specification for RDFS ontology models that are stored in memory and use the RDFS inferencer for additional entailments
						break;
					case 't':
						oms = OntModelSpec.RDFS_MEM_TRANS_INF; // A specification for RDFS ontology models that are stored in memory and use the transitive reasoner for entailments
						break;
					default : break;
				}
				rulesFile = "rdfs-rules.jr" ;
				break;
			default: break;
		}
	}

	public static InfModel processRulesF(String fileloc, Model modelIn) {return processRules(fileloc, modelIn, "forward");}

	public static InfModel processRulesB(String fileloc, Model modelIn) {return processRules(fileloc, modelIn, "backward");}

	public static InfModel processRulesH(String fileloc, Model modelIn) {return processRules(fileloc, modelIn, "hybrid");}

	public static InfModel processRules(String fileloc, Model modelIn, String method) {
	 // create a simple model; create a resource and add rules from a file
	 Resource configuration = modelIn.createResource();
	 configuration.addProperty(ReasonerVocabulary.PROPruleSet, fileloc );
	 configuration.addProperty(ReasonerVocabulary.PROPruleMode, method);
	 // Create an instance of a reasoner
	 Reasoner reasoner = GenericRuleReasonerFactory.theInstance().create(configuration);

	 // Now with the rawdata model & the reasoner, create an InfModel
	 InfModel infmodel = ModelFactory.createInfModel(reasoner, modelIn);
	 ValidityReport vr = infmodel.validate();
	 if (!vr.isClean()) {
	 	Iterator<ValidityReport.Report> it = vr.getReports();
	 	while(it.hasNext()) {
	 		ValidityReport.Report vrr = it.next();
	 		System.err.println((vrr.isError()?"err:":"war:") + vrr.getDescription());
	 	}
	 }
	 return infmodel;
	}

	public void doIt(String ontoFile, String rmlFile) {

		OntModel onto = ModelFactory.createOntologyModel(oms, ModelFactory.createDefaultModel()) ;
	    onto.read(ontoFile,"N3");

	    OntModel rml = ModelFactory.createOntologyModel(oms, ModelFactory.createDefaultModel()) ;
		rml.read(rmlFile,"N3");

		OntModel owlmodel = ModelFactory.createOntologyModel(oms, ModelFactory.createDefaultModel()) ;
	    owlmodel.add(onto);
		owlmodel.add(rml);

		Statement new_tripple = owlmodel.createStatement(
		    	                             owlmodel.createResource(ns.concat("cpt")),
		    	                             owlmodel.createProperty(ns.concat("val")),
		    	                             owlmodel.createTypedLiteral(new Integer(0))  ) ;
		owlmodel.add(new_tripple);

		// owlmodesl.write(System.out,"N3");

	    InfModel inferredModel = processRulesF(rulesFile,owlmodel);
	    Model newStms = inferredModel.getDeductionsModel();

	    owlmodel = ModelFactory.createOntologyModel(oms, ModelFactory.createDefaultModel()) ;
	    owlmodel.add(onto);
	    owlmodel.add(rml);

	    Model suppressStms = owlmodel.difference(inferredModel);  

	    // System.out.println("+++++++++++++++++++ to add +++++++++++++++++++++++");
	    // newStms.write(System.out, "N3") ;
	    // System.out.println("+++++++++++++++++++ to suppress +++++++++++++++++++++++");
	    // suppressStms.write(System.out, "N3") ;
	    // System.out.println("++++++++++++++++++++++++++++++++++++++++++");
	    StmtIterator it = suppressStms.listStatements();
	    while (it.hasNext()) {
	    	Statement st = it.next();
	    	// System.out.println(st);
	    	rml.remove(st);
	    }
	    // System.out.println("++++++++++++++++++++++++++++++++++++++++++");

	    // Statement sts = getUniqueSt(newStms,ns,"cpt");
		// newStms.remove(sts);

	    rml.add(newStms);
      	rml.write(System.out, "N3") ;
	}
 	
	public static void main(String[] args) {
		if (args.length == 3) {
		  String myOnto = args[0];
		  String myRML = args[1];
		  String mode = args[2] ;
		  char reasonnerType = mode.charAt(0) ; // d(l),l(ite),o(wl),r(dfs)
		  char reasonnerMode = mode.charAt(1) ; // n(o), r(dfs), f(ull), t(rans), and only for 'o' type m(icro), (m)i(ni)
		  Apply c = new Apply(reasonnerType,reasonnerMode);
		  c.doIt(myOnto, myRML);
		} else {
			System.out.println("Apply OntoFile RMLFile mode");
			System.out.println("mode = xy : ");
			System.out.println(" - x : d(l),l(ite),o(wl),r(dfs)");
			System.out.println(" - y : n(o), r(dfs), f(ull), t(rans), and only for 'o' type m(icro), (m)i(ni)");
		} 
	}
}
