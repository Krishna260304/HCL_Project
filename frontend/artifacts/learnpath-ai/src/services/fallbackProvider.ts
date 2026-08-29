import {
  mockProfile,
  mockGoals,
  mockSkills,
  mockLearningPath,
  mockRecommendations,
  mockResources,
  mockProjects,
  mockAssessments,
  mockProgress,
  mockNotifications,
  mockConversations,
  mockChatHistory,
} from './mockData';
import type {
  LearnerProfile,
  LearningPath,
  Skill,
  Resource,
  Project,
  Assessment,
  AssessmentAttempt,
  AssessmentResult,
  Recommendation,
  ProgressData,
  Notification,
  ChatMessage,
  ChatConversation,
} from './index';

// Mutable in-memory store for demo session state
let currentProfile: LearnerProfile = { ...mockProfile };
let currentLearningPath: LearningPath = JSON.parse(JSON.stringify(mockLearningPath));
let currentSkills: Skill[] = JSON.parse(JSON.stringify(mockSkills));
let currentRecommendations: Recommendation[] = JSON.parse(JSON.stringify(mockRecommendations));
let currentProjects: Project[] = JSON.parse(JSON.stringify(mockProjects));
let currentProgress: ProgressData = JSON.parse(JSON.stringify(mockProgress));
let currentNotifications: Notification[] = JSON.parse(JSON.stringify(mockNotifications));
let currentChatHistory: ChatMessage[] = JSON.parse(JSON.stringify(mockChatHistory));

