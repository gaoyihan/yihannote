var yihannote = {};

yihannote.mode = 'view';

yihannote.changeMode = function(mode) {
    var button = document.getElementById('edit/view button');
    var noteBody = document.getElementById('note body');
    if (mode === 'edit') {
        yihannote.mode = 'edit';
        button.textContent = 'View';
        noteBody.addEventListener('click', yihannote.onNoteBodyClick, false);
        document.getElementById('editFormBackground').className = 'hidden';
    } else if (mode === 'view') {
        yihannote.mode = 'view';
        button.textContent = 'Edit';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        document.getElementById('editFormBackground').className = 'hidden';
    } else if (mode === 'inEdit') {
        yihannote.mode = 'inEdit';
        button.textContent = 'View';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
        document.getElementById('editFormBackground').className = '';
    }
};

yihannote.onEditViewButtonClick = function() {
    if (yihannote.mode === 'view') {
        yihannote.changeMode('edit');
    } else if (yihannote.mode === 'edit') {
        yihannote.changeMode('view');
    }
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
            document.getElementById('editFormTitle').value = response.title;
            document.getElementById('editFormContent').value = response.content; 
            document.getElementById('editFormChildIndex').value = response.child_index;
            if (response.is_equation) {
                document.getElementById('editFormIsEquationTrue').checked = true;
            } else {
                document.getElementById('editFormIsEquationFalse').checked = true;
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
        }
    }
};

yihannote.onEditFormBackgroundClick = function(event) {
    if (event.target.id === 'editFormBackground') {
        yihannote.changeMode('edit');
    }
};
