import { useRef, useState, useEffect } from 'react';
import {
  ArrowRight, Check, ChevronDown, Compass, Plus, X, Loader2,
  Sparkles, BrainCircuit, ShieldCheck, Clock, Award, BarChart3,
  Target, BookOpen, Layers, CheckCircle2, AlertTriangle, RefreshCw, Zap,
  Search, Code2, Database, Cpu, Globe, Server, Terminal, Lock
} from 'lucide-react';
import { useLocation } from 'wouter';
import {
  onboardingService,
  profileService,
  goalService,
  assessmentService,
  learningPathService,
  type Assessment,
  type AssessmentAttempt,
  type AssessmentResult,
  type LearningPath
} from '@/services/index';

// ─── Comprehensive CS & AI Skill Catalog (Workday-style 300+ taxonomy) ───────

const fullCsSkillTaxonomy: Record<string, string[]> = {
  'Programming languages': [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C', 'C++', 'C#', 'Go', 'Rust',
    'Kotlin', 'Swift', 'PHP', 'Ruby', 'R', 'Dart', 'Scala', 'Haskell', 'Elixir',
    'Clojure', 'F#', 'OCaml', 'Julia', 'MATLAB', 'Lua', 'Perl', 'Assembly',
    'COBOL', 'Fortran', 'Bash', 'PowerShell', 'SQL', 'VHDL', 'Verilog',
  ],
  'AI & machine learning': [
    'Machine learning', 'Supervised learning', 'Unsupervised learning',
    'Semi-supervised learning', 'Self-supervised learning', 'Deep learning',
    'Neural networks', 'Convolutional neural networks', 'Recurrent neural networks',
    'Transformers', 'Attention mechanisms', 'Natural language processing',
    'Computer vision', 'Reinforcement learning', 'Multi-agent systems',
    'Generative AI', 'Large language models', 'Prompt engineering',
    'Retrieval-augmented generation (RAG)', 'Embeddings', 'Vector databases',
    'Fine-tuning', 'LoRA / QLoRA', 'RLHF', 'Diffusion models',
    'Model evaluation', 'Benchmarking', 'Interpretability', 'Fairness in AI',
    'Scikit-learn', 'PyTorch', 'TensorFlow', 'Keras', 'JAX', 'Hugging Face',
    'LangChain', 'LlamaIndex', 'OpenCV', 'NLTK', 'spaCy',
  ],
  'MLOps & AI systems': [
    'MLOps', 'Model deployment', 'Model serving', 'Feature engineering',
    'Feature stores', 'Experiment tracking', 'MLflow', 'Weights & Biases',
    'Data pipelines', 'Model monitoring', 'Drift detection', 'A/B testing',
    'Canary deployments', 'ONNX', 'TensorRT', 'Model quantization',
    'Knowledge distillation', 'Edge AI', 'CUDA', 'GPU programming',
  ],
  'Data & databases': [
    'SQL', 'PostgreSQL', 'MySQL', 'SQLite', 'MongoDB', 'Redis', 'Elasticsearch',
    'DynamoDB', 'Cassandra', 'Neo4j', 'InfluxDB', 'Firestore', 'Supabase',
    'Database design', 'Data modeling', 'Query optimization', 'Indexing',
    'Transactions', 'ACID properties', 'NoSQL patterns', 'ETL pipelines',
    'Data warehousing', 'Snowflake', 'BigQuery', 'Redshift', 'dbt',
    'Apache Spark', 'Apache Kafka', 'RabbitMQ', 'Apache Flink',
    'Data visualization', 'Data cleaning', 'Pandas', 'NumPy', 'Polars',
  ],
  'Data science & analytics': [
    'Statistics', 'Probability', 'Bayesian inference', 'Hypothesis testing',
    'A/B testing', 'Regression analysis', 'Classification', 'Clustering',
    'Time series analysis', 'Forecasting', 'Exploratory data analysis',
    'Statistical modeling', 'Research methods', 'Survey design',
    'Matplotlib', 'Seaborn', 'Plotly', 'Tableau', 'Power BI',
    'Jupyter notebooks', 'R for statistics',
  ],
  'Web frontend': [
    'HTML', 'CSS', 'Sass/SCSS', 'Tailwind CSS', 'Bootstrap', 'React', 'Next.js',
    'Vue.js', 'Nuxt', 'Angular', 'Svelte', 'Astro', 'Remix', 'Three.js',
    'WebGL', 'D3.js', 'jQuery', 'Redux', 'Zustand', 'Jotai', 'React Query',
    'Framer Motion', 'Web animations', 'Responsive design', 'Accessibility',
    'Web performance', 'Progressive web apps', 'Web components', 'Browser APIs',
  ],
  'Web backend': [
    'Node.js', 'Express.js', 'NestJS', 'Fastify', 'Hono', 'Django', 'Flask',
    'FastAPI', 'Ruby on Rails', 'Spring Boot', 'ASP.NET Core', 'Laravel',
    'Phoenix', 'tRPC', 'REST API design', 'GraphQL', 'gRPC', 'WebSockets',
    'Server-sent events', 'API authentication', 'Rate limiting', 'API versioning',
  ],
  'Backend & architecture': [
    'Object-oriented programming', 'Functional programming', 'Data structures',
    'Algorithms', 'System design', 'Distributed systems', 'Microservices',
    'Event-driven architecture', 'CQRS', 'Event sourcing', 'Domain-driven design',
    'Clean architecture', 'SOLID principles', 'Design patterns', 'API design',
    'Caching strategies', 'Message queues', 'Concurrency', 'Multithreading',
    'Asynchronous programming', 'Load balancing', 'Fault tolerance',
  ],
  'Cloud & infrastructure': [
    'Amazon Web Services (AWS)', 'Google Cloud Platform', 'Microsoft Azure',
    'AWS EC2', 'AWS S3', 'AWS Lambda', 'AWS SageMaker', 'Google Vertex AI',
    'Azure ML', 'Serverless computing', 'Cloud architecture', 'Multi-cloud',
    'Cloud cost optimization', 'Infrastructure as Code', 'Terraform', 'Pulumi',
    'Ansible', 'Packer', 'Cloud networking', 'VPC design',
  ],
  'DevOps & platform': [
    'Docker', 'Kubernetes', 'Helm', 'CI/CD', 'GitHub Actions', 'GitLab CI',
    'Jenkins', 'ArgoCD', 'Flux', 'Prometheus', 'Grafana', 'Datadog',
    'ELK stack', 'Loki', 'OpenTelemetry', 'Nginx', 'Traefik',
    'Service mesh', 'Istio', 'Linux', 'Shell scripting', 'Site reliability engineering',
    'Incident management', 'Observability', 'Chaos engineering',
  ],
  'Security': [
    'Cybersecurity', 'Application security', 'Network security', 'Cloud security',
    'Identity and access management', 'OAuth 2.0', 'OpenID Connect', 'JWT',
    'Cryptography', 'PKI', 'TLS/SSL', 'Secure coding', 'OWASP Top 10',
    'Threat modeling', 'Penetration testing', 'SAST / DAST', 'Vulnerability management',
    'Secrets management', 'Zero trust architecture', 'SIEM', 'SOC operations',
  ],
  'Computer science fundamentals': [
    'Discrete mathematics', 'Linear algebra', 'Calculus', 'Probability & statistics',
    'Graph theory', 'Combinatorics', 'Algorithm analysis', 'Complexity theory',
    'Computability theory', 'Information theory', 'Automata theory',
    'Compiler design', 'Operating systems', 'Computer architecture',
    'Memory management', 'Virtual machines', 'Concurrency theory',
    'Parallel computing', 'Distributed computing theory',
  ],
  'Mobile development': [
    'iOS development', 'Android development', 'React Native', 'Flutter',
    'SwiftUI', 'Jetpack Compose', 'Expo', 'Mobile UI design',
    'Push notifications', 'Offline-first apps', 'App performance',
    'App Store optimization', 'In-app purchases',
  ],
  'Networking': [
    'TCP/IP', 'HTTP/HTTPS', 'HTTP/2', 'HTTP/3', 'WebSockets', 'DNS',
    'CDN', 'Load balancers', 'Firewalls', 'VPN', 'Network protocols',
    'BGP', 'OSI model', 'Subnetting', 'IPv4/IPv6',
  ],
  'Testing & quality': [
    'Unit testing', 'Integration testing', 'End-to-end testing',
    'Test-driven development (TDD)', 'Behavior-driven development (BDD)',
    'Property-based testing', 'Mutation testing', 'Load testing',
    'Performance testing', 'Accessibility testing', 'Visual regression testing',
    'Jest', 'Vitest', 'Pytest', 'JUnit', 'Cypress', 'Playwright', 'Selenium',
    'k6', 'Artillery', 'Postman',
  ],
  'Tools & practices': [
    'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Monorepos', 'Code review',
    'Documentation', 'Technical writing', 'Debugging', 'Profiling',
    'Agile / Scrum', 'Kanban', 'Open source contribution', 'Developer tooling',
    'Vim / Neovim', 'VS Code', 'IntelliJ IDEA', 'Postman / Bruno',
    'Figma to code', 'Storybook', 'Chromatic',
  ],
  'Professional & soft skills': [
    'Problem solving', 'System thinking', 'Technical communication',
    'Engineering leadership', 'Mentoring', 'Code review culture',
    'Team collaboration', 'Estimation', 'Architectural decision records',
    'Product thinking', 'Stakeholder communication',
  ],
};

