// populates form fields on table row click event
function select_host_row(host_id) {
    fetch(`/get/${host_id}`)
      .then(function (response) {
            return response.text();
      }).then(function (text) {
            var host = JSON.parse(text);
            document.getElementById('name').value = host.name;
            document.getElementById('macaddress').value = host.macaddress;
            if (host.port > 0)
                document.getElementById('port').value = parseInt(host.port);
            else
                document.getElementById('port').value = '';
            document.getElementById('ipaddress').value = host.ipaddress;
            document.getElementById('interface').value = host.interface;
            document.getElementById('hiddenid').value = host_id;
      });
}

// handles options checkbox click event
function checkbox_change(optionid) {
    var status = document.getElementById(optionid).checked;
    fetch(`/admin/change/${optionid}/${status}`);
}

// handles admin checkbox click event
function admin_checkbox_change(event, userid) {
    var is_admin = event.currentTarget.checked;
    if (userid == 1) {
        event.preventDefault();
    }
    fetch(`/admin/set/${userid}/${is_admin}`);
}

// self delete confirmation dialog
function confirm_delete(event, currentid, userid) {
    if (currentid > 1 && currentid == userid) {
        var proceed = confirm("Are you sure you want to delete yourself?");
        if (proceed) {
            console.log(`Self-deleting user ${currentid}`);
        } else {
            event.preventDefault();
        }
    }
    console.log(`Deleting user ${userid}`);
}

// removes alert messages after timeout
window.setTimeout(function() {
    $(".alert").fadeTo(500, 0)
}, 4000);
