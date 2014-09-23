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
                yihannote.editKey = response.key;
                document.getElementById('editFormKey').value = response.key;
                document.getElementById('editFormParentKey').value = response.parent_key;
                document.getElementById('editFormContent').value = response.content; 
                document.getElementById('editFormChildIndex').value = response.child_index;
                document.getElementById('editFormType_' + response.type).checked = true;
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
