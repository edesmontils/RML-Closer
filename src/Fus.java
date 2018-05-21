  import java.io.*;
  import java.util.*;

  import org.joda.time.*;

  import org.apache.jena.rdf.model.*;
  import org.apache.jena.util.*;
  import org.apache.jena.atlas.logging.*;
  import org.apache.jena.ontology.*;
  import org.apache.jena.query.*;
  import org.apache.jena.datatypes.* ;
  
  /**
   * @author ed
   * @description Combine two parts of a Usage Policy
   */
public class Fus extends Step {
private Model model_get = ModelFactory.createDefaultModel() ;

	public Fus() {super();}

	public void doIt(String myFile1, String myFile2) {
	    model_get.read(myFile1,"N3");
	    model_get.read(myFile2,"N3");
		  model_get.write(System.out,"N3");
	}
 	
	public static void main(String[] args) {
		  String myFile1 = args[0];
		  String myFile2 = args[1];
		  Fus c = new Fus();
		  c.doIt(myFile1,myFile2);
	}
}
