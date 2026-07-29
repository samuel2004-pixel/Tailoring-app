# YWAM Tailoring Training Centre - Management System

A simple, complete management system for a tailoring training centre:
student registration, attendance, monthly fees, and auto-generated
completion certificates - built around your existing application form
and certificate templates.

## Features

- **Student registration** - all fields from your paper application form
  (personal details, course, batch, contact, emergency contact, admission
  date, start/end date, duration, monthly fee).
- **Attendance** - mark Present/Absent per day for all active students,
  with full history and date-range filtering.
- **Monthly fees** - record payments per student per month, see
  total due / paid / balance per student and centre-wide.
- **Certificate auto-generation** - fills your official "Diploma in
  Tailoring" 3-month or 6-month certificate template with the student's
  name and course dates and produces a ready-to-print PDF, identical in
  layout to your original certificates.
- **Export** - Students, Attendance, and Fees can each be exported as
  **CSV** (for Excel) or a formatted **PDF report**, with filters
  (date range / student / month) carried into the export.
- **Biometric attendance (ZKTeco)** - if you have a ZKTeco (or
  compatible eSSL/Realtime) fingerprint device on the same Wi-Fi/LAN,
  the app can pull that day's punches straight from the device and
  mark students Present automatically. Manual marking still works
  alongside it for anyone without a device punch.

## Requirements

- Python 3.9 or newer (download from https://www.python.org/downloads/
  if you don't have it - tick "Add Python to PATH" during install on
  Windows).
- A PostgreSQL database (version 12+). This can be a local install, a
  Docker container, or a hosted database (Render, Railway, Supabase,
  RDS, etc.).
- Internet connection is only needed the very first time you run it, to
  download the small set of Python packages listed in
  `requirements.txt`, and for the page styling (Bootstrap) to load in
  your browser.

## Getting started

### Windows
1. Unzip this folder anywhere (e.g. Desktop).
2. Double-click **run.bat**.
3. A black window will open, install what's needed, then say the app is
   running - open your browser and go to **http://127.0.0.1:5000**

### Mac / Linux
1. Unzip this folder.
2. Open a Terminal in the folder and run:
   ```
   ./run.sh
   ```
3. Open your browser at **http://127.0.0.1:5000**

Each time after the first, you can just run `run.bat` (Windows) or
`./run.sh` (Mac/Linux) again to start the app - your data is saved
between runs.

To stop the server, close the terminal/command window or press
`CTRL + C`.

## How your data is stored

All student, attendance, fee, and certificate records are stored in a
**PostgreSQL** database, configured through a single environment
variable, `DATABASE_URL`:

```
postgresql://username:password@host:5432/tailoring_center
```

### First-time setup

