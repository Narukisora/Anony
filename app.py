
from flask import Flask, request, redirect, session, render_template, url_for
from supabase import create_client, Client
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Supab
url = 'https://tuioudrarooeeerpaagd.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1aW91ZHJhcm9vZWVlcnBhYWdkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3NzA5ODksImV4cCI6MjA2NjM0Njk4OX0.0sMmH6sh0rVdxpZaN6MoxpADh0nyhpHruVADGlIrk9w'
supabase: Client = create_client(url, key)
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = supabase.table('users').select('*').eq('username', username).eq('password', password).execute().data
        
        if user:
            session['user'] = username
            return redirect('/')
        else:
            return 'Invalid Credentials'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/generate_site')
def generate_site():
    if 'user' not in session:
        return redirect('/login')

    unique_id = str(uuid.uuid4())
    supabase.table('anonymous_sites').insert({"id": unique_id, "owner": session['user']}).execute()

    return redirect(f'/anonymous/{unique_id}')

@app.route('/anonymous/<site_id>', methods=['GET', 'POST'])
def anonymous_page(site_id):
    if request.method == 'POST':
        if 'user' not in session:
            return redirect('/login')  # Must be logged in to send

        message = request.form['message']

        supabase.table('messages').insert({
            "site_id": site_id,
            "sender": session['user'],  # Sender is the logged-in username
            "message": message
        }).execute()
        return 'Message Sent!'

    return render_template('anonymous.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    # Get all sites owned by the user
    sites = supabase.table('anonymous_sites').select('*').eq('owner', session['user']).execute().data
    site_ids = [site['id'] for site in sites]

    messages = []
    if site_ids:
        messages = supabase.table('messages').select('*').in_('site_id', site_ids).order('id', desc=False).execute().data

    return render_template('dashboard.html', username=session['user'], sites=sites, messages=messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

