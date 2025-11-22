# Frontend MVC Architecture Documentation

## Overview
The frontend has been refactored to follow a proper MVC (Model-View-Controller) architecture, splitting the monolithic `index.html` file into organized, maintainable modules.

## Directory Structure

```
static/
├── css/
│   └── styles.css                    # All custom styles
├── js/
│   ├── app.js                        # Main application entry point
│   ├── models/                       # Data models
│   │   ├── Candidate.js              # Candidate model with validation
│   │   └── Exam.js                   # Exam model with eligibility logic
│   ├── views/                        # View components (UI rendering)
│   │   ├── CandidateFormView.js      # Form input handling
│   │   ├── ResultsView.js            # Results display
│   │   └── MarksheetScannerView.js   # Marksheet scanner UI
│   ├── controllers/                  # Controllers (business logic coordination)
│   │   ├── CandidateController.js    # Candidate form controller
│   │   └── MarksheetController.js    # Marksheet scanner controller
│   ├── services/                     # Service layer (API & business logic)
│   │   ├── ExamService.js            # Exam eligibility checking
│   │   └── ApiService.js             # API communication
│   ├── utils/                        # Utility functions
│   │   └── security.js               # XSS protection utilities
│   └── data/                         # Data files
│       └── exams.js                  # Mock exam database
└── templates/
    └── index.html                    # Main HTML template (minimal)
```

## Architecture Components

### 1. Models (`js/models/`)

**Purpose**: Represent data structures and contain business logic for data validation.

#### `Candidate.js`
- Represents a candidate with all their information
- Validates candidate data (email format, age calculation, percentage ranges)
- Methods:
  - `calculateAge(dob)`: Calculates age from date of birth
  - `validate()`: Validates all candidate fields
  - `toObject()`: Converts to plain object

#### `Exam.js`
- Represents an exam with eligibility criteria
- Contains eligibility checking logic
- Methods:
  - `isEligible(candidate)`: Checks if a candidate is eligible
  - `toObject()`: Converts to plain object

### 2. Views (`js/views/`)

**Purpose**: Handle UI rendering and user interaction with the DOM.

#### `CandidateFormView.js`
- Manages the candidate registration form
- Handles form data collection and validation
- Displays form messages
- Methods:
  - `getFormData()`: Collects form input values
  - `validateInput()`: Validates form input
  - `showMessage(message, type)`: Displays messages
  - `reset()`: Resets the form

#### `ResultsView.js`
- Manages the display of eligibility results
- Renders exam cards
- Methods:
  - `renderExamCard(exam)`: Creates HTML for an exam card
  - `displayExams(exams)`: Displays list of eligible exams
  - `showNoResults(candidate)`: Shows no results message
  - `clear()`: Clears results

#### `MarksheetScannerView.js`
- Manages the marksheet scanner UI
- Handles file input and scan results display
- Methods:
  - `getFormData()`: Gets scanner form data
  - `showMessage(message, type)`: Displays messages
  - `displayResults(fields)`: Shows extracted marksheet data
  - `setLoading(isLoading)`: Sets loading state

### 3. Controllers (`js/controllers/`)

**Purpose**: Coordinate between models, views, and services. Handle user interactions.

#### `CandidateController.js`
- Coordinates candidate form submission
- Validates candidate data using the model
- Uses ExamService to check eligibility
- Updates views based on results
- Methods:
  - `init()`: Sets up event listeners
  - `handleSubmit(e)`: Handles form submission

#### `MarksheetController.js`
- Coordinates marksheet scanning
- Uses ApiService to communicate with backend
- Updates MarksheetScannerView with results
- Methods:
  - `init()`: Sets up event listeners
  - `handleScan()`: Handles scan button click

### 4. Services (`js/services/`)

**Purpose**: Handle business logic and external communication.

#### `ExamService.js`
- Manages exam data and eligibility checking
- Methods:
  - `checkEligibility(candidate)`: Returns eligible exams
  - `getAllExams()`: Returns all exams
  - `getExamById(examId)`: Gets specific exam

#### `ApiService.js`
- Handles all API communication with backend
- Methods:
  - `parseMarksheet(file, method, dpi)`: Calls marksheet parsing API
  - `parsePdf(file, method, dpi)`: Calls PDF parsing API

### 5. Utilities (`js/utils/`)

**Purpose**: Reusable utility functions.

#### `security.js`
- XSS protection utilities
- Functions:
  - `escapeHtml(text)`: Escapes HTML special characters
  - `setTextContent(element, text)`: Safely sets text content

### 6. Data (`js/data/`)

**Purpose**: Static data files.

#### `exams.js`
- Mock exam database
- Exports `MOCK_EXAM_DB` array

## Data Flow

### Candidate Eligibility Check Flow:
1. User fills form → `CandidateFormView` collects data
2. Form submission → `CandidateController.handleSubmit()`
3. Validation → `Candidate` model validates data
4. Eligibility check → `ExamService.checkEligibility()`
5. Results display → `ResultsView.displayExams()`

### Marksheet Scanning Flow:
1. User selects file → `MarksheetScannerView` collects data
2. Scan button click → `MarksheetController.handleScan()`
3. API call → `ApiService.parseMarksheet()`
4. Results display → `MarksheetScannerView.displayResults()`

## Benefits of This Architecture

1. **Separation of Concerns**: Each component has a single responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Each module can be tested independently
4. **Reusability**: Models, views, and services can be reused
5. **Scalability**: Easy to add new features without affecting existing code
6. **Code Organization**: Clear structure makes the codebase easier to understand

## ES6 Modules

The application uses ES6 modules (`import`/`export`) for:
- Better code organization
- Dependency management
- Tree-shaking support
- Modern JavaScript standards

## Security

- All user input is escaped using `escapeHtml()` utility
- Text content is set using `setTextContent()` to prevent XSS
- Input validation at both view and model levels

## Future Enhancements

1. **State Management**: Consider adding a state management solution for complex state
2. **Routing**: Add client-side routing if needed
3. **Build Tools**: Use webpack/vite for bundling and optimization
4. **Testing**: Add unit tests for models, views, and controllers
5. **TypeScript**: Consider migrating to TypeScript for type safety

