import { useState } from 'react'
import { BookOpen, Code, Database, Lock, Film, Zap, Package } from 'lucide-react'

export default function Documentation() {
  const [selectedModule, setSelectedModule] = useState('overview')

  const modules = [
    {
      id: 'overview',
      name: 'Overview',
      icon: <BookOpen className="h-5 w-5" />,
      description: 'Project structure and architecture'
    },
    {
      id: 'ml',
      name: 'ML Module',
      icon: <Zap className="h-5 w-5" />,
      description: 'Machine learning recommendation engine'
    },
    {
      id: 'auth',
      name: 'Authentication',
      icon: <Lock className="h-5 w-5" />,
      description: 'OAuth2 + JWT authentication system'
    },
    {
      id: 'api',
      name: 'API Routes',
      icon: <Code className="h-5 w-5" />,
      description: 'REST API endpoints'
    },
    {
      id: 'database',
      name: 'Database',
      icon: <Database className="h-5 w-5" />,
      description: 'SQLAlchemy models and schema'
    },
    {
      id: 'frontend',
      name: 'Frontend',
      icon: <Film className="h-5 w-5" />,
      description: 'React components and context'
    }
  ]

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
          📚 API Documentation
        </h1>
        <p className="text-gray-400 text-lg">
          Complete technical documentation for the Movie Recommender System
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="md:col-span-1">
          <div className="glass-card p-4 sticky top-24">
            <h3 className="text-lg font-semibold mb-4 text-white">Modules</h3>
            <div className="space-y-2">
              {modules.map((module) => (
                <button
                  key={module.id}
                  onClick={() => setSelectedModule(module.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-300 flex items-center space-x-3 ${
                    selectedModule === module.id
                      ? 'bg-gradient-to-r from-red-600 to-pink-600 text-white shadow-lg'
                      : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {module.icon}
                  <span className="font-medium">{module.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="md:col-span-3">
          <div className="glass-card p-8">
            {selectedModule === 'overview' && <OverviewDocs />}
            {selectedModule === 'ml' && <MLDocs />}
            {selectedModule === 'auth' && <AuthDocs />}
            {selectedModule === 'api' && <APIDocs />}
            {selectedModule === 'database' && <DatabaseDocs />}
            {selectedModule === 'frontend' && <FrontendDocs />}
          </div>
        </div>
      </div>
    </div>
  )
}

// Documentation Components
function OverviewDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Project Overview</h2>
      
      <Section title="Architecture">
        <p className="text-gray-300 mb-4">
          Full-stack ML application with separated backend and frontend:
        </p>
        <CodeBlock language="text">{`Movie-Recommender/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── config.py    # Settings and configuration
│   │   ├── database.py  # Database setup
│   │   ├── models_db.py # SQLAlchemy models
│   │   ├── api/         # API routes
│   │   ├── auth/        # Authentication logic
│   │   └── ml/          # ML recommendation engine
│   └── requirements.txt
│
└── frontend/            # React Frontend
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── pages/       # Page components
    │   ├── context/     # React Context (state)
    │   └── services/    # API client
    └── package.json`}</CodeBlock>
      </Section>

      <Section title="Tech Stack">
        <ul className="space-y-2 text-gray-300">
          <li>• <strong>Backend:</strong> FastAPI, Python 3.8+</li>
          <li>• <strong>Frontend:</strong> React 18, Vite, TailwindCSS</li>
          <li>• <strong>ML:</strong> scikit-learn, pandas, numpy</li>
          <li>• <strong>Auth:</strong> OAuth2 + JWT</li>
          <li>• <strong>Database:</strong> SQLAlchemy (SQLite/PostgreSQL)</li>
        </ul>
      </Section>
    </div>
  )
}

function MLDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">ML Module</h2>
      
      <Section title="app.ml.recommender.MovieRecommender">
        <p className="text-gray-300 mb-4">
          Main recommendation engine using content-based filtering.
        </p>
        
        <Method
          name="get_content_based_recommendations"
          params={[
            { name: 'title', type: 'str', desc: 'Movie title to base recommendations on' },
            { name: 'n_recommendations', type: 'int', desc: 'Number of recommendations (default: 10)' }
          ]}
          returns="Tuple[List[dict], List[float]]"
          description="Returns similar movies using TF-IDF and cosine similarity"
        />

        <CodeBlock language="python">{`# Example Usage
recommender = MovieRecommender('movie_data.pkl')

# Get recommendations for a movie
recommendations, scores = recommender.get_content_based_recommendations(
    title="The Dark Knight",
    n_recommendations=10
)

# Output: List of 10 similar movies with similarity scores`}</CodeBlock>

        <Method
          name="get_mood_based_recommendations"
          params={[
            { name: 'mood', type: 'str', desc: "User's mood (happy, sad, excited, scared, thoughtful)" },
            { name: 'n_recommendations', type: 'int', desc: 'Number of recommendations' }
          ]}
          returns="List[dict]"
          description="Returns movies matching the user's current mood"
        />

        <CodeBlock language="python">{`# Mood-based recommendations
mood_movies = recommender.get_mood_based_recommendations(
    mood="excited",
    n_recommendations=5
)

# Returns action, adventure, thriller movies`}</CodeBlock>
      </Section>

      <Section title="app.ml.preprocessing.MovieDataPreprocessor">
        <p className="text-gray-300 mb-4">
          Handles data loading, feature extraction, and similarity computation.
        </p>
        
        <Method
          name="run_full_pipeline"
          params={[
            { name: 'output_path', type: 'str', desc: 'Path to save processed data' }
          ]}
          returns="Tuple[DataFrame, ndarray]"
          description="Runs complete preprocessing pipeline"
        />

        <CodeBlock language="python">{`# Preprocessing pipeline
preprocessor = MovieDataPreprocessor(
    credits_path="data/tmdb_5000_credits.csv",
    movies_path="data/tmdb_5000_movies.csv"
)

movies_df, cosine_sim = preprocessor.run_full_pipeline(
    output_path="movie_data.pkl"
)`}</CodeBlock>
      </Section>
    </div>
  )
}

function AuthDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Authentication Module</h2>
      
      <Section title="app.auth.security">
        <p className="text-gray-300 mb-4">
          OAuth2 + JWT authentication utilities.
        </p>

        <Method
          name="get_password_hash"
          params={[
            { name: 'password', type: 'str', desc: 'Plain text password' }
          ]}
          returns="str"
          description="Hashes password using pbkdf2_sha256"
        />

        <Method
          name="verify_password"
          params={[
            { name: 'plain_password', type: 'str', desc: 'Password to verify' },
            { name: 'hashed_password', type: 'str', desc: 'Hashed password from database' }
          ]}
          returns="bool"
          description="Verifies password against hash"
        />

        <Method
          name="create_access_token"
          params={[
            { name: 'data', type: 'dict', desc: 'Token payload (e.g., {"sub": user_id})' },
            { name: 'expires_delta', type: 'timedelta', desc: 'Optional expiration time' }
          ]}
          returns="str"
          description="Creates JWT access token (30 min expiry)"
        />

        <CodeBlock language="python">{`from app.auth.security import create_access_token
from datetime import timedelta

# Create access token
token = create_access_token(
    data={"sub": user_id},
    expires_delta=timedelta(minutes=30)
)

# Token structure: JWT with {sub, exp, type: "access"}`}</CodeBlock>

        <Method
          name="get_current_user"
          params={[
            { name: 'token', type: 'str', desc: 'JWT token from Authorization header' },
            { name: 'db', type: 'Session', desc: 'Database session' }
          ]}
          returns="User"
          description="Decodes token and returns authenticated user"
        />
      </Section>
    </div>
  )
}

function APIDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">API Routes</h2>
      
      <Section title="Authentication Endpoints">
        <APIEndpoint
          method="POST"
          path="/api/auth/signup"
          description="Create new user account"
          request={{
            email: "user@example.com",
            username: "moviefan",
            password: "securepass123",
            full_name: "John Doe"
          }}
          response={{
            id: 1,
            email: "user@example.com",
            username: "moviefan",
            is_active: true,
            created_at: "2024-01-01T12:00:00"
          }}
        />

        <APIEndpoint
          method="POST"
          path="/api/auth/login"
          description="Login and receive JWT tokens"
          request={{
            email: "user@example.com",
            password: "securepass123"
          }}
          response={{
            access_token: "eyJhbGc...",
            refresh_token: "eyJhbGc...",
            token_type: "bearer"
          }}
        />

        <APIEndpoint
          method="GET"
          path="/api/auth/me"
          description="Get current user info (requires auth)"
          auth={true}
          response={{
            id: 1,
            email: "user@example.com",
            username: "moviefan"
          }}
        />
      </Section>

      <Section title="Recommendation Endpoints">
        <APIEndpoint
          method="POST"
          path="/api/recommendations/content-based"
          description="Get content-based recommendations"
          request={{
            title: "The Dark Knight",
            n_recommendations: 10
          }}
          response={{
            recommendations: [
              {
                movie_id: 155,
                title: "The Dark Knight Rises",
                genres: ["Action", "Crime", "Drama"],
                vote_average: 7.6
              }
            ],
            similarity_scores: [0.85, 0.82, Ellipsis]
          }}
        />

        <APIEndpoint
          method="POST"
          path="/api/recommendations/mood-based"
          description="Get mood-based recommendations"
          request={{
            mood: "happy",
            n_recommendations: 5
          }}
          response={{
            mood: "happy",
            recommendations: [Ellipsis],
            count: 5
          }}
        />
      </Section>

      <Section title="User Endpoints">
        <APIEndpoint
          method="GET"
          path="/api/user/watchlist"
          description="Get user's watchlist (requires auth)"
          auth={true}
          response={[
            {
              id: 1,
              movie_id: 550,
              movie_title: "Fight Club",
              genres: "Drama,Thriller",
              vote_average: 8.4,
              added_at: "2024-01-01T12:00:00"
            }
          ]}
        />

        <APIEndpoint
          method="POST"
          path="/api/user/watchlist"
          description="Add movie to watchlist (requires auth)"
          auth={true}
          request={{
            movie_id: 550,
            movie_title: "Fight Club",
            genres: ["Drama", "Thriller"],
            vote_average: 8.4,
            runtime: 139
          }}
          response={{
            id: 1,
            movie_id: 550,
            movie_title: "Fight Club",
            added_at: "2024-01-01T12:00:00"
          }}
        />
      </Section>
    </div>
  )
}

function DatabaseDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Database Models</h2>
      
      <Section title="User Model">
        <p className="text-gray-300 mb-4">
          Stores user account information
        </p>
        <CodeBlock language="python">{`class User(Base):
    __tablename__ = "users"
    
    id: int                    # Primary key
    email: str                 # Unique, indexed
    username: str              # Unique, indexed
    hashed_password: str       # pbkdf2_sha256 hash
    full_name: Optional[str]   # Optional
    
    # OAuth fields
    oauth_provider: Optional[str]  # 'google', 'github'
    oauth_id: Optional[str]        # Provider's user ID
    
    is_active: bool           # Account status
    is_verified: bool         # Email verified
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    watchlist_items: List[WatchlistItem]
    ratings: List[MovieRating]`}</CodeBlock>
      </Section>

      <Section title="WatchlistItem Model">
        <CodeBlock language="python">{`class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id: int
    user_id: int              # Foreign key to users.id
    movie_id: int             # TMDB movie ID
    movie_title: str
    
    # Cached movie data
    genres: str               # Comma-separated
    vote_average: Optional[float]
    runtime: Optional[int]
    
    added_at: datetime`}</CodeBlock>
      </Section>

      <Section title="MovieRating Model">
        <CodeBlock language="python">{`class MovieRating(Base):
    __tablename__ = "movie_ratings"
    
    id: int
    user_id: int              # Foreign key to users.id
    movie_id: int
    movie_title: str
    
    rating: float             # User's rating (1-10)
    review: Optional[str]     # Text review
    
    created_at: datetime
    updated_at: datetime`}</CodeBlock>
      </Section>
    </div>
  )
}

