# Local Development Setup Guide — Phase 1

Architecture for this phase:

```
Local React App (localhost:3000)  ─▶  Local .NET 9 API (localhost:5001)  ─▶  Azure SQL Database (cloud)
```

The API runs on your machine and connects **directly** to Azure SQL — there is
no App Service, Key Vault, or Redis yet. That's all Phase 2.

---

## 1. Provision the Azure SQL Database

If you don't already have one:

```bash
az login

az group create --name rg-busbooking --location centralindia

az sql server create \
  --name busbooking-sqlsrv \
  --resource-group rg-busbooking \
  --location centralindia \
  --admin-user busadmin \
  --admin-password "<Choose-A-Strong-Password!>"

az sql db create \
  --resource-group rg-busbooking \
  --server busbooking-sqlsrv \
  --name BusBookingDb \
  --service-objective S0
```

## 2. Open the Azure SQL firewall for your machine

Azure SQL blocks all inbound connections by default. You must explicitly allow
your current public IP.

**Option A — Azure Portal (fastest for a one-off)**
1. Go to your SQL Server resource (not the database) → **Security → Networking**.
2. Under **Firewall rules**, click **+ Add your client IPv4 address** — the
   portal detects it automatically.
3. Click **Save**.
4. (Local dev convenience only — do **not** do this in production) You may also
   toggle **Allow Azure services and resources to access this server**, but
   for Phase 1 this is not required since you're connecting from your laptop,
   not from Azure.

**Option B — Azure CLI (repeatable / scriptable)**
```bash
# Find your current public IP
MY_IP=$(curl -s ifconfig.me)

az sql server firewall-rule create \
  --resource-group rg-busbooking \
  --server busbooking-sqlsrv \
  --name AllowMyDevMachine \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

> **Note:** Home/office IPs often change (DHCP re-leases, VPN reconnects).
> If you start getting `Cannot open server ... requested by the login` errors,
> re-run the CLI command above — your IP likely changed.

## 3. Get the ADO.NET connection string

```bash
az sql db show-connection-string \
  --server busbooking-sqlsrv \
  --name BusBookingDb \
  --client ado.net
```

Paste it into `backend/BusBooking.Api/appsettings.json` under
`ConnectionStrings:DefaultConnection`, filling in your admin username and
password. Keep `Encrypt=True` — Azure SQL requires TLS.

> For anything beyond solo local dev, don't commit real credentials. Use
> `dotnet user-secrets` instead:
> ```bash
> cd backend/BusBooking.Api
> dotnet user-secrets init
> dotnet user-secrets set "ConnectionStrings:DefaultConnection" "<your full connection string>"
> ```

## 4. Create the database schema

Run the DDL scripts against Azure SQL, in order, using `sqlcmd`, Azure Data
Studio, or SSMS:

```bash
sqlcmd -S busbooking-sqlsrv.database.windows.net -d BusBookingDb -U busadmin -P "<password>" -i database/01_schema.sql
sqlcmd -S busbooking-sqlsrv.database.windows.net -d BusBookingDb -U busadmin -P "<password>" -i database/02_refund_function_and_procs.sql
sqlcmd -S busbooking-sqlsrv.database.windows.net -d BusBookingDb -U busadmin -P "<password>" -i database/03_seed_data.sql   # optional sample data
```

Alternatively, once the C# models and DbContext are in place, you can let EF
Core generate migrations instead of hand-run DDL:

```bash
cd backend/BusBooking.Api
dotnet tool install --global dotnet-ef   # once
dotnet ef migrations add InitialCreate
dotnet ef database update
```
(If you use EF migrations, skip `01_schema.sql` but still run
`02_refund_function_and_procs.sql`, since scalar functions/stored procedures
aren't modeled by EF's migration system.)

## 5. Run the backend API

```bash
cd backend/BusBooking.Api
dotnet restore
dotnet run
```

The API listens on `https://localhost:5001` (see `Properties/launchSettings.json`).
Swagger UI opens automatically at `https://localhost:5001/swagger` — use it to
smoke-test `POST /api/auth/register`, `GET /api/bus/search`, etc. before wiring
up the frontend.

## 6. Run the React frontend

```bash
cd frontend
npm install
npm start
```

React starts on `http://localhost:3000`. It calls the API at
`https://localhost:5001/api` (configurable via `REACT_APP_API_BASE_URL` in a
`.env.local` file if you change the API port).

If the browser complains about the API's self-signed local HTTPS certificate,
either accept it once by visiting `https://localhost:5001/swagger` directly
and trusting the cert, or run:
```bash
dotnet dev-certs https --trust
```

## 7. Quick end-to-end smoke test

1. `POST /api/auth/register` → get a `userId` + token.
2. Run `database/03_seed_data.sql` (or add your own trip) so `GET /api/bus/search`
   returns a trip.
3. Load the React app, search for the seeded route, open the `BookingWizard`,
   pick seats, points, fill passenger details, hit **Proceed to pay** — you
   should see a UPI QR code and a live 3-minute countdown.
4. Click **I have paid (simulate confirmation)** to confirm the booking.
5. Call `POST /api/booking/{id}/cancel` to see the refund tiers in action —
   try it against bookings with different `DepartureDateTime` values to see
   the 90/80/70/0% bands.

---

## What changes in Phase 2 (for reference)

| Concern | Phase 1 (now) | Phase 2 (later) |
|---|---|---|
| Hosting | `dotnet run` + `npm start` locally | Azure App Service (API + static React build) |
| Secrets | `appsettings.json` / user-secrets | Azure Key Vault + Managed Identity |
| DB access | Direct public endpoint + firewall IP rules | Private Endpoint / VNet integration, no public firewall rules |
| Caching | None | Azure Cache for Redis for seat-map/search results |
| Edge | None | Azure Front Door + Application Gateway (WAF) |
| Reports | N/A | RDLC reports rendered server-side, stored in Azure Storage |
