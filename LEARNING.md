# LEARNING.md - Your Plain-English Guide to This Project

This file is **your personal walkthrough**. Every technology, every file, and
every piece of jargon we use gets explained here in simple terms. If you ever
forget what something does or why it exists, this is the place to look.

It grows one section at a time, one per "phase" of the build. You can read it
top-to-bottom like a story of how the app came together.

> **How to use this file:** Read the phase you just finished. Don't try to
> memorize it. The goal is that when someone asks "how does your app work?",
> you can answer in your own words. The **Glossary** at the bottom is a quick
> lookup for any scary word.

---

## The Big Picture: What Are We Even Building?

Imagine **Dropbox or Google Drive** - a website where you upload files and they
live safely in the cloud. Now add two clever twists:

1. **It automatically shrinks your files** (especially images) so they take up
   less space, without you doing anything.
2. **It never stores the same file twice.** If you (or anyone) uploads a file
   that's already there, it just points to the existing copy instead of wasting
   space on a duplicate.

That's the whole app. Simple idea, genuinely useful, and it teaches you a huge
range of real skills.

### The two halves of the app

Almost every modern web app has two separate parts that talk to each other:

- **Backend** - the "engine room." It runs on a server, holds the database,
  does the actual work (saving files, shrinking images, checking for
  duplicates). The user never sees it directly. **We're writing ours in
  Python.**
- **Frontend** - the "dashboard" you see and click in your web browser: the
  upload button, the file list, the charts. **We'll write ours in
  React/TypeScript** (starting in Phase 4).

They talk over the internet using an **API** (see glossary). Think of the API as
a **waiter in a restaurant**: the frontend (you, the customer) asks the waiter
for something, the waiter carries the request to the kitchen (backend), and
brings back the result. You never walk into the kitchen yourself.

---

## The Toolbox: What Each Technology Is (and Why We Picked It)

| Tool | What it is, in plain words | Why we use it |
|------|---------------------------|---------------|
| **Python** | A programming language that reads almost like English. Great for beginners. | Runs our whole backend. |
| **FastAPI** | A Python "framework" (a pre-built skeleton) for making an API - i.e. the waiter that takes requests and sends answers. | Modern, fast, and it *auto-generates a test page* for us (huge for beginners). |
| **Uvicorn** | The actual program that *runs* our FastAPI app and keeps it listening for requests. | FastAPI is the recipe; Uvicorn is the stove that cooks it. |
| **SQLite** | A database that is just **one single file** on your computer (`vault.db`). No separate server to install or manage. | Perfect for learning and small projects. Zero setup pain. |
| **SQLAlchemy** | A translator between Python and the database. Lets us describe tables as Python classes instead of writing raw database commands (SQL). | So we think in Python, not in a second language. |
| **Pillow** | A Python library for editing images (resize, compress, convert formats). | Powers the "auto-shrink images" feature in Phase 3. |

> **Jargon check - "library" vs "framework":** A **library** is a box of tools
> you reach into when *you* want (like Pillow: "hey, shrink this image"). A
> **framework** is a skeleton that runs the show and calls *your* code at the
> right moments (like FastAPI: it runs the server and calls your functions when
> a request arrives). Rough rule: you call a library; a framework calls you.

---

## Phase 1: The Foundation - Database + a Living Server

**Goal of this phase:** Get a backend server running that (a) is alive and can
answer a simple "are you okay?" request, and (b) has a database ready to
remember details about every file we'll store.

We are **not** uploading files yet. This phase is just laying the foundation -
like pouring the concrete slab before building the house.

### Step 1: The virtual environment (`.venv`)

Before installing anything, we created a **virtual environment**.

- **What it is:** a private, isolated copy of Python *just for this project*,
  living in a folder called `backend/.venv/`.
- **The analogy:** it's a **separate toolbox for this one project**. Anything we
  install goes in *this* box, not into your whole computer. So two projects can
  use different versions of the same tool without fighting.
