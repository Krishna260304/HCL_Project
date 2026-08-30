import { wsManager } from './websocket/WebSocketManager';

function unwrapList<T>(value: T[] | Record<string, T[] | undefined> | null | undefined, keys: string[]): T[] {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  for (const key of keys) if (Array.isArray(value[key])) return value[key] as T[];
  return [];
}

// ─── Profile types ────────────────────────────────────────────────────────────

export interface LearnerProfile {
  user_id: string;
  name: string;
  age_range?: string;
  country?: string;
  language?: string;
  education?: string | null;
  academic_background?: string | null;
  current_status?: string | null;
  current_role?: string | null;
  experience_years?: number;
  experience_level?: string;
  goals?: string[];
  interests?: string[];
  knowledge_areas?: string[];
  learning_preferences?: Record<string, unknown>;
  learning_constraints?: Record<string, unknown>;
  motivation?: string | null;
  target_outcome?: string | null;
  timeline?: string | null;
  available_hours?: number;
  learning_history?: unknown[];
  practical_experience?: unknown[];
  self_reported_skills?: string[];
  verified_skills?: string[];
}

export const profileService = {
  async getProfile(): Promise<LearnerProfile> {
    return wsManager.request<LearnerProfile>('profile.get', {});
  },

  async updateProfile(updates: Partial<LearnerProfile>): Promise<LearnerProfile> {
    return wsManager.request<LearnerProfile>('profile.update', updates as Record<string, unknown>);
  },
};

// ─── Onboarding types ─────────────────────────────────────────────────────────

export interface OnboardingSession {
  user_id: string;
  current_step: number;
  completed_steps: number[];
  answers: Record<string, unknown>;
  status: 'in_progress' | 'completed';
}

export const onboardingService = {
  async getSession(): Promise<OnboardingSession> {
    return wsManager.request<OnboardingSession>('onboarding.get', {});
  },

  async saveStep(step: number, data: Record<string, unknown>): Promise<OnboardingSession> {
    return wsManager.request<OnboardingSession>('onboarding.save_step', { step, data });
  },

  async complete(finalData?: Record<string, unknown>): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('onboarding.complete', finalData ?? {});
  },

  async getQuestions(): Promise<unknown[]> {
    return wsManager.request<unknown[]>('onboarding.questions', {});
  },
};

// ─── Goal types ───────────────────────────────────────────────────────────────

export interface Goal {
  id: string;
  title: string;
  description?: string;
  target_role?: string;
  timeline?: string;
  status?: string;
}

export const goalService = {
  async listGoals(): Promise<Goal[]> {
    return unwrapList(await wsManager.request<Goal[] | { goals?: Goal[] }>('goal.list', {}), ['goals']);
  },

  async createGoal(payload: Partial<Goal>): Promise<Goal> {
    return wsManager.request<Goal>('goal.create', payload as Record<string, unknown>);
  },

  async updateGoal(goalId: string, updates: Partial<Goal>): Promise<Goal> {
    return wsManager.request<Goal>('goal.update', { goal_id: goalId, ...updates });
  },

  async analyzeGoal(description: string): Promise<{
    target_role?: string;
    extracted_skills?: string[];
    difficulty?: string;
    timeline_recommendation?: string;
    domains?: string[];
    summary?: string;
  }> {
    return wsManager.request('goal.analyze', { description });
  },
};

// ─── Skill types ──────────────────────────────────────────────────────────────

export interface Skill {
  id: string;
  name: string;
  category?: string;
  difficulty?: string;
  description?: string;
  prerequisites?: string[];
  self_score?: number;
  verified_score?: number;
  required_score?: number;
  confidence?: string;
  status?: string;
  gap?: number;
  last_assessed?: string | null;
}

