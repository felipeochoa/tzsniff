"use strict";
function tzsniff(tree) {
    if (typeof tree === 'string') return tree;
    var off = -(new Date(tree.testPoint)).getTimezoneOffset();
    var child = tree.children[off];
    return child ? tzsniff(child) : null;
}