export const fallbackProvider = {
  handleAction(action: string, payload: Record<string, unknown> = {}): unknown {
    switch (action) {
      // ─── Auth ─────────────────────────────────────────────────────────────
      case 'auth.login':
      case 'auth.register': {
        const email = (payload.email as string) || 'alex.rivera@example.com';
        const name = (payload.name as string) || email.split('@')[0];
        currentProfile.name = name;
        return {
          user: {
            id: 'usr_demo_01',
            email,
            role: 'learner',
            status: 'active',
            profile_id: 'prof_demo_01',
          },
          tokens: {
            access_token: 'demo_access_token_' + Date.now(),
            refresh_token: 'demo_refresh_token_' + Date.now(),
            token_type: 'Bearer',
            expires_in: 86400,
          },
        };
      }
      case 'auth.refresh': {
        return {
          access_token: 'demo_access_token_' + Date.now(),
        };
      }
      case 'auth.logout':
        return { success: true };

      // ─── Profile ──────────────────────────────────────────────────────────
      case 'profile.get':
        return { ...currentProfile };

      case 'profile.update': {
        currentProfile = { ...currentProfile, ...payload };
        return { ...currentProfile };
      }

      // ─── Goals ────────────────────────────────────────────────────────────
      case 'goal.list':
        return [...mockGoals];

      case 'goal.create': {
        const newGoal = {
          id: 'goal_' + Date.now(),
          title: (payload.title as string) || 'Custom Goal',
          description: payload.description as string,
          target_role: payload.target_role as string,
          timeline: (payload.timeline as string) || '3 months',
          status: 'in_progress',
        };
        return newGoal;
      }

      case 'goal.analyze': {
        const desc = (payload.description as string) || '';
        return {
          target_role: 'Full-Stack Web & AI Application Architect',
          extracted_skills: ['TypeScript', 'React', 'Node.js', 'PostgreSQL', 'System Design', 'AI Orchestration'],
          difficulty: 'Intermediate–Advanced',
          timeline_recommendation: '14 Weeks (10 hrs/week)',
          domains: ['Web Engineering', 'Cloud Databases', 'Distributed Systems', 'Generative AI'],
          summary: `Your goal "${desc || 'Full-Stack & AI Systems'}" has been analyzed. A structured 5-phase pathway with prerequisite checkpoints has been constructed.`,
        };
      }

      // ─── Skills ───────────────────────────────────────────────────────────
      case 'skill.list':
        return [...currentSkills];

      case 'skill.get': {
        const id = payload.skill_id as string;
        return currentSkills.find(s => s.id === id || s.name === id) || currentSkills[0];
      }

      case 'skill.graph':
        return {
          nodes: currentSkills.map(s => ({ id: s.id, name: s.name, category: s.category, status: s.status })),
          edges: [
            { source: 'sk_js', target: 'sk_react', type: 'prerequisite' },
            { source: 'sk_js', target: 'sk_apis', type: 'prerequisite' },
            { source: 'sk_sql', target: 'sk_apis', type: 'relates_to' },
            { source: 'sk_apis', target: 'sk_auth', type: 'prerequisite' },
            { source: 'sk_apis', target: 'sk_sysdesign', type: 'prerequisite' },
            { source: 'sk_apis', target: 'sk_rag', type: 'prerequisite' },
          ],
        };

      // ─── Learning Path ────────────────────────────────────────────────────
      case 'learning_path.get':
        return { ...currentLearningPath };

      case 'learning_path.generate': {
        const goal = (payload.goal as string) || currentProfile.goals?.[0] || 'Full-Stack Web & AI Architect';
        currentLearningPath.goal = goal;
        return { ...currentLearningPath };
      }

      case 'learning_path.phase.complete': {
        const phaseId = payload.phase_id as string;
        const phaseIndex = currentLearningPath.phases.findIndex(p => p.id === phaseId);
        if (phaseIndex !== -1) {
          currentLearningPath.phases[phaseIndex].status = 'complete';
          currentLearningPath.phases[phaseIndex].progress = 100;
          if (phaseIndex + 1 < currentLearningPath.phases.length) {
            currentLearningPath.phases[phaseIndex + 1].status = 'current';
            currentLearningPath.current_phase = currentLearningPath.phases[phaseIndex + 1].id;
          }
          // Recalculate total progress
          const total = currentLearningPath.phases.reduce((acc, p) => acc + p.progress, 0);
          currentLearningPath.total_progress = Math.round(total / currentLearningPath.phases.length);
          currentProgress.overall_progress = currentLearningPath.total_progress;
        }
        return { status: 'success' };
      }

      // ─── Recommendations ──────────────────────────────────────────────────
      case 'recommendation.list':
        return [...currentRecommendations];

      case 'recommendation.update_status': {
        const recId = payload.recommendation_id as string;
        const status = payload.status as Recommendation['status'];
        const rec = currentRecommendations.find(r => r.id === recId);
        if (rec) rec.status = status;
        return { status: 'success' };
      }

      // ─── Resources ────────────────────────────────────────────────────────
      case 'resource.list':
      case 'resource.search':
        return [...mockResources];

      case 'resource.get': {
        const id = payload.resource_id as string;
        return mockResources.find(r => r.id === id) || mockResources[0];
      }

      // ─── Projects ─────────────────────────────────────────────────────────
      case 'project.list':
        return [...currentProjects];

      case 'project.get': {
        const id = payload.project_id as string;
        return currentProjects.find(p => p.id === id) || currentProjects[0];
      }

      // ─── Assessments ──────────────────────────────────────────────────────
      case 'assessment.list':
        return [...mockAssessments];

      case 'assessment.get': {
        const id = payload.assessment_id as string;
        return mockAssessments.find(a => a.id === id) || mockAssessments[0];
      }

      case 'assessment.requirements':
        return {
          assessment_required: false,
          reason: 'Diagnostic verified from onboarding profile.',
        };

      case 'assessment.start': {
        const id = payload.assessment_id as string;
        return {
          attempt_id: 'att_' + Date.now(),
          assessment_id: id,
          title: 'API Security & Architecture Checkpoint',
          duration: 20,
          questions: [
            {
              id: 'q1',
              text: 'Where should sensitive JWT refresh tokens ideally be stored in a secure browser single-page app?',
              options: [
                'In an HttpOnly, Secure, SameSite=Strict cookie',
                'In browser localStorage or sessionStorage',
                'In a global JavaScript window variable',
                'In URL query parameters',
              ],
              learning_objective: 'Token Security & Storage Best Practices',
            },
            {
              id: 'q2',
              text: 'What is the primary architectural purpose of a reverse proxy like Nginx or Traefik in front of application instances?',
              options: [
                'TLS termination, load balancing, caching, and rate limiting',
                'Running database migrations automatically',
                'Compiling React TypeScript bundles in real-time',
                'Executing vector embeddings for semantic search',
              ],
              learning_objective: 'System Architecture & Infrastructure',
            },
            {
              id: 'q3',
              text: 'How does an event-driven message queue (e.g. RabbitMQ, Kafka) improve system resilience under peak load?',
              options: [
                'By decoupling producers from consumers and buffering spikes asynchronously',
                'By converting all HTTP GET requests to WebSockets',
                'By automatically indexing all relational database tables',
                'By enforcing single-threaded CPU execution',
              ],
              learning_objective: 'Distributed Systems & Queueing',
            },
          ],
        } satisfies AssessmentAttempt;
      }

      case 'assessment.submit': {
        return {
          attempt_id: (payload.attempt_id as string) || 'att_done',
          score: 100,
          percentage: 100,
          passed: true,
          feedback: 'Excellent grasp of backend security, proxy architecture, and async message queue patterns.',
          strengths: ['HTTP Security & Cookies', 'Reverse Proxy Routing', 'Decoupled Message Queues'],
          weaknesses: [],
        } satisfies AssessmentResult;
      }

      // ─── Progress ─────────────────────────────────────────────────────────
      case 'progress.get':
        return { ...currentProgress };

      case 'progress.skills':
        return [...currentSkills];

      case 'progress.activity':
        return currentProgress.activity;

      case 'progress.update': {
        currentProgress = { ...currentProgress, ...payload };
        return { status: 'success' };
      }

      // ─── Notifications ────────────────────────────────────────────────────
      case 'notification.list':
        return [...currentNotifications];

      case 'notification.mark_read': {
        const id = payload.notification_id as string;
        const notif = currentNotifications.find(n => n.id === id);
        if (notif) notif.read = true;
        return { status: 'success' };
      }

      case 'notification.mark_all_read': {
        currentNotifications.forEach(n => { n.read = true; });
        return { status: 'success' };
      }

      // ─── Chat / Assistant ─────────────────────────────────────────────────
      case 'chat.create_conversation': {
        const conv: ChatConversation = {
          id: 'conv_' + Date.now(),
          title: (payload.title as string) || 'Learning Coach Session',
          created_at: new Date().toISOString(),
          last_message: 'Session initiated',
        };
        return conv;
      }

      case 'chat.conversations':
        return [...mockConversations];

      case 'chat.history':
        return [...currentChatHistory];

      case 'chat.send': {
        const msgText = (payload.message as string) || '';
        const userMsg: ChatMessage = {
          id: 'msg_' + Date.now(),
          from: 'user',
          text: msgText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        currentChatHistory.push(userMsg);

        // Generate contextual AI response
        let aiReply = '';
        const lower = msgText.toLowerCase();

        if (lower.includes('current phase') || lower.includes('what am i learning') || lower.includes('where am i')) {
          aiReply = `You are currently in **Phase 3: Backend API Architecture & Security**. In this phase, you are closing the gap on REST API design, JWT authentication, and WebSocket communication before moving into Distributed Systems in Phase 4.`;
        } else if (lower.includes('why') && (lower.includes('sql') || lower.includes('jwt') || lower.includes('next'))) {
          aiReply = `You are focusing on **API Security & JWT Token Rotation** right now because your skill assessment identified a 40% gap in security protocols. Securing backend endpoints is a strict prerequisite for your upcoming *Production Gateway* project.`;
        } else if (lower.includes('skip') || lower.includes('faster')) {
          aiReply = `If you already feel confident with REST conventions, you can take the **Phase 3 Diagnostic Checkpoint**. Achieving an 85%+ score will automatically mark Phase 3 as mastered and advance your roadmap to **Phase 4: Distributed Systems & Caching**.`;
        } else if (lower.includes('struggling') || lower.includes('help') || lower.includes('difficult')) {
          aiReply = `No problem! I've flagged the *JWT Authentication & Refresh Token Rotation Sandbox* resource for you. It includes an interactive visual simulator breaking down the token handshake step-by-step.`;
        } else if (lower.includes('next') || lower.includes('build')) {
          aiReply = `Your next high-impact action is **Build your Production-Grade REST & WebSocket Gateway**. This project synthesizes everything you've learned in Phases 1–3 and provides verified proof for your portfolio.`;
        } else {
          aiReply = `Based on your goal (*Full-Stack Web & AI Architect*) and your progress in Phase 3 (42% overall path complete), I recommend finishing the active API security milestone. What specific concept would you like to explore deeper?`;
        }

        const assistantMsg: ChatMessage = {
          id: 'msg_' + (Date.now() + 1),
          from: 'assistant',
          text: aiReply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        currentChatHistory.push(assistantMsg);

        return {
          reply: aiReply,
          conversation_id: payload.conversation_id || 'conv_default',
          sources: [
            { title: 'Personalized Roadmap — Phase 3' },
            { title: 'Full-Stack Skill Gap Matrix' },
          ],
        };
      }

      // ─── Onboarding ───────────────────────────────────────────────────────
      case 'onboarding.get':
        return {
          user_id: 'usr_demo_01',
          current_step: 1,
          completed_steps: [1],
          answers: {},
          status: 'in_progress',
        };

      case 'onboarding.save_step':
      case 'onboarding.complete':
        return { status: 'completed' };

      case 'onboarding.questions':
        return [];

      default:
        return { status: 'success', action };
    }
  },
};