export interface SkillGraph {
  nodes: Array<{ id: string; name: string; category?: string; status?: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
}

export const skillService = {
  async listSkills(payload: Record<string, unknown> = {}): Promise<Skill[]> {
    return unwrapList(await wsManager.request<Skill[] | { skills?: Skill[] }>('skill.list', payload), ['skills']);
  },

  async getSkill(skillId: string): Promise<Skill> {
    return wsManager.request<Skill>('skill.get', { skill_id: skillId });
  },

  async getSkillGraph(): Promise<SkillGraph> {
    return wsManager.request<SkillGraph>('skill.graph', {});
  },
};

// ─── Resource types ───────────────────────────────────────────────────────────

export interface Resource {
  id: string;
  title: string;
  source?: string;
  type?: string;
  difficulty?: string;
  duration?: string;
  url?: string;
  skills?: string[];
  rating?: number;
  reason?: string;
  status?: string;
  quality_score?: number;
}

export const resourceService = {
  async listResources(payload: Record<string, unknown> = {}): Promise<Resource[]> {
    return unwrapList(await wsManager.request<Resource[] | { resources?: Resource[] }>('resource.list', payload), ['resources']);
  },

  async searchResources(query: string, filters: Record<string, unknown> = {}): Promise<Resource[]> {
    return unwrapList(await wsManager.request<Resource[] | { resources?: Resource[] }>('resource.search', { query, ...filters }), ['resources']);
  },

  async getResource(resourceId: string): Promise<Resource> {
    return wsManager.request<Resource>('resource.get', { resource_id: resourceId });
  },
};

// ─── Project types ────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  title: string;
  type?: string;
  description?: string;
  skills?: string[];
  estimated_time?: string;
  status?: string;
  reason?: string;
}

export const projectService = {
  async listProjects(payload: Record<string, unknown> = {}): Promise<Project[]> {
    return unwrapList(await wsManager.request<Project[] | { projects?: Project[] }>('project.list', payload), ['projects']);
  },

  async getProject(projectId: string): Promise<Project> {
    return wsManager.request<Project>('project.get', { project_id: projectId });
  },
};

// ─── Assessment types ─────────────────────────────────────────────────────────

export interface Assessment {
  id: string;
  title?: string;
  description?: string;
  topic?: string;
  skill?: string;
  skill_ids?: string[];
  difficulty?: string;
  questions_count?: number;
  average_score?: number;
  status?: string;
  latest_attempt?: {
    score?: number;
    date?: string;
    status?: string;
  } | null;
}

export interface AssessmentQuestion {
  id?: string;
  _id?: string;
  question?: string;
  text?: string;
  options: string[];
  type?: string;
  order?: number;
  skill_id?: string;
  topic?: string;
  difficulty?: string;
  learning_objective?: string;
  explanation?: string;
}

export interface AssessmentAttempt {
  attempt_id: string;
  assessment_id: string;
  title?: string;
  duration?: number;
  questions: AssessmentQuestion[];
  started_at?: string;
}

export interface AssessmentResult {
  attempt_id: string;
  assessment_id?: string;
  score: number;
  percentage?: number;
  total_questions?: number;
  passed?: boolean;
  skill_scores?: Record<string, { total?: number; correct?: number; percentage: number } | number>;
  topic_scores?: Record<string, { total?: number; correct?: number; percentage: number } | number>;
  strengths?: string[];
  weaknesses?: string[];
  feedback?: string;
  detailed_breakdown?: Array<{
    question_id?: string;
    skill_id?: string;
    topic?: string;
    is_correct?: boolean;
    submitted_answer?: string;
    explanation?: string;
  }>;
}

export const assessmentService = {
  async listAssessments(payload: Record<string, unknown> = {}): Promise<Assessment[]> {
    return unwrapList(await wsManager.request<Assessment[] | { assessments?: Assessment[] }>('assessment.list', payload), ['assessments']);
  },

  async getAssessment(assessmentId: string): Promise<Assessment> {
    return wsManager.request<Assessment>('assessment.get', { assessment_id: assessmentId });
  },

  async checkRequirements(): Promise<{
    assessment_required: boolean;
    reason: string;
    assessment_type?: string | null;
    message?: string;
  }> {
    return wsManager.request('assessment.requirements', {});
  },

  async generateDiagnosticAI(payload: {
    skills?: string[];
    goal?: string;
    difficulty?: string;
    experience_level?: string;
    num_questions?: number;
  }): Promise<Assessment> {
    const numQuestions = Math.min(10, Math.max(5, payload.num_questions ?? 5));
    return wsManager.request<Assessment>('assessment.generate_ai', { ...payload, num_questions: numQuestions }, 45_000);
  },

  async startAttempt(assessmentId: string): Promise<AssessmentAttempt> {
    return wsManager.request<AssessmentAttempt>('assessment.start', { assessment_id: assessmentId });
  },

  async submitAttempt(
    assessmentId: string,
    attemptId: string,
    answers: Record<string, string>,
  ): Promise<AssessmentResult> {
    return wsManager.request<AssessmentResult>('assessment.submit', {
      assessment_id: assessmentId,
      attempt_id: attemptId,
      answers,
    });
  },

  async getResult(attemptId: string): Promise<AssessmentResult> {
    return wsManager.request<AssessmentResult>('assessment.result', { attempt_id: attemptId });
  },
};

