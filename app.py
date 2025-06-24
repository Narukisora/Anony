
from flask import Flask, request, redirect, session, render_template, url_for
from supabase import create_client, Client
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Supab
url = 'https://your-supabase-url.supabase.co'
key = 'your-supabase-service-role-key'
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
        message = request.form['message']

        if 'user' not in session:
            return redirect('/login')

        supabase.table('messages').insert({"site_id": site_id, "sender": session['user'], "message": message}).execute()
        return 'Message Sent!'

    return render_template('anonymous.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    sites = supabase.table('anonymous_sites').select('*').eq('owner', session['user']).execute().data
    messages = supabase.table('messages').select('*').order('id', desc=False).execute().data

    return render_template('dashboard.html', username=session['user'], sites=sites, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
