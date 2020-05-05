/* model.rs

This file defines the data model for Wabbit programs.  The data
model is a data structure that represents the contents of a program
as objects, not text.  Sometimes this structure is known as an
"abstract syntax tree" or AST.  However, the model is not
necessarily directly tied to the actual syntax of the language.  So,
we'll prefer to think of it as a more generic data model instead.

To do this, you need to identify the different "elements" that make
up a program and encode them into classes.  To do this, it may be
useful to slightly "underthink" the problem. To illustrate, suppose
you wanted to encode the idea of "assigning a value."  Assignment
involves a location (the left hand side) and a value like this:

        location = expression;

To represent this idea, you need to make an object with just those
parts.  In Python, it would look like this:

    class Assignment:
        def __init__(self, location, expression):
            self.location = location
            self.expression = expression

What are "location" and "expression"?  Does it matter? Maybe
not. All you know is that an assignment operator definitely requires
both of those parts.  DON'T OVERTHINK IT.  Further details will be
filled in as the project evolves.

Work on this file in conjunction with the top-level
"script_models.py" file.  Go look at that file and see what program
samples are provided.  Then, figure out what those programs look like 
in terms of data structures.

There is no "right" solution to this part of the project other than
the fact that a program has to be represented as some kind of data
structure that's not "text."   You could use classes. You could use 
tuples. You could make a bunch of nested dictionaries like JSON. 
The key point: it must be a data structure.

Starting out, I'd advise against making this file too fancy. Just
use basic data structures. You can add usability enhancements later.
-----------------------------------------------------------------------------

The following classes are used for the expression example in script_models.py.
Feel free to modify as appropriate.  You don't even have to use classes
if you want to go in a different direction with it.

*/

#![allow(non_snake_case)]

/* Symbolic representation of all valid operators */
#[derive(Debug)]
pub enum Operator {
    PLUS,
    MINUS,
    TIMES,
    DIVIDE,
    LT,
    LE,
    GT,
    GE,
    EQ,
    NE,
}

/* Enum that's used to represent parse tree nodes */
#[derive(Debug)]
pub enum Node {
    Nil,	 
    Integer(i32),
    Float(f64),
    BinOp {
        op: Operator,
	left: Box<Node>,
	right: Box<Node>,
    },
    UnaryOp {
        op: Operator,
        value: Box<Node>,
    },
    PrintStatement(Box<Node>),
    AssignmentStatement {
	location: Box<Node>,
	expression: Box<Node>,
    },
    LoadLocation(Box<Node>),
    ConstDefinition {
	name: String,
	dtype: String,
	value: Box<Node>,
    },
    VarDefinition {
	name: String,
	dtype: String,
	value: Box<Node>,
    },
    IfStatement {
	test: Box<Node>,
	consequence: Box<Node>,
	alternative: Box<Node>,
    },
    WhileStatement {
	test: Box<Node>,
	body: Box<Node>,
    },
    NamedLocation(String),
    Pair(Box<Node>, Box<Node>),
}

pub type NodeType = Box<Node>;

pub fn Integer(value: i32) -> NodeType {
    Box::new(Node::Integer(value))
}

pub fn Float(value: f64) -> NodeType {
    Box::new(Node::Float(value))
}

pub fn BinOp(op: Operator, left: NodeType, right: NodeType) -> NodeType {
    Box::new(Node::BinOp { op, left, right })
}

pub fn UnaryOp(op: Operator, value: NodeType) -> NodeType {
    Box::new(Node::UnaryOp {op, value })
}

pub fn PrintStatement(expr: NodeType) -> NodeType {
    Box::new(Node::PrintStatement(expr))
}

pub fn AssignmentStatement(location: NodeType, expression: NodeType) -> NodeType {
    Box::new(Node::AssignmentStatement {location, expression})
}

pub fn LoadLocation(location: NodeType) -> NodeType {
    Box::new(Node::LoadLocation(location))
}

pub fn NamedLocation(name: String) -> NodeType {
    Box::new(Node::NamedLocation(name))
}

pub fn ConstDefinition(name: String, dtype: String, value: NodeType) -> NodeType {
    Box::new(Node::ConstDefinition {name, dtype, value})
}

pub fn VarDefinition(name: String, dtype: String, value: NodeType) -> NodeType {
    Box::new(Node::VarDefinition {name, dtype, value})
}

pub fn IfStatement(test: NodeType, consequence: NodeType, alternative: NodeType) -> NodeType {
    Box::new(Node::IfStatement {test, consequence, alternative })
}

pub fn WhileStatement(test: NodeType, body: NodeType) -> NodeType {
    Box::new(Node::WhileStatement {test, body })
}

pub fn Pair(stmt1: NodeType, stmt2: NodeType) -> NodeType {
    Box::new(Node::Pair(stmt1, stmt2))
}

pub fn Nil() -> NodeType {
    Box::new(Node::Nil)
}

/* ------ Debugging function to convert a model into source code (for easier viewing) */

pub fn to_source(node: &Node) -> () {
    use Node::*;
    match node {
	Integer(val) => {
            print!("{}", val);
	},
	Float(val) => {
            print!("{}", val);
	},
	BinOp { op, left, right } => {
            to_source(left);
    	    match op {
		Operator::PLUS => print!(" + "),
   		Operator::MINUS => print!(" - "),
		Operator::TIMES => print!(" * "),
		Operator::DIVIDE => print!(" / "),
		Operator::LT => print!(" < "),
		Operator::LE => print!(" <= "),
		Operator::GT => print!(" > "),
		Operator::GE => print!(" <= "),
		Operator::EQ => print!(" == "),
		Operator::NE => print!(" != "),		
	    }
	    to_source(right);
	},
	UnaryOp { op, value } => {
            match op {
		Operator::PLUS => print!("+"),
		Operator::MINUS => print!("-"),
		_ => print!(""),
            }
            to_source(value);
	},
	PrintStatement(val) => {
            print!("print ");
	    to_source(val);
	    print!(";\n");
	},
	AssignmentStatement { location, expression } => {
	    to_source(location);
	    print!(" = ");
	    to_source(expression);
	    print!(";\n");
	},
	VarDefinition { name, dtype, value } => {
	    print!("var {0} {1}", name, dtype);
	    if let Nil = **value { } else {
		print!(" = ");
		to_source(value);
	    }
	    print!(";\n");
	},
	ConstDefinition { name, dtype, value } => {
	    print!("const {0} {1} = ", name, dtype);
	    to_source(value);
	    print!(";\n");
	},
	NamedLocation(name) => {
	    print!("{}", name);
	},
	LoadLocation(loc) => {
	    to_source(loc);
	},
	IfStatement { test, consequence, alternative } => {
	    print!("if ");
	    to_source(test);
	    print!("{}", " {\n");
	    to_source(consequence);
	    print!("{}", "} else {\n");
	    to_source(alternative);
	    print!("{}", "}\n");
	},
	WhileStatement { test, body } => {
	    print!("while ");
	    to_source(test);
	    print!("{}", " {\n");
	    to_source(body);
	    print!("{}", "}\n");
	},
	Pair(node1, node2) => {
	    to_source(node1);
	    to_source(node2);
	},
	Nil => { },
	_ => {
            print!("{:?}", node);
	}
    }
}
