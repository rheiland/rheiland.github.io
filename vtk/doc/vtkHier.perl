#!/usr/bin/perl
# ---------------------------------------------------------------------
# Description:  See help routine below.
# Created by Tom Smith (smitty@kcc.com).  You're free to copy, modify,
# and redistribute this script, and use it for any purpose you like,
# so long as you clearly document changes as yours and not mine.
# 
# In no event shall the authors or distributors be liable to any party for
# direct, indirect, special, incidental, or consequential damages arising out
# of the use of this software, its documentation, or any derivatives thereof,
# even if the authors have been advised of the possibility of such damage.
# 
# The authors and distributors specifically disclaim any warranties, including,
# but not limited to, the implied warranties of merchantability, fitness for a
# particular purpose, and non-infringement.  This software is provided on an
# "as is" basis, and the authors and distributors have no obligation to provide
# maintenance, support, updates, enhancements, or modifications.
# ---------------------------------------------------------------------
# Changelog:
# 991014 Smitty created.
# 991019 Smitty changed Version to 2.
# 991019 Smitty changed to find methods defined with all the macros in
#	 VtkSetGet.h, e.g. the SetObjectMacro.
# 991020 Smitty changed Version to 3.
# 991021 Smitty added -f command line switch.
# 991101 Smitty added -q command line switch.
# 991104 Smitty added -w and -x command line switches.
# 991125 Smitty added -r command line switch.
# ---------------------------------------------------------------------
select (STDERR);
$| = 1;
select (STDOUT);
$q='"'; # Used globally to put quotation marks in strings.

