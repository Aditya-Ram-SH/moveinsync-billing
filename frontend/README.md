# Frontend - MoveInSync Billing Platform

React + TypeScript frontend for the MoveInSync Billing & Reporting Platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend runs on: `http://localhost:5173`

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Recharts** - Chart library
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible component primitives
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── axios.ts          # API client configuration
│   ├── components/
│   │   ├── ui/               # Reusable UI components
│   │   ├── ContractDetails.tsx
│   │   ├── FormField.tsx
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── context/
│   │   └── AuthContext.tsx   # Authentication context
│   ├── pages/
│   │   ├── Billing.tsx       # Billing management
│   │   ├── Contracts.tsx     # Contract management
│   │   ├── Dashboard.tsx     # Role-specific dashboards
│   │   ├── Login.tsx         # Login page
│   │   └── TripsIngest.tsx   # Trip CSV upload
│   ├── App.tsx               # Main app component
│   └── main.tsx              # Entry point
├── package.json
└── vite.config.ts
```

## 🔐 Authentication

The app uses JWT-based authentication:

1. User logs in via `/` (Login page)
2. Token stored in localStorage
3. Token included in API requests via Axios interceptor
4. Protected routes check authentication status

## 📄 Pages

### Login (`/`)
- User authentication
- Role-based redirect after login

### Dashboard (`/dashboard`)
- Role-specific dashboards:
  - **Admin**: System overview
  - **Client**: Cost analytics and vendor breakdown
  - **Vendor**: Payout analytics and client breakdown
  - **Employee**: Personal trip history and incentives

### Contracts (`/contracts`)
- View all contracts
- Create new contracts (Admin only)
- Contract details and configuration

### Trip Ingestion (`/trips/ingest`)
- Upload CSV files with trip data
- Validation and error reporting
- Available to Vendors and Admins

### Billing (`/billing`)
- List billing runs
- Create new billing runs (Admin only)
- View billing reports
- Export CSV reports

## 🎨 UI Components

### Reusable Components
- `Button` - Styled button component
- `Card` - Card container
- `Input` - Text input
- `Select` - Dropdown select
- `Table` - Data table
- `FormField` - Form field wrapper

### Charts
Using Recharts library:
- Line charts for trends
- Bar charts for comparisons
- Pie charts for distributions
- Area charts for cumulative data

## 🔧 Configuration

### API Endpoint

Default: `http://localhost:8000`

Can be configured via environment variable:
```env
VITE_API_URL=http://localhost:8000
```

### CORS

Backend must allow frontend origin. Configured in `backend/app/core/config.py`:
```python
CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
```

## 🐛 Troubleshooting

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues

1. Verify backend is running: `http://localhost:8000/health`
2. Check API URL in `src/api/axios.ts`
3. Verify CORS settings in backend

### Type Errors

```bash
# Check TypeScript configuration
npm run build

# Fix type issues
# Check tsconfig.json settings
```

## 📦 Dependencies

Key dependencies:
- `react` & `react-dom` - React library
- `react-router-dom` - Routing
- `@tanstack/react-query` - Data fetching
- `axios` - HTTP client
- `recharts` - Charts
- `tailwindcss` - Styling
- `lucide-react` - Icons

See `package.json` for complete list.

## 🚀 Production Build

```bash
# Build for production
npm run build

# Output in dist/ directory
# Serve with any static file server
```

## 📝 Development Notes

- Uses Vite for fast HMR (Hot Module Replacement)
- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for styling
- React Query for server state management

---

For backend setup, see `../backend/README.md`
For complete setup guide, see `../SETUP.md`