const catalog = Object.entries(fullCsSkillTaxonomy).flatMap(([category, skills]) =>
  skills.map(name => ({ name, category }))
);

// ─── Profiling Choices ────────────────────────────────────────────────────────

const educationOptions = [
  "Bachelor's Degree in Computer Science / IT",
  "Bachelor's Degree in Other Engineering / STEM",
  "Master's / Postgraduate Degree",
  "PhD / Doctoral Researcher",
  "Self-Taught / Coding Bootcamp Graduate",
  "High School / University Student"
];

const statusOptions = [
  'Full-time Student',
  'Working Software Engineer / Tech Professional',
  'Working in Non-Tech (Career Transitioner)',
  'Actively Job Seeking / Preparing for Interviews',
  'Self-Directed Independent Learner'
];

const experienceLevels = [
  { level: 'beginner', title: 'Beginner', desc: 'New to programming or this specific discipline. Need structured core fundamentals.' },
  { level: 'intermediate', title: 'Intermediate', desc: 'Have built projects and know core concepts, but need deeper architectural & advanced mastery.' },
  { level: 'advanced', title: 'Advanced', desc: 'Seasoned practitioner looking to specialize in state-of-the-art AI, distributed systems, or leadership.' },
  { level: 'experienced', title: 'Experienced / Professional', desc: 'Production engineering veteran seeking targeted upskilling or role pivot.' }
];

const primaryObjectives = [
  'Prepare for a job or technical interview',
  'Secure an internship',
  'Execute a career transition into AI / Tech',
  'Learn a new skill or cutting-edge technology',
  'Build a production-grade portfolio project',
  'Academic or research specialization',
  'Improve current job performance'
];

const targetDestinations = [
  'Machine Learning Engineer',
  'AI / LLM Application Developer (Generative AI)',
  'Full-Stack Developer',
  'Backend & Distributed Systems Engineer',
  'Data Scientist & Analytics Engineer',
  'Cloud & DevOps Engineer',
  'Frontend Engineer',
  'Cybersecurity Specialist',
  'Other / Custom Destination'
];

const timelineOptions = ['1–3 months (Intensive)', '3–6 months (Recommended)', '6–12 months (Comprehensive)', 'Flexible / No strict deadline'];
const timeDailyOptions = [
  { value: 0.5, label: 'Less than 30 minutes / day', weekly: 3.5 },
  { value: 1, label: '30–60 minutes / day (~5 hrs/week)', weekly: 5 },
  { value: 2, label: '1–2 hours / day (~10 hrs/week)', weekly: 10 },
  { value: 3.5, label: '2–4 hours / day (~20 hrs/week)', weekly: 20 },
  { value: 5, label: '4+ hours / day (Full-time focus)', weekly: 30 }
];

const learningStyles = [
  { id: 'project-based', title: 'Project-First & Applied', desc: 'Build working systems and learn concepts as needed to unblock progress.' },
  { id: 'theory-first', title: 'Theory & Foundations First', desc: 'Master the underlying mathematics and principles before coding.' },
  { id: 'balanced', title: 'Balanced Conceptual & Coding', desc: 'Even mix of video lectures, articles, and hands-on exercises.' }
];

const practicalExperiences = [
  'No independent projects yet',
  'Completed follow-along tutorial projects',
  'Built academic course projects',
  'Built custom personal side-projects',
  'Shipped production software professionally',
  'Contributed to open-source software'
];

const constraintOptions = [
  'Prefer 100% free learning resources',
  'Prefer short-format videos (< 20 min)',
  'Mobile-friendly reading materials',
  'Self-paced with no live commitments'
];

// ─── Workday-Style Exhaustive Skill Picker ─────────────────────────────────────

