mod model;
use model::*;

/* 
expr_source = "2 + 3 * 4;"
*/

fn model0() -> NodeType {
    return BinOp(Operator::PLUS,
                 Integer(2),
                 BinOp(Operator::TIMES, Integer(3), Integer(4)))
}

/* 
source1 = """
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
    print 2 * 3 + -4;
"""
*/

fn model1() -> NodeType {
    let s1 = PrintStatement(
	       BinOp(Operator::PLUS,
		     Integer(2),
		     BinOp(Operator::TIMES,
                           Integer(3),
			   UnaryOp(Operator::MINUS, Integer(4)))));

    let s2 = PrintStatement(
	       BinOp(Operator::MINUS,
		     Float(2.0),
		     BinOp(Operator::DIVIDE,
                           Float(3.0),
			   UnaryOp(Operator::MINUS, Float(4.0)))));

    let s3 = PrintStatement(
	      BinOp(Operator::PLUS,
		    UnaryOp(Operator::MINUS, Integer(2)),
		    Integer(3)));

    let s4 = PrintStatement(
	      BinOp(Operator::PLUS,
		    BinOp(Operator::TIMES,
			  Integer(2),
			  Integer(3)),
		    Integer(4)));

    Pair(s1, Pair(s2, Pair(s3, Pair(s4, Nil()))))
}

/*
source2 = """
    const pi = 3.14159;  
    var tau float;
    tau = 2.0 * pi;
    print tau;
"""
 */

fn model2() -> NodeType {
    let s1 = ConstDefinition("pi".to_string(), "".to_string(), Float(3.14159));
    let s2 = VarDefinition("tau".to_string(), "float".to_string(), Nil());
    let s3 = AssignmentStatement(NamedLocation("tau".to_string()),
			     BinOp(Operator::TIMES,
				   Float(2.0),
				   LoadLocation(NamedLocation("pi".to_string()))));
    let s4 = PrintStatement(LoadLocation(NamedLocation("tau".to_string())));
    Pair(s1, Pair(s2, Pair(s3, Pair(s4, Nil()))))    
}


/*
source3 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''
 */

fn model3() -> NodeType {
    let s1 = VarDefinition("a".to_string(), "int".to_string(), Integer(2));
    let s2 = VarDefinition("b".to_string(), "int".to_string(), Integer(3));
    let s3 = Pair(PrintStatement(LoadLocation(NamedLocation("a".to_string()))), Nil());
    let s4 = Pair(PrintStatement(LoadLocation(NamedLocation("b".to_string()))), Nil());
    let s5 = IfStatement(BinOp(Operator::LT,
			       LoadLocation(NamedLocation("a".to_string())),
			       LoadLocation(NamedLocation("b".to_string()))),
			 s3, s4);
    Pair(s1, Pair(s2, Pair(s5, Nil())))
}

/*
source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''
 */


fn model4() -> NodeType {
    let s1 = ConstDefinition("n".to_string(), "".to_string(), Integer(10));
    let s2 = VarDefinition("x".to_string(), "int".to_string(), Integer(1));
    let s3 = VarDefinition("fact".to_string(), "int".to_string(), Integer(1));
    let b1 = AssignmentStatement(NamedLocation("fact".to_string()),
				 BinOp(Operator::TIMES,
				       LoadLocation(NamedLocation("fact".to_string())),
				       LoadLocation(NamedLocation("x".to_string()))),
    );
    let b2 = PrintStatement(LoadLocation(NamedLocation("fact".to_string())));
    let b3 = AssignmentStatement(NamedLocation("x".to_string()),
				 BinOp(Operator::PLUS,
				       LoadLocation(NamedLocation("x".to_string())),
				       Integer(1)));
    let s4 = WhileStatement(BinOp(Operator::LT,
				  LoadLocation(NamedLocation("x".to_string())),
				  LoadLocation(NamedLocation("n".to_string()))),
			    Pair(b1, Pair(b2, Pair(b3, Nil()))));

    Pair(s1, Pair(s2, Pair(s3, Pair(s4, Nil()))))
}



fn main() {
    let m0 = model0();
    println!("\n----- MODEL 0");
    to_source(&m0);

    let m1 = model1();
    println!("\n----- MODEL 1");
    to_source(&m1);

    let m2 = model2();
    println!("\n----- MODEL 2");
    to_source(&m2);

    let m3 = model3();
    println!("\n----- MODEL 3");
    to_source(&m3);

    let m4 = model4();
    println!("\n----- MODEL 4");
    to_source(&m4);

}