// ─── Learning path types ──────────────────────────────────────────────────────

export interface LearningPathPhase {
  id: string;
  title: string;
  objective?: string;
  status: 'complete' | 'current' | 'upcoming' | 'skipped';
  progress: number;
  skills?: string[];
  resources?: string[];
  project?: string;
  assessment?: string;
  estimated_time?: string;
  order?: number;
}

export interface LearningPath {
  id: string;
  goal: string;
  duration?: string;
  total_progress?: number;
  current_phase?: string | null;
  phases: LearningPathPhase[];
  created_at?: string;
}

export const learningPathService = {
  async getLearningPath(): Promise<LearningPath> {
    const result = await wsManager.request<LearningPath | { learning_path?: LearningPath }>('learning_path.get', {});
    return ('learning_path' in result ? result.learning_path : result) as LearningPath;
  },

  async generateLearningPath(payload: Record<string, unknown> = {}): Promise<LearningPath> {
    return wsManager.request<LearningPath>('learning_path.generate', payload, 60_000);
  },

  async completePhase(phaseId: string): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('learning_path.phase.complete', { phase_id: phaseId });
  },

  async skipPhase(phaseId: string, reason?: string): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('learning_path.phase.skip', {
      phase_id: phaseId,
      reason,
    });
  },
};

// ─── Recommendation types ─────────────────────────────────────────────────────

export interface Recommendation {
  id: string;
  resource_id?: string;
  resource_title?: string;
  source?: string;
  skill?: string;
  score?: number;
  reason?: string;
  difficulty?: string;
  duration?: string;
  type?: string;
  status?: 'pending' | 'accepted' | 'skipped' | 'completed';
}

export const recommendationService = {
  async listRecommendations(payload: Record<string, unknown> = {}): Promise<Recommendation[]> {
    return wsManager.request<Recommendation[]>('recommendation.list', payload);
  },

  async updateStatus(recId: string, status: string): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('recommendation.update_status', {
      recommendation_id: recId,
      status,
    });
  },
};

// ─── Progress types ───────────────────────────────────────────────────────────

export interface ProgressData {
  total_hours?: number;
  learning_streak?: number;
  completed_resources?: number;
  completed_projects?: number;
  completed_assessments?: number;
  overall_progress?: number;
  current_phase?: string | null;
  weekly_data?: Array<{ week: string; hours: number; score: number; progress: number }>;
  skill_progress?: Array<{ name: string; self: number; verified: number; required: number }>;
  activity?: ProgressActivity[];
  average_score?: number;
}

export interface ProgressActivity {
  action?: string;
  item_id?: string;
  timestamp?: string;
  type?: string;
  resource_id?: string;
  assessment_id?: string;
  progress_percentage?: number;
}

interface ProgressRecord {
  time_spent?: number;
  progress_percentage?: number;
  status?: string;
  [key: string]: unknown;
}

export const progressService = {
  async getProgress(): Promise<ProgressData> {
    const response = await wsManager.request<ProgressData | { progress?: ProgressRecord | null; progress_list?: ProgressRecord[] }>('progress.get', {});
    if ('progress' in response && response.progress) {
      return {
        ...response.progress,
        total_hours: Number(response.progress.time_spent ?? 0) / 60,
        overall_progress: Number(response.progress.progress_percentage ?? 0),
      };
    }
    if ('progress_list' in response) {
      const rows = response.progress_list ?? [];
      const totalMinutes = rows.reduce((sum, row) => sum + Number(row.time_spent ?? 0), 0);
      const progress = rows.length > 0
        ? rows.reduce((sum, row) => sum + Number(row.progress_percentage ?? 0), 0) / rows.length
        : 0;
      return { total_hours: totalMinutes / 60, overall_progress: Math.round(progress) };
    }
    return response as ProgressData;
  },

  async updateProgress(payload: Record<string, unknown>): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('progress.update', payload);
  },

  async getSkillProgress(): Promise<Skill[]> {
    return unwrapList(await wsManager.request<Skill[] | { skill_progress?: Skill[] }>('progress.skills', {}), ['skill_progress']);
  },

  async getActivity(): Promise<ProgressActivity[]> {
    return unwrapList(await wsManager.request<ProgressActivity[] | { activity?: ProgressActivity[] }>('progress.activity', {}), ['activity']);
  },
};

// ─── Notification types ───────────────────────────────────────────────────────

export interface Notification {
  id: string;
  title: string;
  body?: string;
  type?: string;
  read?: boolean;
  created_at?: string;
}