function FrontendDocs() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Frontend Architecture</h2>
      
      <Section title="React Context">
        <p className="text-gray-300 mb-4">
          Global state management using Context API
        </p>

        <h4 className="text-xl font-semibold text-white mb-2">AuthContext</h4>
        <CodeBlock language="javascript">{`import { useAuth } from '../context/AuthContext'

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return <div>Please login</div>
  }
  
  return <div>Welcome, {user.username}!</div>
}`}</CodeBlock>

        <h4 className="text-xl font-semibold text-white mb-2 mt-6">WatchlistContext</h4>
        <CodeBlock language="javascript">{`import { useWatchlist } from '../context/WatchlistContext'

function MovieCard({ movie }) {
  const { addToWatchlist, isInWatchlist } = useWatchlist()
  
  const inWatchlist = isInWatchlist(movie.movie_id)
  
  return (
    <button onClick={() => addToWatchlist(movie)}>
      {inWatchlist ? '✓ In Watchlist' : '+ Add'}
    </button>
  )
}`}</CodeBlock>
      </Section>

      <Section title="API Service">
        <CodeBlock language="javascript">{`import { movieAPI } from '../services/api'

// Search movies
const results = await movieAPI.searchMovies('avatar', 10)

// Get recommendations
const data = await movieAPI.getContentRecommendations(
  'The Dark Knight',
  10
)

// Get popular movies
const popular = await movieAPI.getPopularMovies(20)`}</CodeBlock>
      </Section>
    </div>
  )
}

// Helper Components
function Section({ title, children }) {
  return (
    <div className="border-l-4 border-red-500 pl-6 py-2">
      <h3 className="text-2xl font-semibold text-white mb-4">{title}</h3>
      {children}
    </div>
  )
}

function Method({ name, params, returns, description }) {
  return (
    <div className="bg-gray-900/50 rounded-lg p-4 mb-4 border border-gray-700">
      <div className="flex items-start justify-between mb-2">
        <code className="text-lg text-blue-400 font-mono">{name}()</code>
        <span className="text-sm text-gray-400 bg-gray-800 px-2 py-1 rounded">
          → {returns}
        </span>
      </div>
      <p className="text-gray-300 mb-3">{description}</p>
      <div className="space-y-2">
        <p className="text-sm font-semibold text-gray-400">Parameters:</p>
        {params.map((param, idx) => (
          <div key={idx} className="ml-4 text-sm">
            <code className="text-green-400">{param.name}</code>
            <span className="text-purple-400"> ({param.type})</span>
            <span className="text-gray-400"> - {param.desc}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function CodeBlock({ language, children }) {
  return (
    <div className="relative group">
      <div className="absolute top-2 right-2 text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
        {language}
      </div>
      <pre className="bg-gray-950 border border-gray-800 rounded-lg p-4 overflow-x-auto">
        <code className="text-sm text-gray-300 font-mono">{children}</code>
      </pre>
    </div>
  )
}

function APIEndpoint({ method, path, description, request, response, auth }) {
  const methodColors = {
    GET: 'bg-blue-600',
    POST: 'bg-green-600',
    PUT: 'bg-yellow-600',
    DELETE: 'bg-red-600'
  }

  return (
    <div className="bg-gray-900/50 rounded-lg p-6 mb-6 border border-gray-700">
      <div className="flex items-center space-x-3 mb-3">
        <span className={`${methodColors[method]} px-3 py-1 rounded text-sm font-bold`}>
          {method}
        </span>
        <code className="text-lg text-blue-400 font-mono">{path}</code>
        {auth && <span className="text-xs bg-yellow-600 px-2 py-1 rounded">🔒 Auth Required</span>}
      </div>
      <p className="text-gray-300 mb-4">{description}</p>
      
      {request && (
        <>
          <p className="text-sm font-semibold text-gray-400 mb-2">Request Body:</p>
          <pre className="bg-gray-950 border border-gray-800 rounded p-3 mb-4 overflow-x-auto">
            <code className="text-sm text-green-400">{JSON.stringify(request, null, 2)}</code>
          </pre>
        </>
      )}
      
      {response && (
        <>
          <p className="text-sm font-semibold text-gray-400 mb-2">Response:</p>
          <pre className="bg-gray-950 border border-gray-800 rounded p-3 overflow-x-auto">
            <code className="text-sm text-blue-400">{JSON.stringify(response, null, 2)}</code>
          </pre>
        </>
      )}
    </div>
  )
}

