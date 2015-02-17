var yihannote = {};

yihannote.mode = 'view';

yihannote.changeMode = function(mode) {
    var noteBody = document.getElementById('noteBody');
    if (mode === 'view') {
        noteBody.className = '';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        document.getElementById('editFormContainer').className = 'hidden';
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

yihannote.onMoveUpClick = function() {
    var node = yihannote.selectedNode;
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;
    for (var i = 0; i < active_list.length; i++ )
    if (parent_list[i] === parent_list[node] &&
        active_list[i].child_index === active_list[node].child_index - 1) {
        active_list[i].child_index ++;
        active_list[node].child_index --;
        break;
    }
    yihannote.resetNodeHierarchy();
};

yihannote.onMoveDownClick = function() {
    var node = yihannote.selectedNode;
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;
    for (var i = 0; i < active_list.length; i++ )
    if (parent_list[i] === parent_list[node] &&
        active_list[i].child_index === active_list[node].child_index + 1) {
        active_list[i].child_index --;
        active_list[node].child_index ++;
        break;
    }
    yihannote.resetNodeHierarchy();
};

yihannote.onAddChildClick = function() {
    var node = yihannote.selectedNode;
    yihannote.expandNode(yihannote.editFormActiveNodes[node]);
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;
    var child_index = 1;
    for (var i = 0; i < active_list.length; i++ )
    if (parent_list[i] === node)
        child_index ++;
    var new_child = yihannote.editFormNewChild(active_list[node], child_index);
    yihannote.editFormAddNode(new_child);
    yihannote.resetNodeHierarchy();
};

yihannote.editFormNewChild = function(node, child_index) {
    var new_child = {};
    new_child.key = 'new_key';
    new_child.parent_key = node.old_key;
    new_child.content = '';
    new_child.child_index = child_index;
    if (node.type === 'title') {
        new_child.type = 'title';
    } else if (node.type === 'list' || node.type == 'ordered_list') {
        new_child.type = 'list_item';
    } else 
        new_child.type = 'paragraph';
    return new_child;
};

yihannote.editFormUpdateNode = function(index) {
    if (index === -1) return;
    var node = yihannote.editFormActiveNodes[index];
    node.content = document.getElementById('editFormContent').value;
    var types = ['title', 'equation', 'paragraph', 'list', 'ordered_list', 'list_item'];
    for (var i = 0; i < types.length; i++ )
    if (document.getElementById('editFormType_' + types[i]).checked)
        node.type = types[i];
    yihannote.resetNodeHierarchy();
};

yihannote.selectNode = function(index) {
    yihannote.editFormUpdateNode(yihannote.selectedNode);
    yihannote.selectedNode = index;
    var node = yihannote.editFormActiveNodes[index];
    var types = ['title', 'equation', 'paragraph', 'list', 'ordered_list', 'list_item'];
    var disabled = false;
    if (node.type === 'title' && node.old_key !== 'new_key')
        disabled = true;
    for (var i = 0; i < types.length; i++ ) {
        document.getElementById('editFormType_' + types[i]).checked = false;
        document.getElementById('editFormType_' + types[i]).disabled = disabled;
    }
    document.getElementById('editFormType_' + node.type).checked = true;
    document.getElementById('editFormContent').value = node.content;
};

yihannote.expandNode = function(node) {
    if (node.old_key === 'new_key') return;

    var ajaxResponseHandler = function() {
        if (this.readyState === 4 && this.status === 200) {
            var response = JSON.parse(this.responseText);
            for (var i = 0; i < response.children.length; i++) {
                yihannote.editFormAddNode(response.children[i]);
            }
            yihannote.resetNodeHierarchy();
        }
    };
    
    var req = new XMLHttpRequest();
    req.open('GET', '/NodeInfo?key=' + node.old_key);
    req.onreadystatechange = ajaxResponseHandler;
    req.send();    
};

yihannote.submitEditForm = function() {
    yihannote.editFormUpdateNode(yihannote.selectedNode);

    var ajaxResponseHandler = function() {
        if (this.readyState === 4 && this.status === 200) {
            window.location.href = '/#' + yihannote.editKey;
            window.location.reload();
        }
    };

    var req = new XMLHttpRequest();
    req.open('POST', '/EditEntry');
    req.setRequestHeader('Content-type', 'application/json');
    req.onreadystatechange = ajaxResponseHandler;
    req.send(JSON.stringify(yihannote.editFormActiveNodes));
};

yihannote.editFormMoveNode = function(src, target) {
    if (src === target) return;
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;
    yihannote.expandNode(active_list[target]);

    var child_index = 1;
    for (var i = 0; i < active_list.length; i++ )
    if (parent_list[i] === target)
        child_index ++;

    var node = active_list[src];
    yihannote.parentNode[src] = target;
    node.child_index = child_index;
    yihannote.resetNodeHierarchy();
};

yihannote.editFormUpdateKey = function(nodes) {
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;
    // For consistency we do not change the root key
    for (var i = 0; i < nodes.length; i++ ) 
    if (active_list[nodes[i]].key !== yihannote.editKey) {
        var node = active_list[nodes[i]];
        var suffix;
        if (node.type === 'title') suffix = '.';
        if (node.type === 'paragraph') suffix = ' p';
        if (node.type === 'equation') suffix = ' eq';
        if (node.type === 'ordered_list') suffix = ' ol';
        if (node.type === 'list') suffix = ' ul';
        if (node.type === 'list_item') suffix = ' li';
        if (node.type !== 'title') {
            suffix += node.child_index;
        } else {
            var index = 1;
            for (var j = 0; j < nodes.length; j++ )
            if (active_list[nodes[j]].type === 'title' &&
                active_list[nodes[j]].child_index < node.child_index)
                index ++;
            suffix += index;
        }
        node.parent_key = active_list[parent_list[nodes[i]]].key
        var new_key = node.parent_key + suffix;
        node.key = new_key;
    }
};

yihannote.fillNodeHierarchy = function(root, depth, lastChild) {
    var active_list = yihannote.editFormActiveNodes;
    var parent_list = yihannote.parentNode;

    // Add node to html
    var node = active_list[root];
    var div = document.createElement('div');
    div.className = 'nodeHierarchyDiv';

    // Add tree's branch
    for (var i = 0; i < depth - 1; i++ ) {
        var img = document.createElement('img');
        if (lastChild[i])
            img.src = 'images/blank.png';
        else
            img.src = 'images/vertical.png';
        div.appendChild(img);
    }
    if (depth > 0) {
        var img = document.createElement('img');
        if (lastChild[depth - 1])
            img.src = 'images/corner.png';
        else
            img.src = 'images/triway.png';
        div.appendChild(img);
    }

    // Add tree's node
    var nodeContent = document.createElement('button');
    var text = node.content;
    if (text.length > 15)
        text = text.substring(0, 12) + '...';
    if (text.length === 0)
        text = 'untitled';
    nodeContent.appendChild(document.createTextNode(text));
    var click_event = function() {
        yihannote.selectNode(root);
    };
    nodeContent.addEventListener('click', click_event);
    var dblclick_event = function() {
        yihannote.expandNode(node);
    };
    nodeContent.addEventListener('dblclick', dblclick_event);
    nodeContent.draggable = 'true';
    var dragstart_event = function() {
        yihannote.dragging = root;
    };
    nodeContent.addEventListener('dragstart', dragstart_event);
    var dragover_event = function(event) {
        event.preventDefault();
    };
    nodeContent.addEventListener('dragover', dragover_event);
    var drop_event = function(event) {
        event.preventDefault();
        yihannote.editFormMoveNode(yihannote.dragging, root);
    };
    nodeContent.addEventListener('drop', drop_event); 
    div.appendChild(nodeContent);

    // Add the div node to container
    var container = document.getElementById('nodeContainer');
    container.appendChild(div);

    // Recursively build subtrees
    var childList = [];
    for (var i = 0; i < active_list.length; i++ )
    if (parent_list[i] === root) {
        childList.push(i);
    }

    // Sort the children by their child_index, and then update their child_index
    var compare_function = function(a, b) {
        var active_list = yihannote.editFormActiveNodes;
        return active_list[a].child_index - active_list[b].child_index;
    };
    childList.sort(compare_function);
    for (var i = 0; i < childList.length; i++ )
        active_list[childList[i]].child_index = i + 1;
    yihannote.editFormUpdateKey(childList);

    lastChild[depth] = false;
    for (var i = 0; i < childList.length - 1; i++ ) {
        yihannote.fillNodeHierarchy(childList[i], depth + 1, lastChild);
    }
    if (childList.length > 0) {
        lastChild[depth] = true;
        yihannote.fillNodeHierarchy(childList[childList.length - 1],
            depth + 1, lastChild); 
    }
};

yihannote.resetNodeHierarchy = function() {
    var container = document.getElementById('nodeContainer');
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    var active_list = yihannote.editFormActiveNodes;
    for (var i = 0; i < active_list.length; i++ )
    if (yihannote.parentNode[i] === -1)
        yihannote.fillNodeHierarchy(i, 0, []);
};

yihannote.editFormAddNode = function(node) {
    var exist = false;
    var active_list = yihannote.editFormActiveNodes;
    for (var i = 0; i < active_list.length; i++ )
        if (active_list[i].old_key === node.key)
            exist = true;
    if (!exist || node.key === 'new_key') {
        node.old_key = node.key;
        node.deleted = false;
        yihannote.editFormActiveNodes.push(node);
        for (var i = 0; i < active_list.length; i++)
            if (node.parent_key === active_list[i].old_key)
                yihannote.parentNode.push(i);
        if (node.key === yihannote.editKey)
            yihannote.parentNode.push(-1);
    }
};

yihannote.initEditForm = function(response) {
    yihannote.editKey = response.node.key;
    yihannote.selectedNode = -1;
    yihannote.editFormActiveNodes = [];
    yihannote.parentNode = [];
    yihannote.editFormAddNode(response.node);
    for (var i = 0; i < response.children.length; i++) {
        yihannote.editFormAddNode(response.children[i]);
    }
    yihannote.selectNode(0);
};

yihannote.onNoteBodyClick = function(event) {
    var targetNode = event.target;
    while (!targetNode.id || targetNode.className !== 'section sec-title') {
        targetNode = targetNode.parentNode;
    }

    if (yihannote.mode === 'edit') {
        var ajaxResponseHandler = function() {
            if (this.readyState === 4 && this.status === 200) {
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
            if (this.readyState === 4 && this.status === 200) {
                yihannote.changeMode('inLatex');
                var response = JSON.parse(this.responseText)
                document.getElementById('latexFormKey').value = response.key;
                document.getElementById('latexFormContent').value = response.content;
            }
        };
        
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
