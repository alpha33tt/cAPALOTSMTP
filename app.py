<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Sender</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f4f7fc;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            width: 80%;
            max-width: 800px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            font-size: 32px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            font-size: 14px;
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
            display: block;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }
        .btn:hover {
            background-color: #45a049;
        }
        #progress {
            margin-top: 20px;
            font-size: 16px;
            color: #444;
        }
        #progress p {
            margin: 5px 0;
        }
        .sending {
            color: orange;
        }
        .sent {
            color: green;
        }
        .error {
            color: red;
        }
        #loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        #loading img {
            width: 40px;
        }
    </style>
    <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js" referrerpolicy="origin"></script>
</head>
<body>
    <div class="container">
        <h1>Send Emails</h1>
        <form id="email-form">
            <div class="form-group">
                <label for="from-name">Your Name</label>
                <input type="text" id="from-name" name="from-name" required placeholder="Your Name">
            </div>
            <div class="form-group">
                <label for="bcc">Recipient Emails (BCC)</label>
                <input type="text" id="bcc" name="bcc" required placeholder="Enter emails separated by commas">
            </div>
            <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" id="subject" name="subject" required placeholder="Enter email subject">
            </div>
            <div class="form-group">
                <label for="email-body">Email Body</label>
                <textarea id="email-body" name="email-body" required placeholder="Enter your email content"></textarea>
            </div>
            <div class="form-group">
                <button type="submit" class="btn">Send Emails</button>
            </div>
        </form>

        <div id="loading">
            <img src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/images/loader-large.gif" alt="Loading">
            <p>Sending emails, please wait...</p>
        </div>

        <div id="progress"></div>
    </div>

    <script>
        // Initialize TinyMCE editor
        tinymce.init({
            selector: '#email-body',  // Attach TinyMCE to the email body textarea
            plugins: 'link',
            toolbar: 'undo redo | bold italic | link | image | bullist numlist',
            menubar: false,
            statusbar: false
        });

        // Handle form submission
        document.getElementById('email-form').addEventListener('submit', function (e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const progressElement = document.getElementById('progress');
            const loadingElement = document.getElementById('loading');
            
            // Show loading spinner
            loadingElement.style.display = 'block';
            progressElement.innerHTML = '';  // Reset progress

            // Send the email via the backend
            fetch('/send_email', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(response => response.json())
            .then(data => {
                loadingElement.style.display = 'none';  // Hide loading spinner
                if (data.status === 'success') {
                    data.updates.forEach(update => {
                        const p = document.createElement('p');
                        if (update.status === 'sending') {
                            p.className = 'sending';
                            p.textContent = 'Sending email to ' + update.email + '...';
                        } else if (update.status === 'sent') {
                            p.className = 'sent';
                            p.textContent = 'Email to ' + update.email + ' sent successfully!';
                        }
                        progressElement.appendChild(p);
                    });
                } else {
                    const p = document.createElement('p');
                    p.className = 'error';
                    p.textContent = 'An error occurred: ' + data.message;
                    progressElement.appendChild(p);
                }
            })
            .catch(error => {
                loadingElement.style.display = 'none';  // Hide loading spinner
                const p = document.createElement('p');
                p.className = 'error';
                p.textContent = 'Failed to send emails: ' + error.message;
                progressElement.appendChild(p);
            });
        });
    </script>
</body>
</html>
