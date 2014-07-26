var yihannote = {};

yihannote.mode = 'view';

yihannote.changeMode = function(mode) {
    var noteBody = document.getElementById('note body');
    if (mode === 'view') {
        document.getElementById('note body').className = '';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        document.getElementById('editFormBackground').className = 'hidden';
    } else if (mode === 'edit' || mode === 'inEdit') {
        document.getElementById('note body').className = 'editing';
        if (mode === 'edit') {
            document.getElementById('editFormContainer').className = 'hidden';
            noteBody.addEventListener('click', yihannote.onNoteBodyClick);
        } else {
            document.getElementById('editFormContainer').className = '';
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
    var ajaxResponseHandler = function() {
        if (this.readyState == 4 && this.status == 200) {
            yihannote.changeMode('inEdit');
            var response = JSON.parse(this.responseText);
            document.getElementById('editFormKey').value = response.key;
            document.getElementById('editFormParentKey').value = response.parent_key;
            document.getElementById('editFormContent').value = response.content; 
            document.getElementById('editFormChildIndex').value = response.child_index;
            if (response.type === 'title') {
                document.getElementById('editFormTypeTitle').checked = true;
            } else if (response.type === 'equation') {
                document.getElementById('editFormTypeEquation').checked = true;
            } else if (response.type === 'paragraph') {
                document.getElementById('editFormTypeParagraph').checked = true;
            }
        }
    };
    
    var req = new XMLHttpRequest();
    req.open('GET', '/NodeInfo?key=' + targetNode.id);
    req.onreadystatechange = ajaxResponseHandler;
    req.send();
};

yihannote.onKeyDown = function(event) {
    if (event.keyCode === 27) {
        if (yihannote.mode === 'inEdit') {
            yihannote.changeMode('edit');
        } else if (yihannote.mode === 'edit') {
            yihannote.changeMode('view');
        } else if (yihannote.mode === 'latex') {
            yihannote.changeMode('view');
        }
    }
};

yihannote.onEditFormBackgroundClick = function(event) {
    if (event.target.id === 'editFormBackground') {
        yihannote.changeMode('edit');
    }
};
