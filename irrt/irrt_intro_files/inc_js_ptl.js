function E_Me(c1,c2,c3,c4,c5,c6,c7,c8) 	{
	strAdds = new Array(c1,c2,c3,c4,c5,c6,c7,c8);
	strUser = "";
	strMailTo = "";
	for (x=0;x<strAdds.length;x++) {
		if (strAdds[x]!=null)
			strUser += strAdds[x];
	}
	//alert("mai"+"lto:"+strUser+"@"+"indiana"+"."+ "edu");
	strMailTo = "mai"+"lto:"+strUser+"@"+"indiana"+"."+ "edu";
	document.location = strMailTo;
}

function winopen(url)
{
window.open(url,"","resizable=yes,scrollbars=no,height=625,width=825,left=0,top=0");
}

function SetActiveNavLinkColor() {
        var nav_primary;
        var nav_secondary; 
    
        // This produces an array like
        // ["http:", "", "pervasive.iu.edu", ""] or
        //  ["http:", "", "pervasive.iu.edu", "index.shtml?prim=ptl_org&sec=overview"]
        var url_parts = location.href.split('/');
        var page = url_parts[url_parts.length - 1].split('?')[0]
        if (page == '' || page.split('.')[0] == 'index') {
            if (document.getElementById('overview') != null) {
                nav_primary = 'ptl_org';
                nav_secondary = 'overview';
            }
            else if (document.getElementById('lab_overview') != null) {
                nav_primary = 'lab_overview';
            }
        }
        else {
            re = /(c_ptl_org|c_ptl_ec_dev)_(\w+)\.shtml/
            matches = re.exec(page)
            if (matches != null && matches.length == 3) {
                if (matches[1] == 'c_ptl_org') {
                    nav_primary = 'ptl_org';
                    nav_secondary = matches[2];
                }
                else if (matches[1] == 'c_ptl_ec_dev') {
                    nav_primary = 'ptl_ecdev';
                    if (matches[2] == 'index') {
                        nav_secondary = 'philosophy'
                    }
                    else {
                        nav_secondary = matches[2];
                    }
                }
            }
            else {
                lab_re = /(publications|research|links|people|noteworthy)\.\w+/
                matches = lab_re.exec(page)
                if (matches != null && matches.length == 2) {
                    nav_primary = 'lab_' + matches[1];
                }
            }
       }

    document.getElementById(nav_primary).style.color="990000";
    if (nav_secondary != null) {
        document.getElementById(nav_secondary).style.color="990000";
        var tab_secondary = "td_" + nav_secondary;
        document.getElementById(tab_secondary).style.backgroundColor="F0F0F0";
    }
} // function SetActiveNaveLinkColor

window.onload=function() {

	SetActiveNavLinkColor();
}
