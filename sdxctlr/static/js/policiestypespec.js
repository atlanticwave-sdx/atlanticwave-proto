/* Based on 
https://www.formget.com/how-to-dynamically-add-and-remove-form-fields-using-javascript/ */

var MaxInputs = 100; // Maximum Input Boxes Allowed
var i = 0;           // Dynamic input count

var m = 0            // Match count
var a = 0            // Action count

/*
---------------------------------------------
Function to Remove Form Elements Dynamically
---------------------------------------------
*/
function removeElement(parentDiv, childDiv, counter){
    if (childDiv == parentDiv){
        alert("The parent div cannot be removed.");
    }
    else if (document.getElementById(childDiv)){
        var child = document.getElementById(childDiv);
        var parent = document.getElementById(parentDiv);
        parent.removeChild(child);
        counter -= 1;
    }
    else{
        alert("Child div has already been removed or does not exist.");
        return false;
    }
}

/*
----------------------------------------------------------------------------

Functions that will be called upon, when user click on the Name text field.

----------------------------------------------------------------------------
*/
function multipointAddFcn(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    i += 1;
    y.setAttribute("Name", "multipointelement_" + i);
    r.innerHTML = "Endpoint,port,VLAN"
    r.appendChild(y);
    r.setAttribute("id", "endpoint_" + i);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("count").value = i
}
function multipointDeleteFcn(){
    var p = document.getElementById("myForm");
    var c = document.getElementById("endpoint_"+i);
    p.removeChild(c);
    i -= 1;
    document.getElementById("count").value = i;
}

function sdxmatchAddFcn(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    m += 1;
    y.setAttribute("Name", "match_" + m);
    r.innerHTML = "MATCH,value"
    r.appendChild(y);
    r.setAttribute("id", "match_" + m);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("match_count").value = m
}
function sdxmatchDeleteFcn(){
    var p = document.getElementById("myForm");
    var c = document.getElementById("match_"+m);
    p.removeChild(c);
    m -= 1;
    document.getElementById("match_count").value = m;
}

function sdxactionAddFcn(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    a += 1;
    y.setAttribute("Name", "action_" + a);
    r.innerHTML = "ACTION,newvalue"
    r.appendChild(y);
    r.setAttribute("id", "action_" + a);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("action_count").value = a
}
function sdxactionDeleteFcn(){
    var p = document.getElementById("myForm");
    var c = document.getElementById("action_"+a);
    p.removeChild(c);
    a -= 1;
    document.getElementById("action_count").value = a;
}
