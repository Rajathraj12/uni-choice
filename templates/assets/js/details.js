fetch ('/user')
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                document.getElementById('loginbutton').style.display = 'none';
                document.getElementById('name').innerText = data.name;
                document.getElementById('name').style.display = 'block';
                document.getElementById('name').style.display = 'block';
                document.getElementById('logoutbtn').style.display = 'block';
                document.getElementById('profilepicture').src = data.profilepic;
                document.getElementById('profilepicture').style.display = 'block';
                document.getElementById('loginfooter').style.display = 'none';
                document.getElementById('useremail').innerText = "Email: "+data.email;
                document.getElementById('userphone').innerText = "Phone: "+data.phone;
                document.getElementById('useregno').innerText = "Registration Number: "+data.regno;
                document.getElementById('fullname').innerText = "Hello, "+data.name;
                document.getElementById('profilepicturebig').src = data.profilepic;

            }
        })

function deleteacc() {
    fetch('delete', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/signup';
        }
    })
}