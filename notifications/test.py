import requests

def send_simple_message():
    try:
        print('yes')
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org/messages",
            auth=("api", "a54c5ed81fe292a752f7cfd3f62c0c79-b02bcf9f-b48c4038"),
            data={"from": "Excited User <mailgun@sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org>",
                  "to": ["dominicjovin7@gmail.com"],
                  "subject": "Hello",
                  "text": "Testing some Mailgun awesomeness!"})
        
        # Check the response status code
        if response.status_code == 200:
            print("Email sent successfully!")
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
            print(response.text)  # Print error message if available

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

send_simple_message()
