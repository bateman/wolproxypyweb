// populates form fields on table row click event
function select_row(host_id) {
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

// highlights the active item in the navbar
$(document).ready(function () {
    var url = window.location;
    $('ul.nav a[href="'+ url +'"]').parent().addClass('active');
    $('ul.nav a').filter(function() {
         return this.href == url;
    }).parent().addClass('active');
});
