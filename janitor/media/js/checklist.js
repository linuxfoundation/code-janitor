// some generic functions for selecting/deselecting/deleting a number of table entries

function toggleall(f,icheck,allcheck) {
    chk = document.forms[f.name].elements[icheck];
    if (document.forms[f.name].elements[allcheck].checked == true) {
        // if only one test, no array
        if (typeof chk.length == 'undefined') {
            chk.checked = true;
        } else {
            for (i = 0; i < chk.length; i++) {
                chk[i].checked = true;
            }
        }
    } else {
        if (typeof chk.length == 'undefined') {
            chk.checked = false;
        } else {
            for (i = 0; i < chk.length; i++) {
                chk[i].checked = false;
            }
        }
    }
}

function buildlist(f,icheck,ilist) {
    chk = document.forms[f.name].elements[icheck];
    llist = '';
    if (typeof chk.length == 'undefined') {
        if (chk.checked == true) {
            llist = chk.value;
        }
    } else {
        for (i = 0; i < chk.length; i++) {
            if (chk[i].checked == true) {
               llist = llist + chk[i].value + ",";
            }
        }
    }
    document.forms[f.name].elements[ilist].value = llist;
}

function buildpairedlist(f,icheck,ilist) {
    chk = document.forms[f.name].elements[icheck];
    llist = '';
    if (typeof chk.length == 'undefined') {
            if (chk.checked == true) {
               llist = chk.value + ":1";
            } else {
               llist = chk.value + ":0";
            }
    } else {
        for (i = 0; i < chk.length; i++) {
            if (chk[i].checked == true) {
               llist = llist + chk[i].value + ":1,";
            } else {
               llist = llist + chk[i].value + ":0,";
            }
        }
    }
    document.forms[f.name].elements[ilist].value = llist;
}

function buildradiolist(f,icheck,ilist) {
    chk = document.forms[f.name].getElementsByClassName(icheck);
    llist = '';
    if (typeof chk.length == 'undefined') {
        if (chk.checked == true) {
            llist = chk.value;
        }
    } else {
        for (i = 0; i < chk.length; i++) {
            if (chk[i].checked == true) {
               llist = llist + chk[i].value + ",";
            }
        }
    }
    document.forms[f.name].elements[ilist].value = llist;
}