- **Command we ran** (from inside the `backend` folder):
  ```
  python -m venv .venv
  ```
  `python -m venv` means "run Python's built-in `venv` tool," and `.venv` is the
  name of the folder to create.

> `.venv` is listed in `.gitignore`, so it is **never** uploaded to GitHub. It's
> big, machine-specific, and can always be rebuilt from `requirements.txt`.

### Step 2: The shopping list (`requirements.txt`)

`backend/requirements.txt` is a plain text list of every Python package the
project needs, with exact version numbers:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
python-multipart==0.0.20
pillow==11.1.0
```

- **Why pin exact versions (the `==0.115.6` part)?** So the app behaves
  identically on any computer. Without it, someone installing later might get a
  newer, slightly different version that breaks something. This is a
  professional habit.
- `python-multipart` is a helper FastAPI needs specifically to receive uploaded
  files. `pillow` isn't used until Phase 3, but we install it now so the
  toolbox is complete.
- **Command we ran** to install everything on the list:
  ```
  .venv/Scripts/python.exe -m pip install -r requirements.txt
  ```
  `pip` is Python's package installer (think "app store for Python code"), and
  `-r requirements.txt` means "install everything listed in this file."

### Step 3: Connecting to the database (`app/database.py`)

This file sets up the connection to our SQLite database. The key lines:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./vault.db"
```
This says "our database is a SQLite file named `vault.db` in the current
folder." When the app first runs, this file is created automatically.

```python
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
```
The **engine** is the actual pipe/connection to the database file.
(`check_same_thread=False` is a small SQLite-specific setting that lets FastAPI
talk to the database from different tasks safely. You can ignore the details.)

```python
SessionLocal = sessionmaker(...)
```
A **session** is a single "conversation" with the database - you open one, do
your reads/writes, then close it. `SessionLocal` is a factory that hands us a
fresh conversation whenever we need one.

```python
Base = declarative_base()
```
`Base` is the **parent class** all our table definitions will inherit from. It's
the shared blueprint that gives SQLAlchemy its magic powers to turn Python
classes into real database tables.

### Step 4: Describing the `files` table (`app/models.py`)

This is where we define **what we remember about each file**. In database terms,
a **table** is like a spreadsheet: columns are the kinds of info, rows are
individual files.

Our `File` class becomes a table called `files` with these columns:

| Column | What it stores | Example |
|--------|----------------|---------|
| `id` | A unique random ID for each file | `3f9a...-uuid` |
| `filename` | The original name | `cat.png` |
| `original_size` | Size in bytes before shrinking | `2048000` |
| `compressed_size` | Size after shrinking (empty until Phase 3) | `310000` |
| `file_hash` | The file's unique "fingerprint" (Phase 2) | `a1b2c3...` |
| `upload_date` | When it was uploaded | `2026-07-07 12:00` |
| `user_id` | Which user owns it (empty for now) | *(null)* |

> **Why is `user_id` here already if we have no users yet?** We *know* Phase 6
> will add login accounts. Adding an empty column now is nearly free; adding a
> column to a table that's already full of data later is a fiddly, error-prone
> job called a "migration." So we leave the door open now. This is thinking
> ahead - a good engineering instinct.

> **What's a `hash`/`fingerprint`?** A hash is a short string of
> letters/numbers calculated from a file's exact contents. Change one pixel and
> the hash changes completely. Two identical files always produce the *same*
> hash. That's how we'll detect duplicates in Phase 2. `unique=True` on this
> column means the database itself refuses to store two files with the same
> fingerprint.

### Step 5: The app itself + the health check (`app/main.py`)

```python
Base.metadata.create_all(bind=engine)
```
On startup, this line tells SQLAlchemy: "look at every table I defined, and if
it doesn't exist in the database file yet, create it." This is why `vault.db`
and the `files` table appear automatically the first time we run.

