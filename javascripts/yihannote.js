var yihannote = {};

yihannote.mode = 'view';

yihannote.changeMode = function(mode) {
    var noteBody = document.getElementById('noteBody');
    if (mode === 'view') {
        noteBody.className = '';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        document.getElementById('editFormBackground').className = 'hidden';
    } else if (mode === 'edit' || mode === 'inEdit') {
        noteBody.className = 'editing';
        if (mode === 'edit') {
            document.getElementById('editFormContainer').className = 'hidden';
            noteBody.addEventListener('click', yihannote.onNoteBodyClick);
        } else {
            document.getElementById('editFormContainer').className = '';
            noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        }
    } else if (mode === 'latex' || mode === 'inLatex') {
        noteBody.className = 'latex';
        if (mode === 'latex') {
            document.getElementById('latexFormContainer').className = 'hidden';
            noteBody.addEventListener('click', yihannote.onNoteBodyClick);
        } else {
            document.getElementById('latexFormContainer').className = '';
            noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        }
    }
    yihannote.mode = mode;
};

yihannote.NodeHierarchyFillContent = function(root, depth, lastChild) {
    // Add node to html
    var active_list = yihannote.editFormActiveNodes;
    var node = active_list[root];
    var div = document.createElement('div');
    console.log(active_list);
    console.log(root + ',' + depth);
    console.log(node);

    // Add tree's branch
    for (var i = 0; i < depth - 1; i++ ) {
        var vertical = document.createElement('img');
        vertical.src = 'images/vertical.png';
        div.appendChild(vertical);
    }
    if (depth > 0) {
        var corner = document.createElement('img');
        if (lastChild)
            corner.src = 'images/corner.png';
        else
            corner.src = 'images/triway.png';
        div.appendChild(corner);
    }

    // Add tree's node
    var nodeContent = document.createElement('button');
    var text = node.content;
    if (text.length > 15)
        text = text.substring(0, 12) + '...';
    if (text.length == 0)
        text = 'untitled';
    nodeContent.appendChild(document.createTextNode(text));
    div.appendChild(nodeContent);

    // Add the div node to container
    var container = document.getElementById('nodeContainer');
    container.appendChild(div);

    // Recursively build subtrees
    var rootKey = active_list[root].key;
    var childList = [];
    for (var i = 0; i < active_list.length; i++ )
    if (active_list[i].parent_key == rootKey) {
        childList.push(i);
    }
    var compare_function = function(a, b) {
        var active_list = yihannote.editFormActiveNodes;
        return active_list[a].child_index - active_list[b].child_index;
    };
    childList.sort(compare_function);
    for (var i = 0; i < childList.length - 1; i++ ) {
        yihannote.NodeHierarchyFillContent(childList[i], depth + 1, false);
    }
    if (childList.length > 0) {
        yihannote.NodeHierarchyFillContent(childList[childList.length - 1],
            depth + 1, true); 
    }
};

yihannote.resetNodeHierarchy = function() {
    var container = document.getElementById('nodeContainer');
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    var active_list = yihannote.editFormActiveNodes;
    for (var i = 0; i < active_list.length; i++ )
    if (active_list[i].key == yihannote.editKey)
        yihannote.NodeHierarchyFillContent(i, 0, false);       
};

yihannote.editFormAddNode = function(node) {
    // Incorrect implementation, we should detect duplicates
    yihannote.editFormActiveNodes.push(node);
};

yihannote.initEditForm = function(response) {
    yihannote.editKey = response.node.key;
    yihannote.editFormActiveNodes = [];
    yihannote.editFormAddNode(response.node);
    for (var i = 0; i < response.children.length; i++) {
        yihannote.editFormAddNode(response.children[i]);
    }
};

yihannote.onNoteBodyClick = function(event) {
    var targetNode = event.target;
    while (!targetNode.id) {
        targetNode = targetNode.parentNode;
    }

    if (yihannote.mode === 'edit') {
        var ajaxResponseHandler = function() {
            if (this.readyState == 4 && this.status == 200) {
                yihannote.changeMode('inEdit');
                var response = JSON.parse(this.responseText);
                yihannote.initEditForm(response);
                yihannote.resetNodeHierarchy();
            }
        };
    
        var req = new XMLHttpRequest();
        req.open('GET', '/NodeInfo?key=' + targetNode.id);
        req.onreadystatechange = ajaxResponseHandler;
        req.send();
    } else if (yihannote.mode === 'latex') {
        var ajaxResponseHandler = function() {
            if (this.readyState == 4 && this.status == 200) {
                yihannote.changeMode('inLatex');
                var response = JSON.parse(this.responseText)
                document.getElementById('latexFormKey').value = response.key;
                document.getElementById('latexFormContent').value = response.content;
            }
        }
        
        var req = new XMLHttpRequest();
        req.open('GET', '/LatexContent?key=' + targetNode.id);
        req.onreadystatechange = ajaxResponseHandler;
        req.send();
    }
};

yihannote.onKeyDown = function(event) {
    if (event.keyCode === 27) {
        if (yihannote.mode === 'inEdit') {
            yihannote.changeMode('edit');
        } else if (yihannote.mode === 'edit') {
            yihannote.changeMode('view');
        } else if (yihannote.mode === 'inLatex') {
            yihannote.changeMode('latex');
        } else if (yihannote.mode === 'latex') {
            yihannote.changeMode('view');
        }
    }
};

yihannote.onLatexFormContainerClick = function(event) {
    if (event.target.className === 'FormBackground') {
        yihannote.changeMode('latex');
    }
};

yihannote.onEditFormContainerClick = function(event) {
    if (event.target.className === 'FormBackground') {
        yihannote.changeMode('edit');
    }
};

yihannote.addChild = function(event) {
    event.preventDefault();
    document.getElementById('editFormParentKey').value = yihannote.editKey;
    suffix = '';
    if (document.getElementById('editFormType_title').checked) suffix = '.';
    if (document.getElementById('editFormType_paragraph').checked) suffix = ' p';
    if (document.getElementById('editFormType_equation').checked) suffix = ' eq';
    if (document.getElementById('editFormType_ordered_list').checked) suffix = ' ol';
    if (document.getElementById('editFormType_list').checked) suffix = ' ul';
    if (document.getElementById('editFormType_list_item').checked) suffix = ' li';
    suffix += document.getElementById('editFormChildIndex').value;
    document.getElementById('editFormKey').value = yihannote.editKey + suffix;
};
