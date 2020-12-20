function removeMessages(params){
    var parentId = params.parentId;
    var childName = params.childName;

    var childNodesToRemove = document.getElementById(parentId).getElementsByClassName(childName);
    for(var i=childNodesToRemove.length-1;i >= 0;i--){
        var childNode = childNodesToRemove[i];
        childNode.parentNode.removeChild(childNode);
    }
}


document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect("http" + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {
        document.querySelector('#message_form').onsubmit = () => {
            const selection = document.querySelector('#message_text').value;
            socket.emit('submit message', {'message': selection});
            return false;
        };
        document.querySelectorAll('.server_link').forEach(message => {
            message.onclick = () => {
                removeMessages({parentId:'messages_container',childName:'message_box'});
                let ch_name = message.dataset.chname;
                socket.emit('get channel messages', {'ch_name': ch_name});
            };
        });
    });


    socket.on('load messages', data => {
        var container = document.createElement('div');
        container.classList.add('message_box');
        var message_author = document.createElement('span');
        message_author.classList.add('message_author');
        var message_text = document.createElement('span');
        message_text.classList.add('message');
        var authorName = document.createTextNode(data.author);
        var messageText = document.createTextNode(data.message);
        
        message_author.appendChild(authorName);
        message_text.appendChild(messageText);
        container.appendChild(message_author);
        container.appendChild(message_text);

        document.querySelector('#messages_container').appendChild(container);
    });


    socket.on('announce message', data => {
        var container = document.createElement('div');
        container.classList.add('message_box');
        var message_author = document.createElement('span');
        message_author.classList.add('message_author');
        var message_text = document.createElement('span');
        message_text.classList.add('message');
        var authorName = document.createTextNode('Felix: ');
        var messageText = document.createTextNode(data.selection);
        
        message_author.appendChild(authorName);
        message_text.appendChild(messageText);
        container.appendChild(message_author);
        container.appendChild(message_text);

        document.querySelector('#messages_container').appendChild(container);
    });

});