```python
app = FastAPI(title="Cloud File Optimizer & Smart Vault")
```
This creates the actual API application (our "waiter").

```python
@app.get("/api/health")
def health_check():
    return {"status": "ok"}
```
This defines our first **endpoint**. An **endpoint** is one specific address the
frontend can call, like a single item on the waiter's menu.
- `@app.get("/api/health")` means "when someone visits the web address
  `/api/health` with a GET request, run the function below."
- **GET** is the type of request that means "just give me information, don't
  change anything" (as opposed to POST, which we'll use to upload/change data).
- It returns `{"status": "ok"}` - a tiny message that just proves the server is
  alive. This is called a **health check**, and real production systems use them
  constantly to know if a service is up.

### How we *verified* Phase 1 works

Writing code isn't enough - we ran it and checked:
1. Started the server (see commands below).
2. Visited `/api/health` → got back `{"status": "ok"}`. ✅ Server alive.
3. Visited `/docs` → FastAPI's auto-built interactive test page loaded. ✅
4. Opened `vault.db` directly and confirmed the `files` table exists with all 7
   columns. ✅ Database ready.

---

## Phase 2: Uploads + the "Never Store the Same File Twice" Magic

**Goal of this phase:** Let people actually upload files, and make the app smart
enough to notice when a file is a duplicate of one it already has - and if so,
*not* waste space storing a second copy.

This is the first of the app's two headline "twists" (deduplication). It's also
the first time the app changes data instead of just reporting it.

### The big idea in one picture

When a file arrives, we don't save it immediately. We do this:

```
upload arrives
      │
      ▼
compute its fingerprint (SHA-256 hash)
      │
      ▼
is that fingerprint already in the database?
      │
   ┌──┴──────────────┐
  YES                NO
   │                  │
return the         save file to disk,
existing record    add a database row,
(touch NOTHING     return the new record
 on disk)          (deduplicated: false)
(deduplicated:
 true)
```

The key insight: **a duplicate file never gets written to disk at all.** We
figure out it's a duplicate *before* saving. That's the whole space-saving trick.

### What's a "hash" again, and why SHA-256?

A **hash** is a fingerprint for data. You feed in a file's exact bytes and get
back a fixed-length string of letters and numbers. Two rules make it perfect for
finding duplicates:

1. **Same content → same hash, every time.** Upload the same photo twice, you
   get the same fingerprint twice.
2. **Different content → different hash.** Change a single pixel and the
   fingerprint changes completely.

**SHA-256** is a specific, industry-standard hashing recipe. The "256" means the
fingerprint is 256 bits long (shown as 64 hex characters, like
`580787662cc5...`). It's built into Python - no extra package needed.

So instead of comparing whole files byte-by-byte (slow, and we'd need every file
in memory), we just compare their short fingerprints. If two fingerprints match,
the files are identical.

### The new files we added

| File | Job |
|------|-----|
| `app/storage.py` | The fingerprinting + save-to-disk helpers. |
| `app/schemas.py` | Describes the shape of the JSON we send back. |
| `app/main.py` (edited) | The new `POST /api/upload` endpoint that ties it together. |

### Step 1: The fingerprint + save helpers (`app/storage.py`)

**Reading the file in chunks.** A naive approach reads the whole file into
memory at once. That's fine for a 10 KB text file, but a 2 GB video would eat 2
GB of RAM. Instead we read it in **chunks** - 1 MB at a time:

```python
CHUNK_SIZE = 1024 * 1024  # 1 MB (1024 * 1024 bytes)
```

The hashing function:

```python
async def compute_hash(upload_file):
    hasher = hashlib.sha256()      # start an empty fingerprint calculator
    total_bytes = 0
    while True:
        chunk = await upload_file.read(CHUNK_SIZE)  # grab up to 1 MB
        if not chunk:              # empty chunk = end of file, stop
            break
        hasher.update(chunk)       # feed this chunk into the fingerprint
        total_bytes += len(chunk)  # tally the size as we go
    await upload_file.seek(0)      # rewind the file back to the start
    return hasher.hexdigest(), total_bytes
```