sub help {
# ---------------------------------------------------------------------
# Prints help text.
# ---------------------------------------------------------------------
	print<<END;
Description:
	vtkfind, Version 3.
	Scans files in the vtk source directory to report information
	about vtk object classes, e.g. all the children with
	inheritance from a base class, or all the parents from
	which a class has inherited, or to which classes a given
	method name is native to.

Usage: vtkfind [-a] [-c] [-d dir] [-e <edit command>] \\
		[-f] [-h] [-m] [-p] [-q] [-r] [-s] [-w] <name>

-a indicates <name> is to remain as is.  When using -h or -s, without
	-a you can leave off the vtk prefix and vtkfind will add it
	for you.  Also, you don't need to worry about capitalization.
	For example, "vtkfind -a SetDebug" would report -
		/opt/vtk/common/vtkObject.h     vtkObject/void SetDebug(...
	and "vtkfind -h object" would report -
		/opt/vtk/common/vtkObject.h
	When using -m or -f without -a, vtkfind does the search
	case-insensitive, but it doesn't automatically prefix "vtk"
	to <name> for you, since few, if any, methods and fields
	have that prefix.

-c indicates find all the children of the class <name>, i.e. all the
	classes for which <name> is an inherited class.  This option
	is relatively expensive, since all *.h files must be scanned.

-d dir
	Dir is the directory for the vtk source.  The default is /opt/vtk.

-e <edit command>
	Indicates if a filename is found it is to be appended to
	<edit command> and executed.  For example
	"vtkfind -e 'vi -R' -h object" would cause the command
	"vi -R /opt/vtk/common/vtkObject.h" to be executed.
	Use -e in conjunction with -m cautiously.  The command
	"vtkfind -e 'vi -R' insertnextcell" will put you in edit on
	four files.

-f indicates all the *.h files are to be searched, looking for fields,
	i.e. data members, with the specified name.

-h indicates the full path to <name>.h is to be found,
	e.g. "vtkfind -h vtkunstructuredgrid" might list
	/opt/vtk/common/vtkUnstructuredGrid.h.  Can be used in
	conjunction with -e (see above). -h is the default if
	neither -m nor -s is specified.

-m indicates all the *.h files in the vtk source directory (see -d)
	are to be searched to find the classes to which the specified
	method is native.  Can be used in conjunction with -e (see
	above).

-p indicates find all the parents of the class <name>, i.e. all the
	classes from which <name> has inherited.

-q indicates all the *.h files in the vtk source directory (see -d)
	are to be searched to find the classes that contain pointers
	to the specified object name.

-r indicates name.html and name_form.html documents are to be written,
	and also child.html and child_form.html documents for all
	children of the named base class.  parent.html and parent_form.html
	documents are also created if they don't exist for any parent
	of the named class.  Be careful about what you ask for.  Consider
	for example what will be generated if you enter "vtkfind -r object".

-s indicates the full path to <name>.cxx is to be found,
	e.g. "vtkfind -s vtkunstructuredgrid" might list
	/opt/vtk/common/vtkUnstructuredGrid.cxx.  Can be used in
	conjunction with -e (see above).

-x indicates an html document is to be printed on stdout, describing
	the field layout of the specified class.

-w indicates an html document is to be printed on stdout, describing
	either the named method if -m is also specified or a class
	if -h is also specified.  The document will contain pointers
	to the header (.h) and source (.cxx) files for the class,
	pointers to its base class, and pointers to html documents
	for all classes derived from this class.
END
	exit;
} # End help.

sub getbasename {
# ---------------------------------------------------------------------
# Returns the basename, less suffix, from the full path.
# ---------------------------------------------------------------------
	local($path)=@_;
	local(@q,$basename,$ret);

        @q=split("/",$path);
        $basename=pop(@q);
	if($basename =~ /^(.*)\..*/) {
		$ret=$1;
	} else {
		$ret=$basename;
	}
	return($ret);
} # End getbasename.

sub getchildren {
# ---------------------------------------------------------------------
# Called to get the sorted names of all the child classes of the named
# class.
# ---------------------------------------------------------------------
	local($name)=@_;
	local($i,$line,@lines);

	chop(@lines=`vtkfind -c $name`);
	die("Internal error") unless(scalar(@lines));
	if(@lines[0] eq "Not Found: $name") {
		@lines=();
	} else {
		for($i=0; $i<scalar(@lines); $i++) {
			$lines[$i] =~ s/^.*\t(.*)/$1/;
		} 
		@lines=sort(@lines);
	}
	return(@lines);
} # End getchildren.

sub getclass {
# ---------------------------------------------------------------------
# Called to get the declaration statement for the named class.
# Given the statement is of the form "class $Name {$body};" getclass
# returns ("class $Name",$body).
# ---------------------------------------------------------------------
	local($name)=@_;
	local($body,$cursor,$head,$ix,@lines,$Name,$path,$stmt);

	($path,$Name)=&pathsplit($name,".h");
	print("getclass: name=$name, path=$path, Name=$Name\n") if($Debug);
	@lines=&getlines("$path/${Name}.h");
	$cursor=$ix=0; # Indicate it's startup time.
	while(1) {
		($cursor,$ix,$stmt)=&scanner($cursor,$ix,\@lines);
		print("getclass loop: cursor=$cursor ix=$ix stmt='$stmt'\n")
			if($Debug);
		return() if($stmt eq ""); # Return empty array at eof.
		$stmt=&stripcom($stmt);
		next unless($stmt =~
			/^class\s+VTK_EXPORT\s+(\w+)\s+([^{]*){(.*)};$/);
		$class=$1;
		next unless($class eq $Name);
		$head="class VTK_EXPORT $class $2";
		$body=$3;
		print("getclass returning head='$head' body='$body'\n")
			if($Debug);
		return($head,$body);
	}
} # End getclass.

sub getlines {
# ---------------------------------------------------------------------
# Called to read the specified file, returning an array of its lines.
# ---------------------------------------------------------------------
	local($file)=@_;
	local(@lines);

	die("ERROR: Unable to read $file\n") unless (open(IN,$file));
	chop(@lines=<IN>);
	close(IN);
	return(@lines);
} # End getlines.

sub getparents {
# ---------------------------------------------------------------------
# Called to get the names of the parents for the specified class.
# Returns empty array if $name is a topmost class, and dies if $name
# isn't a legitimate vtk class.
# ---------------------------------------------------------------------
	local($name)=@_;
	local($i,$line,@lines,$parent);

	chop(@lines=`vtkfind -p $name`);
	die("getparent internal error") unless($line=shift(@lines));
	die("${name} is not a vtk object class.")
		if($line eq "Not Found: $name");
	if(scalar(@lines)) { # Class is topmost if @lines is empty.
		for($i=0; $i<scalar(@lines); $i++) {
			$lines[$i]=$1 if($lines[$i] =~ /^.*\t(\w+)\/.*/);
		}
	}
	return(@lines);
} # End getparents.

sub getpath {
# ---------------------------------------------------------------------
# Called to search directory $dir for the specified name.
# Returns the full path if found.
# ---------------------------------------------------------------------
	local($name,$suffix)=@_;
	local($cmd,$file,@files,$ret);

	$cmd="find $dir/* -type f -name '*$suffix'";
	chop(@files=`$cmd`);
	$ret="";
	foreach $file (@files) {
		last if($ret=&namecheck($file,$name,$suffix));
	}
	return($ret);
} # End getpath.

sub html {
# ---------------------------------------------------------------------
# Called to generate an html document on stdout describing either a
# method (action=m) or a class (action=h).
# ---------------------------------------------------------------------
	local($name,$action)=@_;
	local($ret);

	if($action eq "h") {
		$ret=($doform) ? &htmlform($name,"STDOUT") :
			&htmlclass($name,"STDOUT");
	} elsif($action eq "m") {
		$ret=&htmlmethod($name,"STDOUT");
	} else {
		die("ERROR:  I don't know what action to take.");
	}
	return($ret);
} # End html.

sub htmlboth {
# ---------------------------------------------------------------------
# Called to generate name.html and name_form.html documents for the
# named class.
# ---------------------------------------------------------------------
	local($name)=@_;
	local($basename,$filename,$path);

	die("Can't determine path to $name")
		unless($path=&getpath($name,".h"));
	$basename=&getbasename($path);
	&htmlopen("$basename.html");
	&htmlclass(lc($basename),"OUT");
	close(OUT);
	&htmlopen("${basename}_form.html");
	&htmlform(lc($basename),"OUT");
	close(OUT);
} # End htmlboth.

sub htmlcindex {
# ---------------------------------------------------------------------
# Called to generate an html document on $out indexing all the classes
# identified by the keys of associative array %class_xref.
# ---------------------------------------------------------------------
	local($out)=@_;
	local($key);

	print $out <<END;
<html>
<head>
<title>class_index</title>
</head>
<body>
--------------------------------------CLASS_INDEX
<br>Vtk Class Index
<p>
<ul>
<li><a href="index.html">Back to vtk main page.</a>
END
	foreach $key (sort keys %class_xref) {
		print $out <<END;
<li><a href="$key.html">$key</a>
END
	}
	print $out <<END;
</ul>
</body>
</html>
END
} # End htmlcindex.

sub htmlclass {
# ---------------------------------------------------------------------
# Called to generate an html document on $out describing a class.
# ---------------------------------------------------------------------
	local($name,$out)=@_;
	local($child,@children,$key,$line,@lines,
		$Name,$path,$pth,%wrk);

	($pth,$Name)=&pathsplit($name,".h");
	$class_xref{$Name}=1; # Save name of class.
	print $out <<END;
<html>
<head>
<title>$Name</title>
</head>
<body>
------------------------------------------$Name
<br>
<p>
<ul>
<li>
<a href="class_index.html">Back to main vtk object index.</a>
<li>
Header is <a href="
/cgi-bin/plaintext.cgi?path=$pth&file=$Name.h">
$pth$Name.h</a>
END
	chop(@lines=`vtkfind -s $name`);
	die("Internal error") unless(scalar(@lines));
	$line=@lines[0];
	if($line eq "Not Found: $name") {
		print $out <<END;
<li>
There is no ${Name}.cxx.
END
	} else {
		$line =~ /^(.*\/)(\w+)\.cxx/;
		$pth=$1;
		$Name=$2;
		print $out <<END;
<li>
Source is <a href="
/cgi-bin/plaintext.cgi?path=$pth&file=$Name.cxx">
$pth$Name.cxx</a>
END
	}
	print $out <<END;
<li>
<a href="${Name}_form.html">Layout.</a>
<li>
<a href="${Name}_notes.html">Notes.</a>
END
	chop(@lines=`vtkfind -p $name`);
	die("Internal error") unless(scalar(@lines));
	$line=@lines[0];
	if($line eq "Not Found: $name") {
		print $out <<END;
<li>
${Name} is not a vtk object class.
END
	} elsif(1 == scalar(@lines)) {
		print $out <<END;
<li>
This class is topmost.  It is not derived from any other class.
END
	} else {
		$line =~ /^.*\t\w+\/(.*)/;
		$parent=$1;
		print $out <<END;
<li>
<a href="$parent.html">$parent</a>
is a public base class of $Name.
END
	}
	@children=&getchildren($name);
	if(0 == scalar(@children)) {
		print $out <<END;
<li>
${Name} is not a base class of any other class.
END
	} else {
		print $out <<END;
<li>
${Name} is a public base class of -
	<ul>
END
		foreach $child (@children) {
			print $out("\t<li><a href=${q}$child.html${q}>$child<\/a>\n");
		} 
		print $out("\t</ul>\n");
	}
	chop(@lines=`vtkfind -q $name`);
	die("Internal error") unless(scalar(@lines));
	$line=@lines[0];
	if($line eq "Not Found: $name") {
		print $out <<END;
<li>
${Name} is not pointed to by any other class.
END
	} else {
		print $out <<END;
<li>
Classes that have pointers to $Name objects:
	<ul>
END
		foreach $line (@lines) {
			$line =~ s/^.*\/(\w+)\.h\t.*/\t<li><a href="$1.html">$1<\/a>/;
			$wrk{$1}=$line;
		} 
		foreach $key (sort keys %wrk) {
			print $out("$wrk{$key}\n");
		}
		print $out("\t</ul>\n");
	}

	&htmlclass_methods($name,$out); # Go itemize class methods.

	print $out <<END;
</ul>
</body>
</html>
END
	return(1);
} # End htmlclass.

sub htmlclass_methods {
# ---------------------------------------------------------------------
# Called to generate html on $out describing the methods
# native to the named class.
# ---------------------------------------------------------------------
	local($name,$out)=@_;
	local($body,$cursor,$descr,$head,$hit,$i,$ix,@keys,$len,
		$line,@lines,$method,%methods,$stmt,$type);

	# The vtk developers put comments in the header (.h) files
	# in a standard format in front of each method declaration.
	# This first loop gathers these descriptions for later use.
	($path,$Name)=&pathsplit($name,".h");
	@lines=&getlines("$path/${Name}.h");
	$hit=$i=0;
	while ($i<scalar(@lines)) {
		$line=$lines[$i];
		if ($hit) {
			if ($line =~ /^\s*\/\/\s*(.*)/) {
				$descr.=" $1"; # Save description segment.
			} else {
				# End of description.  How see if we can
				# identify a method declaration.
				$hit=0;
				($cursor,$ix,$stmt)=&scanner(0,$i,\@lines);
				$methods{$method}=$descr if($method=
					&htmlclass_methods_name($stmt));
			}
		} elsif ($line =~ /^\s*\/\/\s+Description:/) {
			# Found start of description.
			$hit=1;
			$descr="";
		}
		$i++;
	}

	# This loop does a better job syntactically of scanning the
	# class statement, looking for method declarations, which will
	# be added to the %methods array.
	($head,$body)=&getclass($name); # Get class statement.
	@lines=($body); # what's between braces {}.
	$cursor=$ix=0; # Indicate it's startup time.
	while(1) { # parse class declaration body.
		($cursor,$ix,$stmt)=&scanner($cursor,$ix,\@lines);
		last if($stmt eq "");
		next unless($method=&htmlclass_methods_name($stmt));
		$methods{$method}="." unless(defined($methods{$method}));
			# Keep track of all unique method names.
		next;
	}
	@keys = sort keys %methods;
	if(scalar(@keys)) {
		# We found at least one method declaration.
		# Generate start of ul, if we haven't already.
		print $out (
			"<li>\n".
			"Methods native to this class:\n".
			"\t<ul>\n"
		);
		foreach $key (@keys) {
			$descr=$methods{$key};
			$descr="" if($descr eq ".");
			print $out (
			"\t<li><a href=$q${key}_method.html$q>$key</a> $descr\n"
			);
			$method_xref{$key}=1; # List of unique method names.
			if(defined($method_classes{$key})) {
				# List of classes for which method $key native.
				$method_classes{$key}.=" $Name";
			} else {
				$method_classes{$key}=$Name;
			}
		}
		print $out ( "\t</ul>\n" );
	} else {
		print $out (
			"<li>\n".
			"There are no methods native to this class.\n"
		);
	}
} # End htmlclass_methods.

sub htmlclass_methods_name {
# ---------------------------------------------------------------------
# Called to test if $stmt is a method declaration.  Returns the
# method name if so, and "" otherwise.
# ---------------------------------------------------------------------
	local($stmt)=@_;
	local($align,$friend,$len,$method,$type);

	$method=""; # Default.
	if ($stmt =~ /^\s*(vtk(.*)Macro)\((\w+)\s*,.*\)/) {
		# $1 is type, e.g. SetString, GetString, SetClamp, etc.
		# $2 is component of method name after Set or Get,
		#    e.g. FileName.
		$type=$1; # Save Macro type for further parsing.
		$method=$2; # Save partial method name.
		return("") unless ($type =~ /^([SG]et).*/);
		$method="$1$method"; # Full method name.
	} else {
		($len,$align,$friend,$stmt)=&parseb($stmt);
		return("") if($friend || $len==0);
		return("") unless($stmt =~ /(\w+)\s*\(.*/);
		$method=$1;
	}
	return($method);
} # End htmlclass_methods_name.

sub htmlform {
# ---------------------------------------------------------------------
# Called to generate an html document on stdout describing the layout
# of fields for a class.
# ---------------------------------------------------------------------
	local($name,$out)=@_;
	local($adjust,$alignment,$body,$buffer,$ch,$class,$cursor,$file,$head,
		$hit,$ix,$len,$line,@lines,$Name,$offset,$parent,@parents,
		$pth,$stmt);

	($pth,$Name)=&pathsplit($name,".h");
	print $out <<END;
<html>
<head>
<title>${Name}_form</title>
</head>
<body>
------------------------------------------${Name}_form
<br>$Name layout
<p><pre>
END

	@parents=&getparents($name);
	if($parent=shift(@parents)) {
		$file="${parent}_form.html";
		@lines=&getlines($file);
		$hit=0;
		foreach $line (@lines) {
			if($hit) {
				last if($line =~ /^<\/pre>/);
				$offset=$1 if($line =~ /^\s*(\d+)\s*$/);
				print $out("$line\n"); # Add to current.
			} elsif($line =~ /^<p><pre>/) {
				$hit=1;
			}
		}
	} else {
		$offset=0; # Class is topmost.
	}
	print $out("$Name\n");
	printf $out("%3d %3d space for $parent\n",0,$offset) if($parent);

	($head,$body)=&getclass($name); # Get class statement.
	print("htmlform: body='$body'\n") if($Debug);
	@lines=($body); # what's between braces {}.
	$cursor=$ix=0; # Indicate it's startup time.
	while(1) { # parse class declaration body.
		($cursor,$ix,$stmt)=&scanner($cursor,$ix,\@lines);
		last if($stmt eq "");
		($len,$alignment)=&parsea($stmt);
		next unless($len);
		$offset+=$alignment-$adjust
			if($adjust=$offset%$alignment);
		$stmt =~ s/^(.*)\s*\/\*\s*(.*)\s*\*\/\s*;/$1; \/\/ $2/;
		$stmt =~ s/\s*;/;/;
		printf $out("%3d %3d %s\n",$offset,$len,$stmt);
		$offset+=$len;
	}
	printf $out("%3d\n",$offset); # Print final length.
	print $out <<END;
</pre>
</body>
</html>
END
	return(1);
} # End htmlform.

sub htmlmethod {
# ---------------------------------------------------------------------
# Called to generate an html document on stdout describing a method.
# ---------------------------------------------------------------------
	local($name,$out)=@_;
	local($line,@lines,$Name,$ret);

	chop(@lines=`vtkfind $name`);
	return(0) unless(scalar(@lines));
	$line=@lines[0];
	return(0) if($line eq "Not Found: $name");
	return(0) unless($Name=&searchmethod($line,lc($line),$name));
	print $out <<END;
<html>
<head>
<title>$Name</title>
</head>
<body>
------------------------------------------$Name
<br>
<p>
<ul>
END
	foreach $line (@lines) {
		if ($line =~ /^.*\t(\w+)\/.*/) {
			print $out <<END;
<li><a href="$1.html">$1</a>
END
		}
	}
	print $out <<END;
</ul>
</body>
</html>
END
	return(1);
} # End htmlmethod.

sub htmlmethods {
# ---------------------------------------------------------------------
# Called to generate <method name>_method.html documents for each
# key to associative array %method_classes.  $method_classes{"<method_name>"}
# will be set to a string consisting of the blank-delimited
# names of all the classes for which <method_name> is native.
# ---------------------------------------------------------------------
	local($class,$file,$key);

	foreach $key (sort keys %method_classes) {
		$file="${key}_method.html";
		&htmlopen($file);
		print OUT <<END;
<html>
<head>
<title>${key}_method</title>
</head>
<body>
--------------------------------------${key}_METHOD
<br>Classes where Method $key is native
<p>
<ul>
<li><a href="${key}_notes.html">Notes (if any).</a>
END
		foreach $class (split(/\s+/,$method_classes{$key})) {
			print OUT <<END;
<li><a href="$class.html">$class</a>
END
		}
		print OUT <<END;
</ul>
</body>
</html>
END
		close(OUT);
	}
} # End htmlmethods.

sub htmlmindex {
# ---------------------------------------------------------------------
# Called to generate an html document on $out indexing all the methods
# identified by the keys of associative array %method_xref.
# ---------------------------------------------------------------------
	local($out)=@_;
	local($key);

	print $out <<END;
<html>
<head>
<title>method_index</title>
</head>
<body>
--------------------------------------METHOD_INDEX
<br>Vtk Method Index
<p>
<ul>
<li><a href="index.html">Back to vtk main page.</a>
END
	foreach $key (sort keys %method_xref) {
		print $out <<END;
<li><a href="${key}_method.html">$key</a>
END
	}
	print $out <<END;
</ul>
</body>
</html>
END
} # End htmlmindex.

sub htmlopen {
# ---------------------------------------------------------------------
# Called to open the specified filename.
# ---------------------------------------------------------------------
	local($filename)=@_;

	die("ERROR: Unable to open $filename\n")
		unless(open(OUT,">$filename"));
	print STDERR "Processing $filename\n";
} # End htmlopen.

sub htmlrecurse {
# ---------------------------------------------------------------------
# Recursive routine to generate <name>.html and <name>_form.html
# documents for the named class and all of its children.
# ---------------------------------------------------------------------
	local($name)=@_;
	local($child,@children,$parent,@parents);

	@parents=&getparents($name);
	while($parent=pop(@parents)) { # Pop gets highest level parent first.
		next if(-r "${parent}.html" && -r "${parent}_form.html");
		&htmlboth(lc($parent));
	}
	&htmlboth($name);
	@children=&getchildren($name);
	foreach $child (@children) {
		next if(-r "${child}.html" && -r "${child}_form.html");
		&htmlrecurse(lc($child));
	}
} # End htmlrecurse.

sub htmlrmain {
# ---------------------------------------------------------------------
# Called to generate <name>.html and <name>_form.html documents for the
# named class and all of its children.
#
# <parent>.html and <parent>_form.html documents will also be generated
# if they don't exist for any parents of the named class, but
# children.html and chidren_form.html files will be generated only for
# the named class, if they don't already exist.
#
# A class_index.html document showing an alphabetically collated index
# of all classes will be generated.
#
# A method_index.html document showing an alphabetically collated index
# of all methods will be generated.
#
# A <method>_method.html document showing an index to all classes for
# which <method> is native will be generated.
# ---------------------------------------------------------------------
	local($name)=@_;
	local($child,@children,$parent,@parents);

	%class_xref=(); # Initialize to empty.  $class_xref{"<class_name>"}
		# will be set to 1 for all methods encountered.
	%method_xref=(); # Initialize to empty.  $method_xref{"<method_name>"}
		# will be set to 1 for all methods encountered.
	%method_classes=(); # Initialize to empty.
		# $method_classes{"<method_name>"}
		# will be set to a string consisting of the blank-delimited
		# names of all the classes for which <method_name> is native.

	&htmlrecurse($name); # Start recursion to travel down the tree.

	# Now build the class index.
	&htmlopen("class_index.html");
	&htmlcindex("OUT");
	close(OUT);

	# Now build the method index.
	&htmlopen("method_index.html");
	&htmlmindex("OUT");
	close(OUT);

	# Now build all the <method_name>_method.html documents.
	&htmlmethods;

	return(1);
} # End htmlrmain.

sub listhit {
# ---------------------------------------------------------------------
# Called by both searchfile and namehit to take the proper action
# when a filename matching the search criteria is found.
# ---------------------------------------------------------------------
	local($file,$trailer)=@_;

	if ($edit) {
		system("$edit $file") unless($hits{$file});
		$hits{$file}=1; # Indicate file found.
	} elsif($Debug) {
		&scanner_debug($file);
	} else {
		print("$file$trailer\n");
	}
	return(1);
} # End listhit.

sub namecheck {
# ---------------------------------------------------------------------
# Returns $file if the full path in $file matches $name and $suffix.
# Otherwise returns "".
# ---------------------------------------------------------------------
	local($file,$name,$suffix)=@_;
	local(@q,$basename,$ret);

	$ret=0;
        @q=split("/",$file);
        $basename=pop(@q);
	$basename=lc($basename) unless($a_switch);
	$ret = ($basename =~ /^$name$suffix$/) ? $file : "";
	return($ret);
} # End namecheck.

sub namehit {
# ---------------------------------------------------------------------
# Returns 1 or 0 after listing the full path to the specified filename.
# ---------------------------------------------------------------------
	local($file,$name,$suffix)=@_;
	local(@q,$basename,$ret);

	$ret=1 if(&namecheck($file,$name,$suffix));
	&listhit($file) if ($ret);
	return($ret);
} # End namehit.

sub parsea {
# ---------------------------------------------------------------------
# Called from htmlform to parse a line in a C header file.
# Returns a length greater than 0 if this is a line we're interested in,
# i.e. a line declaring a field of a class.
# ---------------------------------------------------------------------
	local($line)=@_;
	local($length,$alignment,$friend,$word);

	($length,$alignment,$friend,$line)=&parseb($line);
	return($length,$alignment) if($friend);
	if($length == 0 && $line =~ /^\*+(\w+.*)/) {
		# It is pointer to something.
		$length=$alignment=4;
		$line=$1;
	}
	return(0,0) unless($length);
	if(!($line =~ /^\(\*\w+\)\s*\(.*/)) {
		# It is not pointer to function.
		$line=~/^(\w+)\s*(.*)/;
		return(0,0) unless($word=$1); # Should've found variable name.
		$line=&stripcom($2); # Strip leading blanks and comments.
		return(0,0) if($line=~/^\(/); # Must be a function declare
			# not part of class structure declaration.
		if ($line =~ /^\s*\[(\d+)\]\s*(.*)/) {
			$length*=$1 ; # Multiply by dimension if array. 
			$line=&stripcom($2);
		}
		return(0,0) unless($line=~/^;.*/);
	}
	return($length,$alignment);
} # End parsea.

sub parseb {
# ---------------------------------------------------------------------
# Called from htmlform and htmlclass_methods to parse a line in a C
# header file, looking for a data type declaration, e.g. the "int *"
# in "int *abc".  Returns ($length,$alignment,$friend,$tail), where -
# ->	length is greater than 0 if this is a declaration of some kind,
#	"unsigned char *xyz;" or "unsigned char *xyz(int a,...);".  The
#	length is the length needed to store the identified data type,
#	e.g. length will be 1 for "unsigned char" and 4 for "unsigned
#	char *".
# ->	alignment is the alignment needed in memory for the identified
#	data type, e.g. 1 for "char", 4 for "char *".
# ->	friend is 1 if the friend keyword is encountered.
# ->	tail is the part after the data type declaration, e.g. "abc"
#	in "int *abc".
# ---------------------------------------------------------------------
	local($line)=@_;
	local($length,$alignment,$friend,$save,$word);

	($length,$alignment,$friend,$save)=(0,0,0,$line); # Default.
	while(1) {
		$line=~/^\s*(\w+)\s*(.*)/;
		$word=$1; # $1 is 1st word.
		$line=$2; # Line is all except 1st word.
		print("word='$word' line='$line'\n") if($Debug);
		next if($word eq "virtual" ||
			$word eq "unsigned" ||
			$word eq "const");
		if(	$word eq "float" ||
			$word eq "int" ||
			$word eq "long" ||
			$word eq "short" ||
			$word eq "void"
			) {
			$length=$alignment=4;
			last;
		}
		if( $word eq "char" ) {
			$length=$alignment=1;
			last;
		}
		if( $word eq "double" ) {
			$length=$alignment=8;
			last;
		}
		if( $word eq "vtkTimeStamp") {
			$length=8;
			$alignment=4;
			last;
		}
		if( $word eq "friend") {
			$friend=1;
			$length=$alignment=4;
			last;
		}
		if( $line =~ /^\*+(.*)/) {
			# It is pointer, e.g. "vtkObject *xyz".
			return(4,4,$friend,$1);
		} 
		return(0,0,0,$save); # Not identifiable.
	}
	if($line =~ /^\*+\s*(.*)/) { # It is pointer
		$line=$1;
		$length=$alignment=4;
	}
	return($length,$alignment,$friend,$line);
} # End parseb.

sub pathsplit {
# ---------------------------------------------------------------------
# Called to obtain the path and Name from "$Name.$suffix" in the filename
# for the specified class name.
# ---------------------------------------------------------------------
	local($name,$suffix)=@_;
	local($line);

	$line = &getpath($name,".h");
	$line =~ /^(.*\/)(\w+)\.h/;
	return($1,$2);
} # End pathsplit.

sub scanner {
# ---------------------------------------------------------------------
# Called to do a lexical scan of the input array @lines, and return
# the next C++ statement.  The scan is not lexically complete, some
# shortcuts having been taking for efficiency, and because we're not
# going to attempt to compile code from the output.
#
# -> cursor is the index within the currently indexed line to the
#	next avaialable character.
# -> ix is the index within @lines to the currently available line.
# -> Some comments will be returned, but those of the form '//...' 
#	on lines by themselves will be eliminated.  Comments of the
#	form //... that're at the end of a line following a semicolon
#	will be transformed to '/*...*/;'.
# -> Other than the above, complete C++ statements ending in a semicolon
#	or right brace are returned.
# -> "" will be returned to indicate EOF.
#
# state 0:  Looking for start of statement.
# state 1:  Found first non-blank first statement.
# state 2:  Looking for trailing */ after finding beginning /* of comment.
# state 3:  Looking for ending quotation mark (").
# state 4:  Expecting either semicolon or new statement.
# ---------------------------------------------------------------------
	local($cursor,$ix,$lines)=@_;
	local($blnk,$ch,$len,$line,$savestate,$state,$stmt,$substmt);

	$blnk=$state=0;
	$stmt="";
	return(-1,-1,"") if($ix>=scalar(@$lines));
	$line=$$lines[$ix]; # Current line.
	$len=length($line);
	print("scanner: cursor=$cursor ix=$ix len=$len scalar(\@\$lines)=".
		scalar(@$lines)." line='$line'\n")
		if($Debug_scanner);
	while(1) {
		($ch,$cursor,$ix,$len,$line)=
			&scanner_getch($cursor,$ix,\@$lines);
		print("scanner loop: state=$state ch='$ch' cursor=$cursor ".
			"ix=$ix len=$len line='$line' stmt='$stmt'\n")
			if($Debug_scanner);
		last if(length($ch)==0); # end of file.
		if($ch eq "}" && $state != 3 && $state != 2) {
			# Brace must be matched at higher level of nesting
			# so put it back in input stream and return.
			($ch,$cursor,$ix,$len,$line)=
				&scanner_putch($cursor,$ix,\@$lines);
			last;
		}
		if($state==4) { # Looking for either semicolon or new stmt.
			next if ($ch eq " ");
			if($ch eq ";") {
				# Add semicolon to current statement before
				# returning it.
				$stmt.=";";
			} else { # Must be 1st nonblank of new statement.
				# Put character back in input stream before
				# returning current statement that isn't
				# terminated with a semicolon.
				($ch,$cursor,$ix,$len,$line)=
					&scanner_putch($cursor,$ix,\@$lines);
			}
			last;
		}
		if($state != 2 && $state != 3) {
			# If not processing quoted string, or processing
			# /*...*/, # eliminate repeated blanks, replace
			# comments with a single blank, and eliminate
			# preprocessor statements.
			if ($ch eq " ") {
				next if($blnk); # Eliminate multiple blanks.
				next if($state==0); # Eliminate leading blanks.
				$blnk=1; # Indicate one blank processed.
				$stmt.=$ch; # Add blank to stmt.
				next;
			}
			if($ch eq "/" && $cursor<$len) {
				if(substr($line,$cursor,1) eq "/") {
					# It is //...
					$cursor=$len; # Skip comment.
					next if($state==0);
						# Eliminate leading blanks.
					$stmt.=" " unless($blnk);
					$blnk=1; # One blank processed.
					next;
				} elsif(substr($line,$cursor,1) eq "*") {
					# It is /*...
					$cursor++;
					$stmt.="/*";
					$blnk=1; # One blank processed.
					$savestate=$state;
					$state=2; # Find */.
					next;
				}
			}
			if($ch eq "#") {
				$cursor=$len; # Skip prep. line.
				next;
			}
			$blnk=0; # ch is nonblank.
			$state=1 unless($state); # Found start of stmt.
		}
		if($state==2) { # Looking for end comment, */.
			$stmt.=$ch; # Next character in comment.
			next if($ch ne "*"); # Ignore all but asterisk.
			next if($cursor>=$len); # Ignore asterisk at end line.
			next unless(substr($line,$cursor,1) eq "/");
			$cursor++;
			$stmt.="/";
			$state=$savestate; # Restore state before /*...*/.
			next;
		}
		$stmt.=$ch; # At this point, $ch is part of statement.
		last if($stmt =~ /^((public)|(private)|(protected)):/);
		if($state==3) { # Processing quoted string.
			next if(ch eq "\\" && $cursor<$len &&
				substr($line,$cursor,1)=='"'); # It is \".
			if($ch eq '"') { # End of quoted string.
				$state=1; # Processing statement.
				next;
			}
		}
		# Must be state==1, processing statement
		if($ch eq ";") {
			if (substr($line,$cursor) =~ /\s*\/\/(.*)/) {
				# Transform trailing '; //comment' to
				# '/*comment*/;' so it can later be
				# associated with proper stmt.
				$stmt=substr($stmt,0,length($stmt)-1).
					" /*".$1."*/ ;";
				$cursor=$len; # Skip rest of line.
			}
			last;
		}
		if($ch eq '"') {
			$state=3; # Look for ending quote.
			next;
		}
		if($ch eq '{') {
			while(1) {
				($cursor,$ix,$substmt)=
					&scanner($cursor,$ix,\@$lines);
				$stmt.=$substmt;
				last if($ix>=scalar(@$lines));
				($ch,$cursor,$ix,$len,$line)=
					&scanner_getch($cursor,$ix,\@$lines);
				last if($ch eq "}");
				($ch,$cursor,$ix,$len,$line)=
					&scanner_putch($cursor,$ix,\@$lines);
					# If it's not a closing brace, put
					# it back and loop to try for next
					# stmt at this nesting level.
			}
			$stmt.=$ch; # Add } to current stmt.
			$state=4; # Expecting either semicolon or new stmt.
			next;
		}
	}
	print("scanner returning cursor=$cursor ix=$ix stmt='$stmt'\n")
		if($Debug);
	return($cursor,$ix,$stmt);
} # End scanner.

sub scanner_getch {
# ---------------------------------------------------------------------
# Called to get the next character from the input stream.
# ---------------------------------------------------------------------
	local($cursor,$ix,$lines)=@_;
	local($ch,$line,$len);

	$line=$$lines[$ix]; # Current line.
	$len=length($line); # Current length.
	print("scanner_getch: cursor=$cursor ix=$ix len=$len line='$line'\n")
		if($Debug_scanner);
	if($cursor>=$len) { # Time to go to a new line.
		while($cursor>=$len) {
			$ix++;
			return("",0,$ix) if($ix>=scalar(@$lines)); # All done.
			$line=$$lines[$ix]; # Current line.
			$len=length($line);
			$cursor=0;
		}
		$ch=" "; # Return a blank for a newline, and leave cursor 0.
	} else {
		$ch=substr($line,$cursor,1); # Next character.
		$ch=" " if($ch eq "\t"); # Replace a tab with a blank.
		$cursor++;
	}
	return($ch,$cursor,$ix,$len,$line);
} # End scanner_getch.

sub scanner_putch {
# ---------------------------------------------------------------------
# Called to put the current character back in the input stream, i.e.
# get the prior character in the input stream.
# ---------------------------------------------------------------------
	local($cursor,$ix,$lines)=@_;
	local($ch,$line,$len,$save);

	$line=$$lines[$ix]; # Current line.
	$len=length($line); # Current length.
	$cursor--; # Back up cursor.
	if ($cursor<0) {
		# The last thing returned was a blank to represent a newline,
		# in which case we should back up $ix to the next prior
		# line with a length greater than 0, set $cursor to
		# length($$lines[$ix]), and set ch to the last character in
		# $$lines[$ix].
		while(1) { # Back up to prior empty line.
			die("ERROR: ix already at 0 in scanner_putch")
				unless($ix > 0);
			$ix--;
			$line=$$lines[$ix]; # Current line.
			$len=length($line); # Current length.
			$cursor=$len;
			last if($len>0);
		}
		$ch=substr($line,$cursor-1,1); # Prior character.
	} elsif ($cursor==0) {
		# The last thing returned was the first character on this line,
		# in which case we should leave cursor, ix and len alone, and
		# set ch to " " to represent the newline from the prior line.
		$ch=" "; 
	} else {
		# The last thing returned was the second or subsequent
		# character on this line.  We should leave cursor, ix and len
		# along, and set ch to the character indexed by cursor-1.
		$ch=substr($line,$cursor-1,1); # Prior character.
	}
	return($ch,$cursor,$ix,$len,$line);
} # End scanner_putch.

sub search {
# ---------------------------------------------------------------------
# Called from mainline to initiate a search.
# ---------------------------------------------------------------------
	local($name,$suffix,$action)=@_;
	local($ret);

	if($dohtml) {
		$ret=&html($name,$action);
	} elsif($action eq "p") {
		$ret=&searchparent($name,$suffix,$action);
	} elsif($action eq "r") {
		$ret=&htmlrmain($name);
	} else {
		$ret=&searchfiles($name,$suffix,$action);
	}
	return($ret);
} # End search.

sub searchfile {
# ---------------------------------------------------------------------
# Called to search the specified file for the specified object.
# action may be either -
#	"c" for class definition, searching for inheritance from
#		$name in a class defined in this file.
#	"f" for field name.
#	"m" for $name being a method of a class defined in this file.
#	"p" for class $name being defined in this file.  If found,
#		the class' parent name will be returned, or a 1 if
#		no parent is defined.  Otherwise 0 is returned.
#	"q" for class $name being pointed to by an element declared
#		in this file.
# ---------------------------------------------------------------------
	local($file,$name,$action)=@_;
	local($class,$line,@lines,$macroform,$parent,$prefix,$rest,
		$ret,$save,$suffix);

	$ret=0;
	@lines=&getlines($file);
	$class="";
	if ($action eq "m" && $name =~ /^([gs]et)(.*)/) {
		$macroform=1;
		$prefix=$1;
		$suffix=$2;
	}
	foreach $line (@lines) {
		next if ($line =~ m#^\s*//#); # Skip comments.
		if ($line =~ /^\s*class\s+VTK_EXPORT\s+(\w+)\s+(.*)/) {
			$class=$1;
			$rest=$2;
			if ($action =~ /[cp]/) { 
				$parent = ($rest =~ /:\s+public\s+(\w+)/)
					? $1 : "";
				if ($action eq "c") { 
					$ret=&listhit($file,"\t$class")
						if ($name eq lc($parent));
					last if($ret); # All done.
				}
				if ($action eq "p") { 
					if ($name eq lc($class)) {
						$ret=($parent) ? $parent : 1;
						&listhit($file,
							"\t$class/$parent");
						last; # All done.
					}
				}
			}
		}
		if ($action eq "m") { # Looking for method name.
			$line=~s/^\s*(.*)/$1/; # Remove whitespace at front.
			$save=$line;
			$line=lc($line) unless($a_switch); # Lowercase.
			$ret=&listhit($file,"\t$class/$save")
				if (&searchmethod($save,$line,$name));
		}
		if ($action eq "f") { # Looking for field name.
			$line=~s/^\s*(.*)/$1/; # Remove whitespace at front.
			$save=$line;
			$line=lc($line) unless($a_switch); # Lowercase.
			$ret=&listhit($file,"\t$class/$save")
				if (	$line =~ /^.*\s+$name\s*;.*/ ||
					$line =~ /^.*\s+$name\[.$\]\s*;.*/ 
				);
		}
		if ($action eq "q") { # Looking for pointer to name.
			$line=~s/^\s*(.*)/$1/; # Remove whitespace at front.
			$save=$line;
			$line=lc($line) unless($a_switch); # Lowercase.
			$ret=&listhit($file,"\t$class/$save")
				if ($line =~ /^$name\s*\*\w+;/);
		}
	}
	return($ret);
} # End searchfile.

sub searchfiles {
# ---------------------------------------------------------------------
# Called to search directory $dir for the specified name.
# ---------------------------------------------------------------------
	local($name,$suffix,$action)=@_;
	local($cmd,$file,@files,$ret);

	$cmd="find $dir/* -type f -name '*$suffix'";
	chop(@files=`$cmd`);
	$ret=0;
	foreach $file (@files) {
		if ($action eq "c") {
			$ret=1 if(&searchfile($file,$name,$action));
		} elsif ($action eq "h" || $action eq "s") {
			$ret=&namehit($file,$name,$suffix);
			last if($ret);
		} elsif ($action eq "m" || $action eq "f" || $action eq "q") {
			$ret+=&searchfile($file,$name,$action);
		} elsif ($action eq "p") {
			last if($ret=&searchfile($file,$name,$action));
		}
	}
	return($ret);
} # End searchfiles.

sub searchmacro {
# ---------------------------------------------------------------------
# Returns the mixed case method name if $line is a macro to define a
# Set/Get method, and "" otherwise.  $save contains the original line
# in mixed case.  $line is equivalent to lc($save), i.e. a copy of $save
# translated to lowercase.  $prefix and $suffix are also lowercase.
# ---------------------------------------------------------------------
	local($save,$line,$prefix,$suffix)=@_;
	local($macro);

	foreach $macro (
		"",
		"clamp",
		"object",
		"referencecountedobject",
		"string",
		"vector",
		"vector2",
		"vector3",
		"vector4",
		"vector6",
		"viewportcoordinate",
		"worldcoordinate"
	) {
		if ($line =~ /^vtk${prefix}${macro}macro\($suffix,.*/) {
			$save =~ /^(vtk.*Macro)\(([SG]et)..*/;
			return("$1$2");
		}
	}
	return("");
} # End searchmacro.

sub searchmethod {
# ---------------------------------------------------------------------
# Returns the method name in mixed case if $line declares a method.
# Otherwise returns "".  $save contains the original line in mixed
# case.  $line is equivalent to lc($save), i.e. a copy of $save
# translated to lowercase.  $name is also lowercase.
# ---------------------------------------------------------------------
	local($save,$line,$name)=@_;
	local($prefix,$ret,$suffix)=@_;

	if ($line =~ /^.*$name\s*\(.*/) {
		$save =~ /^.*\s+(\w+)\(.*/;
		$ret=$1;
	} elsif ($name =~ /^([gs]et)(.*)/) {
		$prefix=$1;
		$suffix=$2;
		$ret=&searchmacro($save,$line,$prefix,$suffix);
	} else {
		$ret=""; # Method not found.
	}
	return($ret);
} # End searchmethod.

sub searchparent {
# ---------------------------------------------------------------------
# Called to initiate a parent search.
# ---------------------------------------------------------------------
	local($name,$suffix,$action)=@_;
	local($ret);

	$ret=0;
	while(1) {
		last unless($name=lc(&searchfiles($name,$suffix,$action)));
		$ret=1; # We found at least one file.
	}
	return($ret);
} # End searchparent.

sub stripcom {
# ---------------------------------------------------------------------
# Strips leading comments of the form /*...*/.
# ---------------------------------------------------------------------
	local($stmt)=@_;
	while($stmt =~ /^\s*\/\*(.*)/) {
		$stmt=substr($1,index($1,"*/")+2);
	}
	print("stripcom returning stmt='$stmt'\n") if($Debug_scanner);
	return($stmt);
} # End stripcom.


# Mainline ---------------------------------------------------------------
&help if (0==scalar(@ARGV));
$dir="/opt/vtk"; # Default.
$prefix="vtk"; # Default.
$suffix=".h"; # Default.
$action="h"; # Default.
while($arg=shift) {
	if (substr($arg,0,1) eq "-") {
		if (length($arg) > 2) {
			unshift(@ARGV,"-".substr($arg,2));
			$arg=substr($arg,0,2);
		}
		if ($arg eq "-a") {
			$a_switch=1;
			$prefix="";
			next;
		}
		if ($arg eq "-c") { $action="c"; next; }
		if ($arg eq "-d") {
			die("ERROR: -d not followed by path\n")
				unless($dir=shift);
			next;
		}
		if ($arg eq "-D") { $Debug=1; next; }
		if ($arg eq "-e") {
			die("ERROR: -e not followed by edit command\n")
				unless($edit=shift);
			next;
		}
		if ($arg eq "-f") { $action="f"; next; }
		if ($arg eq "-h") { $action="h"; next; }
		if ($arg eq "-m") { $action="m"; next; }
		if ($arg eq "-p") { $action="p"; next; }
		if ($arg eq "-q") { $action="q"; next; }
		if ($arg eq "-r") { $action="r"; next; }
		if ($arg eq "-s") {
			$action="s";
			$suffix=".cxx";
			next;
		}
		if ($arg eq "-w") { $dohtml=1; next; }
		if ($arg eq "-x") { $dohtml=1; $doform=1; next; }
	}
	unshift(@ARGV,$arg);
	last;
}
die("ERROR: No name to search for specified.\n") unless($name=shift);
unless($a_switch) {
	$name="$prefix$name" if ($action !~ /[fm]/  && 
		0 != index($name,$prefix));
		# Add vtk prefix unless we're looking for a method (m)
		# or a field (f).
	$name=lc($name); # Make it all lowercase.
}
unless(&search($name,$suffix,$action)) {
	print("Not Found: $name\n");
	exit 1;
}

