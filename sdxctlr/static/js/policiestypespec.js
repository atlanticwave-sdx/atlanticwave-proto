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
function multipointFunction(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    var g = document.createElement("IMG");
    g.setAttribute("src", "delete.png");
    i += 1;
    y.setAttribute("Name", "multipointelement_" + i);
    r.innerHTML = "Endpoint,port,VLAN"
    r.appendChild(y);
    g.setAttribute("onclick", "removeElement('myForm','endpoint_" + i + "')");
    r.appendChild(g);
    r.setAttribute("id", "endpoint_" + i);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("count").value = i
}

function sdxmatchFunction(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    var g = document.createElement("IMG");
    g.setAttribute("src", "delete.png");
    m += 1;
    y.setAttribute("Name", "match_" + m);
    r.innerHTML = "MATCH:value"
    r.appendChild(y);
    g.setAttribute("onclick", "removeElement('myForm','match_" + m + "')");
    r.appendChild(g);
    r.setAttribute("id", "match_" + m);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("match_count").value = m
}

function sdxactionFunction(){
    var r = document.createElement('span');
    var y = document.createElement("input");
    y.setAttribute("type", "text");
    y.setAttribute("placeholder", "Name");
    var g = document.createElement("IMG");
    g.setAttribute("src", "delete.png");
    m += 1;
    y.setAttribute("Name", "action_" + a);
    r.innerHTML = "ACTION:newvalue"
    r.appendChild(y);
    g.setAttribute("onclick", "removeElement('myForm','action_" + a + "')");
    r.appendChild(g);
    r.setAttribute("id", "action_" + a);
    document.getElementById("myForm").appendChild(r);
    document.getElementById("action_count").value = a
}