- `hasher.update(chunk)` **adds** each chunk to the running fingerprint. After
  the last chunk, `hasher.hexdigest()` gives the final fingerprint as text.
- We **count the bytes** (`total_bytes`) at the same time, so we learn the
  file's size for free without a separate step. This becomes `original_size`.
- **`await upload_file.seek(0)` - the important subtle bit.** Reading the file to
  hash it "uses up" the reading position, like a bookmark now sitting at the end
  of the book. `seek(0)` moves that bookmark back to page 1, so when we save the
  file next, we read it from the beginning again. Forget this line and you'd save
  an empty file.

> **Jargon check - `async` / `await`:** You'll see `async def` and `await` on
> these functions. Reading a file or a network upload involves *waiting*
> (for the disk, for the network). `async` lets the server go do useful work for
> *other* users during that wait instead of freezing. `await` marks the exact
> spots where waiting happens. For now: "if a function talks to files or the
> network, it's usually `async`, and you `await` it when you call it."

**Saving the file** (only reached for genuinely new files):

```python
async def save_file(upload_file, file_hash):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)   # make the folder if missing
    extension = Path(upload_file.filename or "").suffix   # ".png", ".txt", ...
    destination = UPLOAD_DIR / f"{file_hash}{extension}"  # e.g. 580787...txt
    with destination.open("wb") as out_file:        # "wb" = write, binary mode
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break
            out_file.write(chunk)
    return destination
```

- **Why name the saved file by its hash** instead of its original name? Because
  two different users might both upload `report.pdf` with different contents -
  naming by original name would clash. The hash is guaranteed unique per unique
  content. We still remember the *original* name (`a.txt`) in the database for
  display; the file *on disk* is just named by its fingerprint.
- `"wb"` means **write bytes**. Files aren't text, they're raw bytes (a photo, a
  zip, a PDF), so we open in binary mode.
- `mkdir(parents=True, exist_ok=True)` = "create the `uploaded_files/` folder,
  and don't error if it already exists."

### Step 2: The response shape (`app/schemas.py`)

We already have `app/models.py` describing the *database table*. So why a second
file describing almost the same fields?

- **`models.py` = the database's internal shape.**
- **`schemas.py` = the public shape we send out as JSON.**

Keeping them separate is a deliberate, professional habit: you can rearrange your
database later without accidentally changing what your API promises to the
outside world. They just happen to look similar right now.

These schemas are written with **Pydantic** - a library FastAPI uses to define
and *validate* data shapes:

```python
class FileOut(BaseModel):
    id: str
    filename: str
    original_size: int
    compressed_size: int | None   # the "| None" means "or empty"
    file_hash: str
    upload_date: datetime
    user_id: str | None
    model_config = ConfigDict(from_attributes=True)
```

- `int | None` means "an integer **or** nothing." `compressed_size` is empty
  until Phase 3 shrinks the file, so it's allowed to be `None`.
- `from_attributes=True` is a small permission slip that lets Pydantic build this
  response by reading the fields straight off a SQLAlchemy database object.

```python
class UploadResponse(BaseModel):
    deduplicated: bool   # True if this file already existed
    file: FileOut        # the file's details, nested inside
```

`deduplicated` is the flag that tells the frontend "heads up, this was already
here - we saved you the space."

### Step 3: The upload endpoint (`app/main.py`)

```python
@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
```

- **`@app.post(...)`** - unlike Phase 1's `@app.get`, this is a **POST**: the
  request type that means "here's some data, do something with it." Uploading is
  a POST because we're *sending* a file, not just asking for info.
- **`response_model=UploadResponse`** tells FastAPI "the reply will look like
  this," which also documents it automatically on the `/docs` page.
