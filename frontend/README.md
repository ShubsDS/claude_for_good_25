# AI Essay Grading Frontend

A React-based frontend for the AI Essay Grading System. This application provides an intuitive interface for teachers to upload assignments, create rubrics, and review AI-generated grading results.

## Features

- **Landing Page**: Simple teacher/student role selection
- **Assignment Upload**: Enter Canvas assignment ID and upload rubric
- **Rubric Management**: Upload rubric files or create rubrics using the built-in text editor
- **Bulk Grading**: Automatically grade all submissions for an assignment
- **Interactive Results View**:
  - Side-by-side essay and grading panel
  - Color-coded text highlighting by criterion
  - Editable scores and feedback
  - Student-by-student navigation

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Styling**: TailwindCSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`
- Canvas LMS API credentials (for automatic submission ingestion)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure Canvas credentials:
   - Copy `.env.example` to `.env`
   - Update the Canvas credentials:
     ```
     VITE_CANVAS_BASE_URL=https://your-canvas-instance.edu
     VITE_CANVAS_API_TOKEN=your_api_token_here
     VITE_CANVAS_COURSE_ID=your_course_id
     ```

3. Start the development server:
```bash
npm run dev
```

The application will be available at [http://localhost:5173/](http://localhost:5173/)

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ui/              # shadcn/ui components
│   ├── pages/               # Page components
│   │   ├── Home.tsx         # Landing page
│   │   ├── UploadPage.tsx   # Assignment & rubric upload
│   │   ├── GradingPage.tsx  # Loading screen during grading
│   │   └── ResultsPage.tsx  # Grading results viewer
│   ├── services/
│   │   └── api.ts           # API integration layer
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   ├── App.tsx              # Main app component with routing
│   └── main.tsx             # Entry point
├── public/                  # Static assets
└── package.json
```

## Usage Flow

1. **Start**: Teacher selects "Continue as Teacher" on the landing page
2. **Upload**:
   - Enter Canvas assignment ID (numeric, e.g., 790778)
   - Upload rubric file OR create rubric using text editor
   - Click "Start Grading"
3. **Canvas Integration** (automatic):
   - System fetches all submissions from Canvas for the given assignment
   - PDFs are automatically converted to text
   - Essays are uploaded to the database
4. **Processing**: Loading screen shows grading progress for each student
5. **Results**:
   - View essay with color-coded highlights
   - Edit scores and feedback for each criterion
   - Navigate between students using Previous/Next buttons
   - Save changes

### Canvas Integration

The application automatically:
- Fetches submissions from Canvas using the assignment ID
- Downloads PDF submissions
- Extracts text from PDFs (TXT files are used directly)
- Uploads all essays to the database for grading

**Note**: Ensure Canvas credentials are properly configured in `.env` file before attempting to grade assignments.

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. Key endpoints used:

- `POST /rubrics/` - Upload rubric
- `GET /essays/` - Get all essays
- `POST /grade` - Grade an essay
- `GET /essays/{id}` - Get specific essay
- `GET /gradings/{id}` - Get grading results

To change the API URL, edit `src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## Customization

### Adding More Criterion Colors

Edit the `CRITERION_COLORS` object in `src/pages/ResultsPage.tsx`:

```typescript
const CRITERION_COLORS: Record<string, string> = {
  THESIS: '#FFE0B2',
  CITATIONS: '#C8E6C9',
  YOUR_CRITERION: '#YOUR_COLOR',
  // Add more...
};
```

### Styling

The application uses TailwindCSS. To customize the theme, edit `tailwind.config.js`.

## Development

### Adding New Pages

1. Create the page component in `src/pages/`
2. Add the route in `src/App.tsx`
3. Update navigation links

### Adding New API Endpoints

1. Add the function to `src/services/api.ts`
2. Add corresponding TypeScript types to `src/types/index.ts`
3. Use React Query hooks for data fetching if needed

## Known Limitations

- Student view is not yet implemented (shows "Coming Soon")
- Canvas assignment browser is not yet implemented (manual ID entry only)
- Save functionality in results view needs backend implementation
- No authentication/authorization

## Future Enhancements

- Canvas assignment browser integration
- Student portal for viewing grades
- Batch export of grading results
- Real-time progress updates using WebSockets
- Advanced filtering and search in results
- Grading history and analytics

## Troubleshooting

### Port Already in Use

If port 5173 is already in use, Vite will automatically try the next available port. Check the terminal output for the actual URL.

### API Connection Errors

Ensure the backend is running on `http://localhost:8000`. You can test it by visiting `http://localhost:8000/docs` in your browser.

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules
npm install
```

## License

MIT