export const notificationService = {
  async listNotifications(payload: Record<string, unknown> = {}): Promise<Notification[]> {
    return unwrapList(await wsManager.request<Notification[] | { notifications?: Notification[] }>('notification.list', payload), ['notifications']);
  },

  async markRead(notificationId: string): Promise<void> {
    await wsManager.request('notification.mark_read', { notification_id: notificationId });
  },

  async markAllRead(): Promise<void> {
    await wsManager.request('notification.mark_all_read', {});
  },

  onNew(callback: (notification: Notification) => void): () => void {
    return wsManager.on('notification.created', (data) => callback(data as Notification));
  },
};

// ─── Chat types ───────────────────────────────────────────────────────────────

export interface ChatMessage {
  id?: string;
  from: 'user' | 'assistant';
  text: string;
  timestamp?: string;
  sources?: Array<{ title: string; url?: string }>;
}

export interface ChatConversation {
  id: string;
  title?: string;
  created_at?: string;
  last_message?: string;
}

export const chatService = {
  async sendMessage(
    conversationId: string,
    message: string,
  ): Promise<{ reply: string; conversation_id: string; sources?: unknown[] }> {
    const result = await wsManager.request<{
      reply?: string;
      assistant_message?: { content?: string };
      conversation_id?: string;
      sources?: unknown[];
      recommended_actions?: unknown[];
    }>(
      'chat.send',
      { conversation_id: conversationId, message },
      60_000,
    );
    return {
      reply: result.reply || result.assistant_message?.content || 'I could not generate a response yet.',
      conversation_id: result.conversation_id || conversationId,
      sources: result.sources,
    };
  },

  async listConversations(): Promise<ChatConversation[]> {
    const result = await wsManager.request<{ conversations?: ChatConversation[] } | ChatConversation[]>('chat.conversations', {});
    return Array.isArray(result) ? result : result.conversations ?? [];
  },

  async getHistory(conversationId: string): Promise<ChatMessage[]> {
    const result = await wsManager.request<{ messages?: ChatMessage[] } | ChatMessage[]>('chat.history', { conversation_id: conversationId });
    return Array.isArray(result) ? result : result.messages ?? [];
  },

  async createConversation(title?: string): Promise<ChatConversation> {
    return wsManager.request<ChatConversation>('chat.create_conversation', { title });
  },

  onMessageDelta(callback: (data: unknown) => void): () => void {
    return wsManager.on('chat.message.delta', callback);
  },
};

// ─── Admin service ────────────────────────────────────────────────────────────

export interface AdminUser {
  id: string;
  name?: string;
  email: string;
  role?: string;
  status?: string;
  progress?: number;
  joined?: string;
  last_active?: string;
  goal?: string;
  experience?: string;
}

export interface AdminAnalytics {
  total_learners?: number;
  active_this_week?: number;
  paths_generated?: number;
  resources_live?: number;
  assessments_taken?: number;
  ai_conversations?: number;
  skills_in_catalog?: number;
  projects_shipped?: number;
  recent_activities?: Array<{ event: string; time: string; actor: string; tag?: string }>;
  weekly_signups?: number[];
  weekly_active?: number[];
  weeks?: string[];
  top_goals?: Array<{ goal: string; percentage: number }>;
  top_skills?: Array<{ skill: string; learners: number }>;
}

