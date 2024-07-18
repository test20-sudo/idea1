from flask import Flask, render_template_string, request, jsonify
import os
import spacy
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

app = Flask(__name__)

# Initialize the Mistral client and spaCy model
model = "mistral-large-latest"
client = MistralClient(api_key="azyEN3ZYjcvg964D8U99slt0JzY5jG4F")
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"}:
            keywords.add(token.text)
    for ent in doc.ents:
        keywords.add(ent.text)
    return keywords

@app.route('/', methods=['GET'])
def index():
    return render_template_string(html_template)

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form['user_input']
    keywords = extract_keywords(user_input)
    input1 = str(keywords)
    
    messages = [
        ChatMessage(role="user", content=f"Generate 10 research ideas based on the keywords: {input1}. Describe how it can be done with technical details and a rough idea of methodology. Dont highlight the heading")
    ]

    chat_response = client.chat(model=model, messages=messages)
    response_content = chat_response.choices[0].message.content
    
    # Split the response content into lines
    ideas = response_content.split('\n')
    
    return jsonify({'ideas': ideas})

html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Research Idea Generator</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kalnia+Glaze:wght@100..700&family=Playwrite+HR+Lijeva:wght@100..400&display=swap" rel="stylesheet">
    <style>
      body {
        background-color: black;
        color: white;
      }
      #loading {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0,0,0,0.5);
        z-index: 9999;
      }
      .loader {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        height: 50px;
        aspect-ratio: 2;
        border: 10px solid #000;
        box-sizing: border-box;
        background: 
          radial-gradient(farthest-side,#fff 98%,#0000) left/20px 20px,
          radial-gradient(farthest-side,#fff 98%,#0000) left/20px 20px,
          radial-gradient(farthest-side,#fff 98%,#0000) center/20px 20px,
          radial-gradient(farthest-side,#fff 98%,#0000) right/20px 20px,
          #000;
        background-repeat: no-repeat;
        filter: blur(4px) contrast(10);
        animation: l14 1s infinite;
      }
      @keyframes l14 {
        100%  {background-position:right,left,center,right}
      }
      .typewriter {
        overflow: hidden;
        border-right: .15em solid white;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: .15em;
        animation: 
          typing 3.5s steps(40, end),
          blink-caret .75s step-end infinite;
      }
      @keyframes typing {
        from { width: 0 }
        to { width: 100% }
      }
      @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: white; }
      }
      #user_input {
        background-color: black !important;
        color: white !important;
        transition: box-shadow 0.3s ease-in-out;
      }
      #user_input:focus {
        box-shadow: 0 0 5px 2px red,
                    0 0 10px 4px green,
                    0 0 15px 6px blue;
        outline: none;
      }
      .btn-primary {
        background-color: black !important;
        border-color: white !important;
        color: white !important;
        transition: all 0.3s ease-in-out;
      }
      .btn-primary:hover {
        background-color: gray !important;
        border-color: gray !important;
      }
      .btn-primary:active {
        background-color: white !important;
        border-color: white !important;
        color: black !important;
      }
      .kalnia-glaze {
    font-family: "Kalnia Glaze", serif;
    font-optical-sizing: auto;
    font-weight: 600; /* You can adjust this value as needed */
    font-style: normal;
    font-variation-settings: "wdth" 100;
  }
    </style>
  </head>
  <body>
    <div class="container mt-5">
      <h1 class="text-center kalnia-glaze" style="color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5);">
  IdeoSynth<span style="color: white; text-shadow: 0 0 10px rgba(255,255,255,1), 0 0 20px rgba(255,255,255,0.8), 0 0 30px rgba(255,255,255,0.6);">.</span>
</h1>
<br><br>
      <form id="idea-form">
        <div class="form-group">
          <label for="user_input" class="typewriter">Yo, enter what are you thinking. Lets make a research out of it.</label><br>
          <input type="text" class="form-control" id="user_input" name="user_input" required>
        </div>
        <center><button type="submit" class="btn btn-primary">Generate</button></center>
      </form>
      <div id="ideas-container" class="mt-4" style="display: none;">
        <h2>Generated Research Topics:</h2>
        <div id="ideas-list"></div>
      </div>
    </div>
    <div id="loading">
      <div class="loader"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
      $(document).ready(function() {
        $('#idea-form').on('submit', function(e) {
          e.preventDefault();
          $('#loading').show();
          $('#ideas-container').hide();
          $.ajax({
            url: '/generate',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
              $('#loading').hide();
              $('#ideas-container').show();
              $('#ideas-list').empty();
              response.ideas.forEach(function(idea) {
                $('#ideas-list').append('<p>' + idea + '</p>');
              });
            },
            error: function() {
              $('#loading').hide();
              alert('An error occurred. Please try again.');
            }
          });
        });
      });
    </script>
  </body>
</html>

'''

if __name__ == '__main__':
    app.run(debug=True)