- **`file: UploadFile = File(...)`** - FastAPI hands us the uploaded file as an
  `UploadFile` object. The `File(...)` (with three dots meaning "required")
  tells FastAPI to look for it in the upload form.
- **`db: Session = Depends(get_db)`** - this is **dependency injection**:
  FastAPI automatically opens a fresh database conversation for us and closes it
  when we're done. We just ask for `db` and it appears.

The logic inside:

```python
    file_hash, size = await storage.compute_hash(file)   # fingerprint it

    existing = db.query(models.File).filter(
        models.File.file_hash == file_hash).first()       # already have it?

    if existing is not None:                              # YES - it's a dupe
        return UploadResponse(deduplicated=True,
                              file=FileOut.model_validate(existing))

    await storage.save_file(file, file_hash)             # NO - save to disk
    record = models.File(filename=file.filename,
                         original_size=size, file_hash=file_hash)
    db.add(record); db.commit(); db.refresh(record)      # write the DB row
    return UploadResponse(deduplicated=False,
                          file=FileOut.model_validate(record))
```

- `db.query(...).filter(...).first()` is SQLAlchemy for "SELECT the first file
  whose `file_hash` equals this fingerprint." `.first()` returns the row, or
  `None` if there isn't one.
- `db.add(record)` stages the new row; `db.commit()` actually saves it;
  `db.refresh(record)` reloads it so we get the auto-filled `id` and
  `upload_date` back.

**The safety net (the `try/except IntegrityError` bit).** There's a rare race:
two identical *new* files uploaded at almost the same instant could both check
"do we have this?", both see "no", and both try to save. The database's
`unique=True` rule on `file_hash` (set back in Phase 1) blocks the second one
with an `IntegrityError`. We catch that, undo our half-finished write
(`db.rollback()`), and just return the copy that won the race. This is
**defensive programming** - trusting the database as the final guardrail rather
than assuming our check is always enough.

### How we *verified* Phase 2 works

Code that isn't tested is just a guess. We started the server and ran three real
uploads with `curl`:

1. Uploaded `a.txt` → response `deduplicated: false`, got a new id. ✅
2. Uploaded the **exact same** `a.txt` again → `deduplicated: true`, **same id
   and same hash** as before. ✅ Duplicate correctly recognized.
3. Uploaded a **different** file `b.txt` → `deduplicated: false`, a brand-new id
   and different hash. ✅

Then we checked the two places data lives:
- **On disk:** `uploaded_files/` held exactly **2** files (not 3), each named by
  its hash. ✅ The duplicate was never written.
- **In the database:** exactly **2** rows. ✅

That's the whole promise of this phase proven: identical content is stored once.

---

## Command Cheat Sheet (bookmark this)

All commands are run from inside the `backend/` folder unless noted. On Windows
PowerShell:

**Start the backend server** (keep this running in its own terminal tab):
```
.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```
- `--reload` means "automatically restart when I change the code" - great while
  developing.
- Once running, open these in your browser:
  - `http://127.0.0.1:8000/api/health` - the health check
  - `http://127.0.0.1:8000/docs` - the interactive API test page

**Stop the server:** press `Ctrl + C` in that terminal.

**Test a file upload** (from any folder, with the server running). The easiest
way is the interactive `/docs` page: open `http://127.0.0.1:8000/docs`, expand
`POST /api/upload`, click *Try it out*, choose a file, and *Execute*. Upload the
same file twice and watch `deduplicated` flip from `false` to `true`.

Or from the command line with `curl` (replace `myfile.png` with a real file):
```
curl -F "file=@myfile.png" http://127.0.0.1:8000/api/upload
```
`-F "file=@..."` means "send this as an uploaded form file." The `@` tells curl
"read an actual file from disk," not send the literal text.