1. Create an empty database (e.g. `createdb tailoring_center`, or via
   your hosting provider's dashboard).
2. Set `DATABASE_URL` before starting the app, e.g. on Mac/Linux:
   ```
   export DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/tailoring_center"
   ./run.sh
   ```
   or on Windows (PowerShell):
   ```
   $env:DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/tailoring_center"
   run.bat
   ```
   If `DATABASE_URL` isn't set, the app falls back to
   `postgresql://postgres:postgres@localhost:5432/tailoring_center`
   (see `db.py`) - fine for local testing, but you should always set it
   explicitly for anything real.
3. The app creates all required tables automatically on first run
   (via `db.init_db()`), including a default login:
   - **Username:** `ywam`
   - **Password:** `1974`

   You can also create the schema manually ahead of time:
   ```
   psql "$DATABASE_URL" -f schema.sql
   ```

### Migrating data from an older SQLite version of this app

If you were previously running this app with SQLite
(`data/centre.db`), a one-time export of that data is included as
`data_seed.sql` - plain SQL `INSERT` statements matching the schema
above. Load it into your new PostgreSQL database **after** the schema
exists:

```
psql "$DATABASE_URL" -f schema.sql
psql "$DATABASE_URL" -f data_seed.sql
```

It's safe to re-run - existing rows are skipped (`ON CONFLICT DO
NOTHING`). If you need to regenerate `data_seed.sql` from a different
`centre.db` file, see the migration script described at the bottom of
this file.

- **Back it up regularly** using PostgreSQL's own tools, e.g.
  `pg_dump "$DATABASE_URL" > backup.sql`.
- To start completely fresh, drop and recreate the database, then
  restart the app so it can rebuild the schema.

## Folder structure

```
tailoring_center/
├── app.py                  Main application (routes/logic)
├── db.py                   Database setup (PostgreSQL)
├── schema.sql              Standalone PostgreSQL schema
├── data_seed.sql           One-time data export from a prior SQLite install (optional)
├── certificate.py          Certificate PDF generator
├── requirements.txt        Python packages needed
├── run.bat / run.sh        One-click start scripts
├── assets/
│   ├── cert_3_months.pdf   Official 3-month certificate template
│   └── cert_6_months.pdf   Official 6-month certificate template
├── templates/               Web page templates
└── static/
    └── style.css            App styling
```

## Using the system

1. **Register a student**: Students → Register Student. Fill in the
   same details as your paper form. Set the course duration (3 or 6
   months), start/end dates, and monthly fee.
2. **Mark attendance**: Attendance → pick a date → mark each active
   student Present/Absent → Save. Change the date at the top to mark
   attendance for a different day, or to review/edit a past day.
3. **Record a fee payment**: Fees → choose student, month, amount, date,
   mode → Save Payment. The student's profile page shows Total Due,
   Paid, and Balance automatically (Due = monthly fee × duration).
4. **Generate a certificate**: on a student's profile page, click
   "Generate Certificate", confirm/adjust the name, duration, and
   dates, then click Generate & Download - a filled PDF certificate
   downloads straight away, matching your original template exactly.
5. **Export data**: on the Students, Attendance History, and Fees
   History pages, use the "Export CSV" / "Export PDF" buttons - any
   filters you've set (date range, student, month) are applied to the
   export too.

## Setting up biometric attendance (ZKTeco)

1. **Give the device a fixed IP address** on your Wi-Fi/router, and
   make sure the computer running this app is on the same network.
   (On the device: Menu → Comm. → Ethernet - note the IP shown there,
   or set a static one.)
2. In the app, go to **Device** (top menu) → enter the device's IP
   address → click **Test Connection** to confirm it's reachable.
3. Go to **Attendance → Link Biometric IDs**. This shows every
   fingerprint already enrolled on the device (with the ID number it
   was enrolled under). Type that same ID into the matching student's
   row and click **Save Links**. (Fingerprint enrolment itself - i.e.
   scanning someone's finger for the first time - is still done on the
   device's own menu, same as before; this step just tells the app
   "device ID 7 = this student".)
4. From then on, open **Attendance**, pick a date, and click
   **Sync from Biometric Device** - anyone who punched that day is
   marked Present automatically. Students who didn't punch (forgot,
   device down, not yet linked, etc.) are left for you to mark
   manually, so nothing is silently assumed either way.
5. Attendance records show a small "Device" or "Manual" tag so you can
   always see how each entry was marked.

If "Test Connection" fails: double-check the IP address, that the
device and computer are on the same network, and that no firewall is
blocking it. If you've set a communication password on the device
itself, enter that in the "Comm Password" field too.

## Customising

- **Centre name/address/logo on certificates**: the certificates are
  generated by overlaying the student's name and dates directly onto
  your original `assets/cert_3_months.pdf` / `cert_6_months.pdf` files,
  so if you ever update the official templates, just replace those two
  files (keep the same filenames) and the system will use the new
  design automatically.
- **Courses/Batches list**: edit the `COURSES` and `BATCHES` lists near
  the top of `app.py`.
- **Colours/branding**: edit `static/style.css`.

## Support

This is a self-contained Flask (Python) web application that runs
entirely on your own computer - no data is sent anywhere else. If you
want to make it accessible to more than one computer on your premises
(e.g. a front-desk PC and a coordinator's laptop), the app can be run on
one computer and accessed from others on the same Wi-Fi network via
that computer's local IP address and port 5000 - ask a local IT person
to help set this up if needed.
