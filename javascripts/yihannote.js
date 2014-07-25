var yihannote = {};

yihannote.mode = 'view';

yihannote.changeMode = function() {
    var button = document.getElementById('edit/view button');
    var noteBody = document.getElementById('note body');
    if (yihannote.mode === 'view') {
        yihannote.mode = 'edit';
        button.textContent = 'View';
        noteBody.addEventListener('click', yihannote.onNoteBodyClick, false);
    } else {
        yihannote.mode = 'view';
        button.textContent = 'Edit';
        noteBody.removeEventListener('click', yihannote.onNoteBodyClick);
    }
};

yihannote.onNoteBodyClick = function(event) {
    var targetNode = event.target;
    while (!targetNode.id) {
        targetNode = targetNode.parentNode;
    }
    var ajaxResponseHandler = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            document.getElementById('editFormBackground').className = '';
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

yihannote.onEditFormBackgroundClick = function(event) {
    if (event.target.id === 'editFormBackground') {
        event.target.className = 'hidden';
    }
};