**Reinstall dependencies** (e.g. on a new computer after cloning):
```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

> `127.0.0.1` (also called `localhost`) means "this very computer." `8000` is
> the **port** - like an apartment number that tells the request which program
> on the computer to go to.

---

## Glossary (every jargon word, one line each)

- **Backend** - the behind-the-scenes engine (server + database + logic). Users
  don't see it.
- **Frontend** - the part you see and click in the browser.
- **API** (Application Programming Interface) - the agreed set of "requests" the
  frontend can send the backend. The waiter between them.
- **Endpoint** - one specific API address/action, e.g. `/api/health`.
- **GET / POST** - types of requests. GET = "give me info." POST = "here's data,
  do something with it" (e.g. upload).
- **Server** - a program (or computer) that waits for requests and responds.
- **Framework** - a skeleton that runs your app and calls your code (FastAPI).
- **Library** - a toolbox you call when you need it (Pillow).
- **Database** - organized permanent storage for information.
- **SQLite** - a database that's just one file. No setup.
- **Table** - a spreadsheet-like structure in a database. Columns = fields,
  rows = records.
- **SQLAlchemy / ORM** - a translator so we define tables in Python instead of
  raw database language (SQL).
- **SQL** - the traditional language for talking to databases. SQLAlchemy writes
  it for us.
- **Engine** - the live connection to the database file.
- **Session** - one open "conversation" with the database.
- **Model** - a Python class that describes one database table (our `File`).
- **Hash / fingerprint** - a short code derived from a file's contents; unique
  per unique file. Powers duplicate detection.
- **SHA-256** - a specific, standard hashing recipe producing a 256-bit (64
  hex-character) fingerprint. Built into Python. What we use to fingerprint files.
- **Deduplication ("dedup")** - detecting that a file is identical to one already
  stored, and reusing the existing copy instead of saving a duplicate.
- **Chunk / streaming** - reading a file in small pieces (we use 1 MB) instead of
  all at once, so memory stays small even for huge files.
- **seek(0)** - rewinding a file's read position back to the start, so it can be
  read again from the beginning.
- **UploadFile** - FastAPI's object representing a file someone uploaded.
- **Pydantic** - the library FastAPI uses to describe and validate data shapes
  (our `schemas.py`). Guards what goes in and out of the API.
- **Schema** - a description of a data shape (which fields, which types). Ours
  describe the JSON the API returns.
- **POST** - the request type meaning "here's data, do something with it" (used
  for uploads), as opposed to GET ("just give me info").
- **Dependency injection (`Depends`)** - FastAPI automatically creating and
  handing us something we need (like a database session) when a request comes in.
- **Binary mode (`"wb"`)** - opening a file to write raw bytes (photos, PDFs),
  not text.
- **async / await** - a way of writing functions that can pause while waiting
  (for disk or network) and let the server serve other users meanwhile.
- **IntegrityError** - the error a database raises when a write would break a
  rule (like our "no two files with the same hash"). We catch it as a safety net.
- **Virtual environment (`.venv`)** - an isolated per-project Python + its
  packages.
- **pip** - Python's package installer (its "app store").
- **requirements.txt** - the list of packages + versions the project needs.
- **Package / dependency** - a chunk of reusable code someone else wrote that we
  install and use.
- **Port** - a numbered "door" on a computer (we use 8000) so requests reach the
  right program.
- **localhost / 127.0.0.1** - "this computer, right here."
- **Health check** - a trivial endpoint that just confirms the server is alive.
- **Migration** - the (annoying) process of changing a database's structure
  after it already holds data.
- **Git / commit / GitHub** - Git tracks the history of your code; a commit is
  one saved snapshot; GitHub is the website that stores it online.

---

## Progress Tracker

- [x] **Phase 1** - Database + running server with a health check
- [x] **Phase 2** - Hashing + duplicate detection on upload ← *you are here*
- [ ] **Phase 3** - Auto-shrink images to WebP
- [ ] **Phase 4** - React dashboard (upload zone + file table)
- [ ] **Phase 5** - Analytics charts (space saved, file types)
- [ ] **Phase 6** - User accounts, login, and vault encryption