export const adminService = {
  async listUsers(payload: Record<string, unknown> = {}): Promise<AdminUser[]> {
    const res = await wsManager.request<{ users: AdminUser[] } | AdminUser[]>('admin.users.list', payload);
    return Array.isArray(res) ? res : (res as { users: AdminUser[] }).users ?? [];
  },

  async getUser(userId: string): Promise<AdminUser> {
    return wsManager.request<AdminUser>('admin.users.get', { user_id: userId });
  },

  async updateUserStatus(userId: string, status: string): Promise<{ status: string }> {
    return wsManager.request<{ status: string }>('admin.users.update_status', {
      user_id: userId,
      status,
    });
  },

  async deleteUser(userId: string): Promise<void> {
    await wsManager.request('admin.users.delete', { user_id: userId });
  },

  async getAnalyticsOverview(): Promise<AdminAnalytics> {
    return wsManager.request<AdminAnalytics>('admin.analytics.overview', {});
  },

  async listAuditLogs(payload: Record<string, unknown> = {}): Promise<unknown[]> {
    const result = await wsManager.request<unknown[] | { audit_logs?: unknown[] }>('admin.audit.list', payload);
    return unwrapList(result, ['audit_logs']);
  },

  async listLearningPaths(payload: Record<string, unknown> = {}): Promise<unknown[]> {
    const result = await wsManager.request<unknown[] | { learning_paths?: unknown[] }>('admin.learning_paths.list', payload);
    return unwrapList(result, ['learning_paths']);
  },

  async adminListCourses(payload: Record<string, unknown> = {}): Promise<any[]> {
    const result = await wsManager.request<any[] | { courses?: any[] }>('course.list', payload);
    return unwrapList(result, ['courses']);
  },

  async listRecommendations(payload: Record<string, unknown> = {}): Promise<any[]> {
    const result = await wsManager.request<any[] | { recommendations?: any[] }>('admin.recommendations.list', payload);
    return unwrapList(result, ['recommendations']);
  },

  async getSettings(): Promise<Record<string, unknown>> {
    return wsManager.request<Record<string, unknown>>('admin.settings.get', {});
  },

  async updateSettings(settings: Record<string, unknown>): Promise<Record<string, unknown>> {
    return wsManager.request<Record<string, unknown>>('admin.settings.update', settings);
  },

  async listFeatureFlags(): Promise<unknown[]> {
    return wsManager.request<unknown[]>('admin.feature_flags.list', {});
  },

  async updateFeatureFlag(key: string, enabled: boolean): Promise<void> {
    await wsManager.request('admin.feature_flags.update', { key, enabled });
  },

  // Resources
  async adminListResources(payload: Record<string, unknown> = {}): Promise<Resource[]> {
    return unwrapList(await wsManager.request<Resource[] | { resources?: Resource[] }>('resource.list', payload), ['resources']);
  },
  async approveResource(resourceId: string): Promise<void> {
    await wsManager.request('admin.resources.approve', { resource_id: resourceId });
  },
  async rejectResource(resourceId: string): Promise<void> {
    await wsManager.request('admin.resources.reject', { resource_id: resourceId });
  },
  async createResource(payload: Record<string, unknown>): Promise<Resource> {
    return wsManager.request<Resource>('admin.resources.create', payload);
  },
  async updateResource(resourceId: string, updates: Record<string, unknown>): Promise<Resource> {
    return wsManager.request<Resource>('admin.resources.update', { resource_id: resourceId, ...updates });
  },
  async deleteResource(resourceId: string): Promise<void> {
    await wsManager.request('admin.resources.delete', { resource_id: resourceId });
  },

  // Skills
  async adminListSkills(payload: Record<string, unknown> = {}): Promise<Skill[]> {
    return unwrapList(await wsManager.request<Skill[] | { skills?: Skill[] }>('skill.list', payload), ['skills']);
  },
  async createSkill(payload: Record<string, unknown>): Promise<Skill> {
    return wsManager.request<Skill>('admin.skills.create', payload);
  },
  async updateSkill(skillId: string, updates: Record<string, unknown>): Promise<Skill> {
    return wsManager.request<Skill>('admin.skills.update', { skill_id: skillId, ...updates });
  },
  async deleteSkill(skillId: string): Promise<void> {
    await wsManager.request('admin.skills.delete', { skill_id: skillId });
  },

  // Assessments
  async adminListAssessments(payload: Record<string, unknown> = {}): Promise<Assessment[]> {
    return unwrapList(await wsManager.request<Assessment[] | { assessments?: Assessment[] }>('assessment.list', payload), ['assessments']);
  },
  async createAssessment(payload: Record<string, unknown>): Promise<Assessment> {
    return wsManager.request<Assessment>('admin.assessments.create', payload);
  },
  async updateAssessment(assessmentId: string, updates: Record<string, unknown>): Promise<Assessment> {
    return wsManager.request<Assessment>('admin.assessments.update', { assessment_id: assessmentId, ...updates });
  },
  async deleteAssessment(assessmentId: string): Promise<void> {
    await wsManager.request('admin.assessments.delete', { assessment_id: assessmentId });
  },

  // Notifications (admin)
  async adminListNotifications(payload: Record<string, unknown> = {}): Promise<Notification[]> {
    return unwrapList(await wsManager.request<Notification[] | { notifications?: Notification[] }>('notification.list', payload), ['notifications']);
  },

  onUserUpdated(callback: (data: unknown) => void): () => void {
    return wsManager.on('admin.user.updated', callback);
  },
  onResourceUpdated(callback: (data: unknown) => void): () => void {
    return wsManager.on('admin.resource.updated', callback);
  },
  onSettingsUpdated(callback: (data: unknown) => void): () => void {
    return wsManager.on('admin.settings.updated', callback);
  },
};