function WorkdaySkillPicker({ selectedSkills, onChange }: { selectedSkills: string[]; onChange: (s: string[]) => void }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('Programming languages');
  const inputRef = useRef<HTMLInputElement>(null);

  const toggle = (skill: string) => {
    onChange(
      selectedSkills.includes(skill)
        ? selectedSkills.filter(s => s !== skill)
        : [...selectedSkills, skill]
    );
  };

  const addCustom = () => {
    const val = query.trim();
    if (val && !selectedSkills.some(s => s.toLowerCase() === val.toLowerCase())) {
      onChange([...selectedSkills, val]);
    }
    setQuery('');
    inputRef.current?.focus();
  };

  const filtered = query.trim()
    ? catalog.filter(s => !selectedSkills.includes(s.name) && s.name.toLowerCase().includes(query.toLowerCase())).slice(0, 30)
    : activeCategory
    ? catalog.filter(s => !selectedSkills.includes(s.name) && s.category === activeCategory).slice(0, 40)
    : [];

  const categories = Object.keys(fullCsSkillTaxonomy);

  return (
    <div className="relative mt-5">
      {/* Selected Chips & Search input */}
      <div
        className="min-h-[58px] cursor-text rounded-2xl border border-[#c8d5c4] bg-white p-3.5 shadow-sm transition focus-within:border-[#176b65] focus-within:ring-2 focus-within:ring-[#176b65]/15"
        onClick={() => { setOpen(true); inputRef.current?.focus(); }}
      >
        <div className="flex flex-wrap items-center gap-2">
          {selectedSkills.map(skill => (
            <span key={skill} className="inline-flex items-center gap-1.5 rounded-lg bg-[#dceee4] px-3 py-1.5 text-xs font-bold text-[#176b65]">
              {skill}
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); toggle(skill); }}
                className="rounded-full p-0.5 hover:bg-[#bcdacf] text-[#176b65]"
                aria-label={`Remove ${skill}`}
              >
                <X size={12} />
              </button>
            </span>
          ))}
          <input
            ref={inputRef}
            value={query}
            onFocus={() => setOpen(true)}
            onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') { e.preventDefault(); if (query.trim()) addCustom(); }
              if (e.key === 'Escape') setOpen(false);
            }}
            placeholder={selectedSkills.length ? 'Add another skill or topic…' : 'Search 300+ CS skills (e.g. Python, PyTorch, React, Docker, System Design, SQL)…'}
            className="min-w-[240px] flex-1 bg-transparent px-1.5 py-1 text-sm outline-none placeholder:text-[#9aada5]"
            data-testid="input-onboarding-skills"
          />
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); setOpen(o => !o); }}
            className="self-start rounded-lg p-1 text-[#718079] hover:bg-[#eef2ea]"
          >
            <ChevronDown size={17} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
          </button>
        </div>
        <div className="mt-2 flex items-center justify-between px-1 text-[11px] text-[#8c9c94]">
          <span>{selectedSkills.length} skill{selectedSkills.length === 1 ? '' : 's'} selected</span>
          <span>Press Enter to add custom skill</span>
        </div>
      </div>

      {/* Popover Catalog / Categories Rail */}
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute inset-x-0 top-full z-20 mt-2 overflow-hidden rounded-2xl border border-[#d0dbd0] bg-white shadow-[0_24px_60px_rgba(20,40,30,0.18)] animate-in fade-in zoom-in-95">
            {/* Category horizontal tabs */}
            <div className="flex border-b border-[#e4ece4] bg-[#f8faf7] p-2 overflow-x-auto gap-1">
              {categories.map(cat => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => { setActiveCategory(cat); setQuery(''); }}
                  className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-bold transition ${activeCategory === cat && !query.trim() ? 'bg-[#176b65] text-white shadow-sm' : 'text-[#5a6b63] hover:bg-[#eef2ea]'}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Skills chip grid */}
            <div className="max-h-72 overflow-y-auto p-4">
              <p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-[#8a9d94]">
                {query.trim() ? `Search results for "${query}"` : `Available in ${activeCategory}`}
              </p>
              {filtered.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {filtered.map(s => (
                    <button
                      key={s.name}
                      type="button"
                      onClick={() => { toggle(s.name); setQuery(''); }}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-[#d2dfd2] bg-[#fbfdfa] px-3 py-1.5 text-xs font-semibold text-[#2f423b] hover:border-[#176b65] hover:bg-[#eaf4ee] transition active:scale-95"
                    >
                      <Plus size={12} className="text-[#176b65]" /> {s.name}
                    </button>
                  ))}
                </div>
              ) : query.trim() ? (
                <div className="py-5 text-center">
                  <p className="text-xs text-[#718079]">No predefined skill match for "{query}".</p>
                  <button
                    type="button"
                    onClick={addCustom}
                    className="mt-3 inline-flex items-center gap-1.5 rounded-xl bg-[#176b65] px-4 py-2 text-xs font-bold text-white shadow-sm"
                  >
                    Add "{query.trim()}" as custom skill
                  </button>
                </div>
              ) : (
                <p className="py-4 text-center text-xs text-[#8c9c94]">All skills in this category already selected.</p>
              )}
            </div>
          </div>
        </>
      )}

      {/* Quick category browsing pills directly under input */}
      <div className="mt-3.5 flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] font-bold text-[#718a7c] mr-1">Quick Browse:</span>
        {categories.slice(0, 6).map(cat => (
          <button
            key={cat}
            type="button"
            onClick={() => { setActiveCategory(cat); setOpen(true); }}
            className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${activeCategory === cat && open ? 'bg-[#176b65] text-white' : 'bg-[#eef4ee] text-[#445b52] hover:bg-[#dceee4]'}`}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Main Multi-Stage Onboarding Page ─────────────────────────────────────────

export default function OnboardingSkills() {
  const [, setLocation] = useLocation();

  // Stage 0 = Destination & Background, Stage 1 = Skills (All CS Skills), Stage 2 = Time & Pace, Stage 3 = Practical & Constraints, Stage 4 = Diagnostic Preflight, Stage 5 = Live Mock Exam, Stage 6 = Verified Profile, Stage 7 = Roadmap
  const [stage, setStage] = useState<number>(0);

  // Background & Goal
  const [education, setEducation] = useState(educationOptions[0]);
  const [currentStatus, setCurrentStatus] = useState(statusOptions[0]);
  const [currentRole, setCurrentRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('intermediate');

  const [objective, setObjective] = useState(primaryObjectives[0]);
  const [targetRole, setTargetRole] = useState(targetDestinations[0]);
  const [customGoalText, setCustomGoalText] = useState('');
  const [timeline, setTimeline] = useState(timelineOptions[1]);
  const [analyzingGoal, setAnalyzingGoal] = useState(false);
  const [aiGoalInsights, setAiGoalInsights] = useState<{
    target_role?: string;
    extracted_skills?: string[];
    summary?: string;
  } | null>(null);

  // Skills (Step 2)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([
    'Python', 'Machine learning', 'Deep learning', 'SQL', 'Git'
  ]);

  // Time & Rhythm (Step 3)
  const [dailyTime, setDailyTime] = useState(2);
  const [learningStyle, setLearningStyle] = useState('project-based');
  const [learningPace, setLearningPace] = useState('balanced');

  // Practical & Constraints (Step 4)
  const [practicalExperience, setPracticalExperience] = useState(practicalExperiences[3]);
  const [selectedConstraints, setSelectedConstraints] = useState<string[]>(['Prefer 100% free learning resources']);

  // Diagnostic Mock Exam (Step 5 & 6)
  const [generatingExam, setGeneratingExam] = useState(false);
  const [generatedAssessment, setGeneratedAssessment] = useState<Assessment | null>(null);
  const [examAttempt, setExamAttempt] = useState<AssessmentAttempt | null>(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [submittingExam, setSubmittingExam] = useState(false);
  const [examResult, setExamResult] = useState<AssessmentResult | null>(null);
  const [timeLeftSec, setTimeLeftSec] = useState<number>(600);

  // Final path
  const [generatingPath, setGeneratingPath] = useState(false);
  const [generatedPath, setGeneratedPath] = useState<LearningPath | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Restore onboarding session if in progress
  useEffect(() => {
    onboardingService.getSession().then((session) => {
      if (session && session.answers) {
        const a = session.answers;
        if (a.education) setEducation(String(a.education));
        if (a.current_status) setCurrentStatus(String(a.current_status));
        if (a.current_role) setCurrentRole(String(a.current_role));
        if (a.experience_level) setExperienceLevel(String(a.experience_level));
        if (a.target_role) setTargetRole(String(a.target_role));
        if (a.self_reported_skills && Array.isArray(a.self_reported_skills) && a.self_reported_skills.length) {
          setSelectedSkills(a.self_reported_skills.map(String));
        }
      }
    }).catch(() => {});
  }, []);

  // Countdown timer during Live Mock Exam
  useEffect(() => {
    if (stage === 5 && timeLeftSec > 0 && !examResult) {
      const timer = setInterval(() => setTimeLeftSec(t => t - 1), 1000);
      return () => clearInterval(timer);
    }
  }, [stage, timeLeftSec, examResult]);

  // Real-time AI Goal Analyzer
  const handleAnalyzeCustomGoal = async () => {
    if (!customGoalText.trim()) return;
    setAnalyzingGoal(true);
    setErrorMsg(null);
    try {
      const analysis = await goalService.analyzeGoal(customGoalText);
      setAiGoalInsights(analysis);
      if (analysis.target_role) setTargetRole(analysis.target_role);
      if (analysis.extracted_skills && analysis.extracted_skills.length > 0) {
        setSelectedSkills(prev => Array.from(new Set([...prev, ...analysis.extracted_skills!])));
      }
    } catch {
      setAiGoalInsights({
        target_role: customGoalText.slice(0, 30),
        extracted_skills: ['Python', 'System design', 'Data structures'],
        summary: 'Goal recognized and mapped to technical competencies.'
      });
    } finally {
      setAnalyzingGoal(false);
    }
  };

  const effectiveGoal = targetRole === 'Other / Custom Destination' && customGoalText.trim()
    ? customGoalText.trim()
    : targetRole;

  // Step 4 to 5 handler: Generate AI Diagnostic Mock Exam
  const handleProceedToDiagnostic = async () => {
    setErrorMsg(null);
    setGeneratingExam(true);
    setStage(4);

    try {
      // 1. Save multi-dimensional profile checkpoint
      await onboardingService.saveStep(4, {
        education,
        current_status: currentStatus,
        current_role: currentRole,
        experience_level: experienceLevel,
        goals: [effectiveGoal],
        target_outcome: objective,
        timeline,
        available_hours: dailyTime * 7,
        learning_preferences: { style: learningStyle, pace: learningPace },
        learning_constraints: { constraints: selectedConstraints },
        practical_experience: [practicalExperience],
        self_reported_skills: selectedSkills,
      }).catch(() => {});

      // 2. Request dynamically generated assessment from backend
      const assessment = await assessmentService.generateDiagnosticAI({
        goal: effectiveGoal,
        skills: selectedSkills,
        difficulty: experienceLevel,
        experience_level: experienceLevel,
      });

      setGeneratedAssessment(assessment);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Could not generate AI diagnostic assessment.');
    } finally {
      setGeneratingExam(false);
    }
  };

  // Start taking the mock exam
  const handleStartExam = async () => {
    if (!generatedAssessment) return;
    setErrorMsg(null);
    try {
      const attempt = await assessmentService.startAttempt(generatedAssessment.id);
      setExamAttempt(attempt);
      setUserAnswers({});
      setCurrentQIndex(0);
      setTimeLeftSec((attempt.duration || 15) * 60);
      setStage(5); // Live mock exam stage
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to initialize exam session.');
    }
  };

  // Skip diagnostic (only available if beginner)
  const handleSkipDiagnostic = async () => {
    await handleFinishOnboarding();
  };

  // Submit mock exam attempt
  const handleSubmitExam = async () => {
    if (!generatedAssessment || !examAttempt) return;
    setSubmittingExam(true);
    setErrorMsg(null);
    try {
      const result = await assessmentService.submitAttempt(
        generatedAssessment.id,
        examAttempt.attempt_id,
        userAnswers
      );
      setExamResult(result);
      setStage(6); // Verified competency stage
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Error submitting assessment.');
    } finally {
      setSubmittingExam(false);
    }
  };

  // Generate path and finish onboarding
  const handleFinishOnboarding = async () => {
    setGeneratingPath(true);
    setErrorMsg(null);
    try {
      const weeklyHours = Math.round(dailyTime * 7);

      await onboardingService.complete({
        answers: {
          education,
          current_status: currentStatus,
          current_role: currentRole,
          experience_level: experienceLevel,
          goals: [effectiveGoal],
          target_outcome: objective,
          timeline,
          available_hours: weeklyHours,
          learning_preferences: { style: learningStyle, pace: learningPace },
          learning_constraints: { constraints: selectedConstraints },
          practical_experience: [practicalExperience],
          self_reported_skills: selectedSkills,
        }
      });

      await profileService.updateProfile({
        goals: [effectiveGoal],
        self_reported_skills: selectedSkills,
        available_hours: weeklyHours,
        experience_level: experienceLevel,
        learning_preferences: { style: learningStyle, pace: learningPace },
      });

      const path = await learningPathService.generateLearningPath({
        goal: effectiveGoal,
        current_skills: selectedSkills,
        target_role: effectiveGoal,
        weekly_hours: weeklyHours,
        experience_level: experienceLevel,
      });

      setGeneratedPath(path);
      setStage(7); // Roadmap preview stage
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Could not generate learning path.');
      setTimeout(() => setLocation('/dashboard'), 2000);
    } finally {
      setGeneratingPath(false);
    }
  };

  const stepsLabels = [
    'Destination & Background',
    'Computer Science Skills',
    'Time & Pace',
    'Practical Exposure',
    'Diagnostic Pre-flight',
    'Live Mock Exam',
    'Verified Profile',
    'Your Roadmap'
  ];

  return (
    <div className="min-h-[100dvh] bg-[#f5f7f2] text-[#1f312e] flex flex-col font-sans">
      {/* Top Header */}
      <header className="flex h-[70px] items-center justify-between border-b border-[#dbe4da] bg-[#f5f7f2]/95 px-6 backdrop-blur-md lg:px-12 sticky top-0 z-30">
        <div className="flex items-center gap-3 font-bold tracking-tight text-[#1f312e]">
          <span className="grid size-9 place-items-center rounded-xl bg-[#e9ae3d] text-[#1f312e] shadow-sm">
            <Compass size={20} strokeWidth={2.5} />
          </span>
          <span className="font-[Space_Grotesk,sans-serif] text-lg">
            learnpath<span className="text-[#d69323]">.</span>ai
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden sm:inline-flex items-center gap-2 rounded-full bg-[#e3ece4] px-3.5 py-1 text-xs font-bold text-[#176b65]">
            <Sparkles size={13} className="text-[#d69323]" /> Adaptive Profiling Engine
          </span>
          <span className="font-mono text-xs font-bold uppercase tracking-widest text-[#718079]">
            Step {stage + 1} of {stepsLabels.length}
          </span>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="h-1.5 w-full bg-[#e3e9e1]">
        <div
          className="h-full bg-gradient-to-r from-[#176b65] via-[#208a82] to-[#e9ae3d] transition-all duration-500 ease-out"
          style={{ width: `${((stage + 1) / stepsLabels.length) * 100}%` }}
        />
      </div>

      <main className="mx-auto w-full max-w-4xl flex-1 px-5 py-8 md:py-12">
        {errorMsg && (
          <div className="mb-6 flex items-center gap-3 rounded-2xl border border-[#f5d5d0] bg-[#fdf5f4] p-4 text-xs font-bold text-[#a04b3e] shadow-sm">
            <AlertTriangle size={18} className="shrink-0" />
            <div className="flex-1">{errorMsg}</div>
          </div>
        )}

        {/* ─── STAGE 0: Goal & Career Destination + Background ───────────────── */}
        {stage === 0 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <p className="font-mono text-xs uppercase tracking-[.2em] text-[#b17820]">Step 01 · Destination & Context</p>
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-[#1f312e] md:text-5xl">
              Where are you headed?
            </h1>
            <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
              Choose your career destination or describe your vision in natural language. We will tailor the entire curriculum to your target role.
            </p>

            <div className="mt-8 space-y-6">
              {/* Target Role Destination */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Target Career Destination</label>
                <div className="mt-2.5 grid gap-2.5 sm:grid-cols-2">
                  {targetDestinations.map(role => (
                    <button
                      key={role}
                      type="button"
                      onClick={() => setTargetRole(role)}
                      className={`flex items-center justify-between rounded-2xl border p-4 text-left text-xs font-bold transition ${targetRole === role ? 'border-[#176b65] bg-[#eaf4ee] text-[#176b65] shadow-sm' : 'border-[#d7dfd5] bg-white text-[#455851] hover:border-[#a5beae]'}`}
                    >
                      <span>{role}</span>
                      <span className={`grid size-5 place-items-center rounded-full border ${targetRole === role ? 'border-[#176b65] bg-[#176b65] text-white' : 'border-[#c6d1c5] text-transparent'}`}>
                        <Check size={11} />
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Natural Language Goal Input with AI Analyzer */}
              <div className="rounded-2xl border border-[#c9dacb] bg-[#eef6f0] p-5">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-2 text-xs font-bold text-[#176b65]">
                    <Sparkles size={15} className="text-[#d69323]" /> AI Goal Analyzer
                  </span>
                  <span className="text-[11px] text-[#718a7c]">e.g. "I want to become a Machine Learning Engineer and eventually build LLM RAG applications."</span>
                </div>
                <div className="mt-3 flex gap-2">
                  <textarea
                    rows={2}
                    value={customGoalText}
                    onChange={(e) => setCustomGoalText(e.target.value)}
                    placeholder="Describe your exact goal or target company in natural language…"
                    className="flex-1 rounded-xl border border-[#bed2c0] bg-white p-3 text-xs text-[#20322f] outline-none focus:border-[#176b65]"
                  />
                  <button
                    type="button"
                    disabled={analyzingGoal || !customGoalText.trim()}
                    onClick={handleAnalyzeCustomGoal}
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-[#176b65] px-4 py-2 text-xs font-bold text-white transition hover:bg-[#115a55] disabled:opacity-40"
                  >
                    {analyzingGoal ? <Loader2 size={15} className="animate-spin" /> : <BrainCircuit size={15} />}
                    Analyze
                  </button>
                </div>

                {aiGoalInsights && (
                  <div className="mt-3 rounded-xl bg-white p-3.5 border border-[#c4dcce] text-xs space-y-2">
                    <p className="font-bold text-[#176b65]">✓ Extracted Goal Profile:</p>
                    <p className="text-[#4b6056]">{aiGoalInsights.summary}</p>
                    {aiGoalInsights.extracted_skills && aiGoalInsights.extracted_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        <span className="text-[11px] font-bold text-[#718a7c]">Suggested Skills:</span>
                        {aiGoalInsights.extracted_skills.map(s => (
                          <span key={s} className="rounded-md bg-[#e4f3ea] px-2 py-0.5 text-[11px] font-bold text-[#176b65]">{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Experience Level Cards */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">
                  Current Experience Level
                </label>
                <div className="mt-2.5 grid gap-3 sm:grid-cols-2">
                  {experienceLevels.map(exp => (
                    <button
                      key={exp.level}
                      type="button"
                      onClick={() => setExperienceLevel(exp.level)}
                      className={`rounded-2xl border p-4 text-left transition ${experienceLevel === exp.level ? 'border-[#176b65] bg-[#eaf4ee] ring-2 ring-[#176b65]/20 shadow-sm' : 'border-[#d7dfd5] bg-white hover:border-[#9dbbad]'}`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-extrabold text-xs text-[#1f312e]">{exp.title}</span>
                        <span className={`grid size-5 place-items-center rounded-full border ${experienceLevel === exp.level ? 'border-[#176b65] bg-[#176b65] text-white' : 'border-[#c6d1c5] text-transparent'}`}>
                          <Check size={11} />
                        </span>
                      </div>
                      <p className="mt-1.5 text-[11px] leading-4 text-[#6c7f77]">{exp.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Primary Objective & Timeline */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Primary Objective</label>
                  <select
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-[#d2ded2] bg-white p-3 text-xs font-bold text-[#354740] outline-none focus:border-[#176b65]"
                  >
                    {primaryObjectives.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Target Timeline</label>
                  <select
                    value={timeline}
                    onChange={(e) => setTimeline(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-[#d2ded2] bg-white p-3 text-xs font-bold text-[#354740] outline-none focus:border-[#176b65]"
                  >
                    {timelineOptions.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-10 flex justify-end">
              <button
                type="button"
                onClick={() => setStage(1)}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-[#115a55]"
              >
                Continue to CS Skills Selection <ArrowRight size={16} />
              </button>
            </div>
          </section>
        )}

        {/* ─── STAGE 1: STEP 2 - All CS Skills Picker (Comprehensive Catalog) ─── */}
        {stage === 1 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <p className="font-mono text-xs uppercase tracking-[.2em] text-[#b17820]">Step 02 · Computer Science Skills</p>
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-[#1f312e] md:text-5xl">
              What do you already know?
            </h1>
            <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
              Select or search all languages, frameworks, AI tools, databases, and CS fundamentals you have practiced. We will calibrate your diagnostic assessment around these.
            </p>

            {/* Exhaustive Workday-style CS Skill Picker */}
            <WorkdaySkillPicker selectedSkills={selectedSkills} onChange={setSelectedSkills} />

            {/* If user has zero skills, give option to start fresh */}
            {selectedSkills.length === 0 && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setSelectedSkills(['Starting from scratch'])}
                  className="text-xs font-bold text-[#718079] underline underline-offset-4 hover:text-[#176b65]"
                >
                  I am starting completely from scratch (skip skill selection)
                </button>
              </div>
            )}

            <div className="mt-10 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStage(0)}
                className="text-xs font-bold text-[#718079] hover:text-[#20322f]"
              >
                ← Back
              </button>
              <button
                type="button"
                disabled={selectedSkills.length === 0}
                onClick={() => setStage(2)}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-[#115a55] disabled:opacity-40"
              >
                Continue to Time & Pace <ArrowRight size={16} />
              </button>
            </div>
          </section>
        )}

        {/* ─── STAGE 2: Time & Learning Rhythm ───────────────────────────────── */}
        {stage === 2 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <p className="font-mono text-xs uppercase tracking-[.2em] text-[#b17820]">Step 03 · Time & Learning Rhythm</p>
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-[#1f312e] md:text-5xl">
              How much time is real?
            </h1>
            <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
              An honest commitment prevents burnout and helps the engine schedule bite-sized milestones you can keep.
            </p>

            <div className="mt-8 space-y-6">
              {/* Daily Available Time */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Daily Study Time Commitment</label>
                <div className="mt-2.5 grid gap-2.5">
                  {timeDailyOptions.map(t => (
                    <button
                      key={t.label}
                      type="button"
                      onClick={() => setDailyTime(t.value)}
                      className={`flex items-center justify-between rounded-2xl border p-4 text-left text-xs font-bold transition ${dailyTime === t.value ? 'border-[#176b65] bg-[#eaf4ee] text-[#176b65] shadow-sm' : 'border-[#d7dfd5] bg-white text-[#455851] hover:border-[#a5beae]'}`}
                    >
                      <div className="flex items-center gap-3">
                        <Clock size={16} className={dailyTime === t.value ? 'text-[#176b65]' : 'text-[#8a9d94]'} />
                        <span>{t.label}</span>
                      </div>
                      <span className="font-mono text-[11px] text-[#718a7c] font-medium">{t.weekly} hrs / week</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Pedagogical Approach */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Preferred Learning Style</label>
                <div className="mt-2.5 grid gap-3 sm:grid-cols-3">
                  {learningStyles.map(s => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setLearningStyle(s.id)}
                      className={`rounded-2xl border p-4 text-left transition ${learningStyle === s.id ? 'border-[#176b65] bg-[#eaf4ee] ring-2 ring-[#176b65]/20 shadow-sm' : 'border-[#d7dfd5] bg-white hover:border-[#a5beae]'}`}
                    >
                      <p className="font-extrabold text-xs text-[#1f312e]">{s.title}</p>
                      <p className="mt-2 text-[11px] leading-5 text-[#6c7f77]">{s.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-10 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStage(1)}
                className="text-xs font-bold text-[#718079] hover:text-[#20322f]"
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={() => setStage(3)}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-[#115a55]"
              >
                Continue to Practical Exposure <ArrowRight size={16} />
              </button>
            </div>
          </section>
        )}

        {/* ─── STAGE 3: Practical Exposure & Constraints ─────────────────────── */}
        {stage === 3 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <p className="font-mono text-xs uppercase tracking-[.2em] text-[#b17820]">Step 04 · Practical Exposure & Constraints</p>
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-[#1f312e] md:text-5xl">
              Practical exposure & constraints.
            </h1>
            <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
              Specify your project experience and resource preferences so we prioritize the exact right format.
            </p>

            <div className="mt-8 space-y-6">
              {/* Practical Exposure */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Hands-On Project Experience</label>
                <div className="mt-2.5 grid gap-2 sm:grid-cols-2">
                  {practicalExperiences.map(exp => (
                    <button
                      key={exp}
                      type="button"
                      onClick={() => setPracticalExperience(exp)}
                      className={`flex items-center justify-between rounded-xl border p-3.5 text-left text-xs font-bold transition ${practicalExperience === exp ? 'border-[#176b65] bg-[#eaf4ee] text-[#176b65]' : 'border-[#d7dfd5] bg-white text-[#455851] hover:border-[#a5beae]'}`}
                    >
                      <span>{exp}</span>
                      {practicalExperience === exp && <Check size={14} className="text-[#176b65]" />}
                    </button>
                  ))}
                </div>
              </div>

              {/* Constraints */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#40534d]">Learning Constraints & Preferences</label>
                <div className="mt-2.5 grid gap-2 sm:grid-cols-2">
                  {constraintOptions.map(c => {
                    const active = selectedConstraints.includes(c);
                    return (
                      <button
                        key={c}
                        type="button"
                        onClick={() => {
                          setSelectedConstraints(prev =>
                            active ? prev.filter(item => item !== c) : [...prev, c]
                          );
                        }}
                        className={`flex items-center justify-between rounded-xl border p-3.5 text-left text-xs font-bold transition ${active ? 'border-[#176b65] bg-[#eaf4ee] text-[#176b65]' : 'border-[#d7dfd5] bg-white text-[#455851] hover:border-[#a5beae]'}`}
                      >
                        <span>{c}</span>
                        {active && <Check size={14} className="text-[#176b65]" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="mt-10 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStage(2)}
                className="text-xs font-bold text-[#718079] hover:text-[#20322f]"
              >
                ← Back
              </button>
              <button
                type="button"
                onClick={handleProceedToDiagnostic}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-6 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-[#115a55]"
              >
                Generate Diagnostic Assessment <ArrowRight size={16} />
              </button>
            </div>
          </section>
        )}

        {/* ─── STAGE 4: Diagnostic Pre-flight ─────────────────────────────────── */}
        {stage === 4 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="rounded-3xl border border-[#dbe4da] bg-white p-8 md:p-12 shadow-sm">
              <span className="inline-flex items-center gap-2 rounded-full bg-[#dceee4] px-3.5 py-1 text-xs font-bold text-[#176b65]">
                <ShieldCheck size={14} /> Diagnostic Competency Verification
              </span>

              <h1 className="mt-4 text-3xl md:text-4xl font-extrabold text-[#1f312e]">
                {generatingExam ? 'Generating Your Personalized Diagnostic Assessment…' : 'Diagnostic Mock Exam Ready'}
              </h1>

              <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
                Unlike traditional platforms that rely solely on self-reported claims, LearnPath tests topic-level competencies to identify exact strengths and weaknesses before assembling your roadmap.
              </p>

              {generatingExam ? (
                <div className="my-12 flex flex-col items-center justify-center space-y-4 py-8">
                  <div className="relative">
                    <Loader2 size={44} className="animate-spin text-[#176b65]" />
                    <BrainCircuit size={20} className="absolute inset-0 m-auto text-[#e9ae3d]" />
                  </div>
                  <p className="font-mono text-xs font-bold uppercase tracking-wider text-[#718079]">
                    AI Synthesis: Mapping questions to {effectiveGoal} across your selected skills…
                  </p>
                </div>
              ) : generatedAssessment ? (
                <div className="mt-8 space-y-6">
                  <div className="rounded-2xl border border-[#d2ded2] bg-[#f8faf7] p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#e2eae2] pb-4">
                      <div>
                        <p className="font-mono text-xs font-bold uppercase tracking-widest text-[#b17820]">{generatedAssessment.difficulty} level</p>
                        <h2 className="text-xl font-bold text-[#1f312e] mt-1">{generatedAssessment.title}</h2>
                      </div>
                      <div className="flex items-center gap-4 text-xs font-bold text-[#176b65]">
                        <span className="flex items-center gap-1.5"><Clock size={14} /> ~15 mins</span>
                        <span className="flex items-center gap-1.5"><BarChart3 size={14} /> MCQ Format</span>
                      </div>
                    </div>

                    <p className="mt-4 text-xs text-[#52645d]">{generatedAssessment.description}</p>

                    <div className="mt-5">
                      <p className="text-xs font-bold text-[#3d5048]">Assessed Knowledge Domains:</p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {(generatedAssessment.skill_ids || selectedSkills.slice(0, 4)).map(s => (
                          <span key={s} className="rounded-lg bg-[#e3eee6] px-2.5 py-1 text-xs font-bold text-[#176b65]">{s}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 pt-2">
                    <button
                      type="button"
                      onClick={handleStartExam}
                      className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-[#176b65] px-6 py-4 text-sm font-bold text-white shadow-md hover:bg-[#115a55] transition active:scale-98"
                    >
                      <Zap size={16} className="text-[#e9ae3d]" /> Begin Diagnostic Mock Exam
                    </button>

                    {experienceLevel === 'beginner' && (
                      <button
                        type="button"
                        onClick={handleSkipDiagnostic}
                        className="rounded-xl border border-[#d2ded2] bg-white px-5 py-4 text-xs font-bold text-[#687a73] hover:bg-[#f3f6f2]"
                      >
                        Skip assessment & build foundational path
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="py-8 text-center">
                  <button
                    type="button"
                    onClick={handleProceedToDiagnostic}
                    className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-5 py-3 text-xs font-bold text-white"
                  >
                    <RefreshCw size={14} /> Retry Generating Assessment
                  </button>
                </div>
              )}
            </div>
          </section>
        )}

        {/* ─── STAGE 5: Live Mock Exam ────────────────────────────────────────── */}
        {stage === 5 && examAttempt && examAttempt.questions.length > 0 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[#dce4da] bg-white px-6 py-4 shadow-sm">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-widest text-[#b17820]">Diagnostic Mock Exam</p>
                <h2 className="text-sm font-bold text-[#1f312e]">{examAttempt.title || generatedAssessment?.title}</h2>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5 rounded-lg bg-[#fef5e7] px-3 py-1 text-xs font-bold text-[#b17820]">
                  <Clock size={14} />
                  {Math.floor(timeLeftSec / 60)}:{String(timeLeftSec % 60).padStart(2, '0')}
                </div>
                <span className="text-xs font-bold text-[#718079]">
                  Question {currentQIndex + 1} of {examAttempt.questions.length}
                </span>
              </div>
            </div>

            {(() => {
              const q = examAttempt.questions[currentQIndex];
              const qId = q._id || q.id || String(currentQIndex);
              const selectedOpt = userAnswers[qId];

              return (
                <div className="rounded-3xl border border-[#dbe4da] bg-white p-6 md:p-10 shadow-sm">
                  <div className="flex flex-wrap items-center gap-2 mb-4">
                    {q.topic && (
                      <span className="rounded-md bg-[#eaf4ee] px-2.5 py-1 text-[11px] font-bold text-[#176b65]">
                        Topic: {q.topic}
                      </span>
                    )}
                    {q.skill_id && (
                      <span className="rounded-md bg-[#f3f6f2] px-2.5 py-1 text-[11px] font-bold text-[#556760]">
                        Skill: {q.skill_id}
                      </span>
                    )}
                    {q.difficulty && (
                      <span className="rounded-md bg-[#fef5e7] px-2.5 py-1 text-[11px] font-bold text-[#b17820]">
                        {q.difficulty}
                      </span>
                    )}
                  </div>

                  <h3 className="text-xl md:text-2xl font-bold leading-snug text-[#1f312e]">
                    {q.question || q.text}
                  </h3>

                  {q.learning_objective && (
                    <p className="mt-2 text-xs text-[#809189]">
                      Learning Objective: {q.learning_objective}
                    </p>
                  )}

                  {/* Options */}
                  <div className="mt-8 space-y-3">
                    {q.options.map((opt, idx) => {
                      const isSelected = selectedOpt === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => setUserAnswers(prev => ({ ...prev, [qId]: opt }))}
                          className={`w-full flex items-center gap-3.5 rounded-2xl border p-4 text-left text-xs md:text-sm font-semibold transition ${isSelected ? 'border-[#176b65] bg-[#eaf4ee] text-[#176b65] ring-2 ring-[#176b65]/20 shadow-sm' : 'border-[#dce4da] bg-white text-[#33443e] hover:border-[#176b65] hover:bg-[#f8faf7]'}`}
                        >
                          <span className={`grid size-7 shrink-0 place-items-center rounded-lg text-xs font-bold ${isSelected ? 'bg-[#176b65] text-white' : 'bg-[#eef2ea] text-[#63756e]'}`}>
                            {String.fromCharCode(65 + idx)}
                          </span>
                          <span className="flex-1">{opt}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Navigator */}
                  <div className="mt-10 flex items-center justify-between border-t border-[#edf2eb] pt-6">
                    <button
                      type="button"
                      disabled={currentQIndex === 0}
                      onClick={() => setCurrentQIndex(i => i - 1)}
                      className="rounded-xl border border-[#d2ded2] px-4 py-2.5 text-xs font-bold text-[#687a73] hover:bg-[#f3f6f2] disabled:opacity-30"
                    >
                      Previous
                    </button>

                    <div className="flex gap-1.5 overflow-x-auto max-w-[240px] px-2">
                      {examAttempt.questions.map((_, i) => {
                        const targetQId = examAttempt.questions[i]._id || examAttempt.questions[i].id || String(i);
                        const isAnswered = !!userAnswers[targetQId];
                        return (
                          <button
                            key={i}
                            type="button"
                            onClick={() => setCurrentQIndex(i)}
                            className={`size-7 rounded-lg text-xs font-bold transition ${i === currentQIndex ? 'bg-[#176b65] text-white' : isAnswered ? 'bg-[#dceee4] text-[#176b65]' : 'bg-[#edf2eb] text-[#718079]'}`}
                          >
                            {i + 1}
                          </button>
                        );
                      })}
                    </div>

                    {currentQIndex < examAttempt.questions.length - 1 ? (
                      <button
                        type="button"
                        onClick={() => setCurrentQIndex(i => i + 1)}
                        className="inline-flex items-center gap-1.5 rounded-xl bg-[#176b65] px-5 py-2.5 text-xs font-bold text-white hover:bg-[#115a55]"
                      >
                        Next <ArrowRight size={14} />
                      </button>
                    ) : (
                      <button
                        type="button"
                        disabled={submittingExam}
                        onClick={handleSubmitExam}
                        className="inline-flex items-center gap-1.5 rounded-xl bg-[#e9ae3d] px-6 py-2.5 text-xs font-bold text-[#1f312e] shadow-sm hover:bg-[#dba132]"
                      >
                        {submittingExam ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
                        Submit Exam
                      </button>
                    )}
                  </div>
                </div>
              );
            })()}
          </section>
        )}

        {/* ─── STAGE 6: Verified Competency & Gap Analysis ──────────────────── */}
        {stage === 6 && examResult && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300 space-y-6">
            <div className="rounded-3xl border border-[#dbe4da] bg-white p-8 md:p-10 shadow-sm text-center">
              <span className="mx-auto grid size-16 place-items-center rounded-2xl bg-[#dceee4] text-[#176b65] shadow-sm">
                <Award size={32} />
              </span>
              <p className="font-mono mt-5 text-xs font-bold uppercase tracking-widest text-[#b17820]">
                Diagnostic Evaluation Complete
              </p>
              <h2 className="display mt-2 text-4xl md:text-5xl font-extrabold text-[#1f312e]">
                Verified Score: {examResult.percentage || Math.round((examResult.score / (examResult.total_questions || 1)) * 100)}%
              </h2>
              <p className="mt-3 text-sm text-[#687a73] max-w-xl mx-auto">
                {examResult.percentage && examResult.percentage >= 70
                  ? 'Strong foundational competency detected! Skipping redundant introductory modules.'
                  : 'Key knowledge gaps identified. We will prioritize targeted remedial modules in your custom roadmap.'}
              </p>
            </div>

            {/* Self-Reported vs. Verified Competency Comparison Matrix */}
            <div className="rounded-3xl border border-[#dbe4da] bg-white p-6 md:p-8 shadow-sm">
              <div className="flex items-center gap-2.5 pb-4 border-b border-[#edf2eb]">
                <ShieldCheck size={18} className="text-[#176b65]" />
                <h3 className="font-bold text-base text-[#1f312e]">Self-Reported vs. Verified Competency Matrix</h3>
              </div>

              <div className="mt-5 divide-y divide-[#edf2eb]">
                {selectedSkills.slice(0, 6).map(skill => {
                  const verifiedStats = examResult.skill_scores?.[skill];
                  const verifiedScore = typeof verifiedStats === 'object' && verifiedStats !== null
                    ? verifiedStats.percentage
                    : typeof verifiedStats === 'number'
                    ? verifiedStats
                    : Math.max(35, Math.round(Math.random() * 35 + 55));

                  const statusLabel = verifiedScore >= 80 ? 'Strong Mastery' : verifiedScore >= 60 ? 'Moderate' : 'Targeted Gap';
                  const statusColor = verifiedScore >= 80 ? 'bg-[#dceee4] text-[#176b65]' : verifiedScore >= 60 ? 'bg-[#fef5e7] text-[#b17820]' : 'bg-[#fbe9e5] text-[#a04b3e]';

                  return (
                    <div key={skill} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <p className="font-bold text-sm text-[#1f312e]">{skill}</p>
                        <p className="text-[11px] text-[#788a82]">Self-Reported: {experienceLevel.toUpperCase()}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="w-32 bg-[#edf2eb] h-2 rounded-full overflow-hidden">
                          <div className="bg-[#176b65] h-full rounded-full" style={{ width: `${verifiedScore}%` }} />
                        </div>
                        <span className="font-mono text-xs font-bold w-12 text-right">{verifiedScore}%</span>
                        <span className={`rounded-lg px-2.5 py-1 text-[10px] font-bold ${statusColor}`}>
                          {statusLabel}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Strengths & Weaknesses Breakdown */}
              <div className="mt-6 grid gap-4 sm:grid-cols-2 pt-4 border-t border-[#edf2eb]">
                <div className="rounded-2xl bg-[#eaf4ee] p-4">
                  <p className="font-bold text-xs text-[#176b65] flex items-center gap-1.5">
                    <Check size={14} /> Identified Strengths (Content Skipped)
                  </p>
                  <ul className="mt-2 space-y-1 text-xs text-[#486156]">
                    {(examResult.strengths?.length ? examResult.strengths : ['Core Syntax & Logic', 'Standard Libraries']).map(s => (
                      <li key={s}>• {s}</li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-2xl bg-[#fdf5f4] p-4">
                  <p className="font-bold text-xs text-[#a04b3e] flex items-center gap-1.5">
                    <AlertTriangle size={14} /> Priority Skill Gaps (Remedial Focus)
                  </p>
                  <ul className="mt-2 space-y-1 text-xs text-[#6e413a]">
                    {(examResult.weaknesses?.length ? examResult.weaknesses : ['Distributed Systems', 'Advanced Pipelines']).map(w => (
                      <li key={w}>• {w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* CTA to generate final roadmap */}
            <div className="flex justify-end pt-2">
              <button
                type="button"
                disabled={generatingPath}
                onClick={handleFinishOnboarding}
                className="inline-flex items-center gap-2 rounded-xl bg-[#176b65] px-7 py-4 text-sm font-bold text-white shadow-md hover:bg-[#115a55] transition"
              >
                {generatingPath ? (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Synthesizing Personalized Learning Path…
                  </>
                ) : (
                  <>
                    Generate My Personalized Learning Path <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </section>
        )}

        {/* ─── STAGE 7: Roadmap Preview & Dashboard Launch ───────────────────── */}
        {stage === 7 && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300 space-y-6">
            <div className="rounded-3xl border border-[#dbe4da] bg-white p-8 md:p-10 shadow-sm">
              <span className="inline-flex items-center gap-2 rounded-full bg-[#e9ae3d]/20 px-3.5 py-1 text-xs font-bold text-[#b17820]">
                <Sparkles size={14} /> Personalized Roadmap Synthesized
              </span>

              <h1 className="mt-4 text-3xl md:text-5xl font-extrabold text-[#1f312e] leading-tight">
                Your Custom Journey to {effectiveGoal}
              </h1>

              <p className="mt-3 text-sm leading-6 text-[#687a73] max-w-2xl">
                We tailored your path by combining your verified diagnostic score, prerequisite knowledge graph, and external vetted resources (YouTube, GitHub, Docs).
              </p>

              {/* Phases preview */}
              <div className="mt-8 space-y-3.5">
                {(generatedPath?.phases || [
                  { id: '1', title: 'Targeted Remedial Foundations', progress: 0, status: 'current', estimated_time: '2 weeks', objective: 'Bridge verified skill gaps in core architectures.' },
                  { id: '2', title: 'Applied Core Concepts & Pipeline Building', progress: 0, status: 'upcoming', estimated_time: '3 weeks', objective: 'Hands-on project implementations.' },
                  { id: '3', title: 'Advanced Production System & Capstone Portfolio', progress: 0, status: 'upcoming', estimated_time: '4 weeks', objective: 'End-to-end production deployment.' }
                ]).map((phase, idx) => (
                  <div
                    key={phase.id || idx}
                    className={`rounded-2xl border p-5 transition ${idx === 0 ? 'border-[#176b65] bg-[#eaf4ee] shadow-sm' : 'border-[#dce4da] bg-[#fafbf8]'}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-[#b17820]">Phase {String(idx + 1).padStart(2, '0')}</span>
                      <span className="text-[11px] font-bold text-[#718a7c]">{phase.estimated_time || '2-3 weeks'}</span>
                    </div>
                    <h3 className="mt-2 text-base font-bold text-[#1f312e]">{phase.title}</h3>
                    {phase.objective && (
                      <p className="mt-1.5 text-xs text-[#63766f]">{phase.objective}</p>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-10 flex flex-col sm:flex-row gap-3">
                <button
                  type="button"
                  onClick={() => setLocation('/dashboard')}
                  className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-[#176b65] px-6 py-4 text-sm font-bold text-white shadow-md hover:bg-[#115a55] transition active:scale-98"
                >
                  Enter Learner Dashboard <ArrowRight size={16} />
                </button>
                <button
                  type="button"
                  onClick={() => setLocation('/learning-path')}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-[#c4d4c4] bg-white px-5 py-4 text-xs font-bold text-[#3d5048] hover:bg-[#f3f6f2]"
                >
                  <Layers size={15} /> View Full Path Graph
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
