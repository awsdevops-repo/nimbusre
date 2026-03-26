export interface Message {
  id: string
  role: "user" | "bot"
  content: string
  timestamp: Date
  findings?: Record<string, any>
  metadata?: {
    tool?: string
    severity?: string
    status?: string
  }
}

export interface WorkflowState {
  status: "idle" | "loading" | "executing" | "completed" | "failed"
  severity?: "critical" | "high" | "medium" | "low"
  workflowType?: "diagnostic" | "remediation" | "optimization" | "multi_step"
  findings: Record<string, any>
  plannedActions: Action[]
  executedActions: Action[]
}

export interface Action {
  id: string
  toolName: string
  action: string
  parameters: Record<string, any>
  status: "planned" | "executing" | "succeeded" | "failed" | "rolled_back"
  result?: string
  error?: string
  timestamp: string
}

export type SREQueryResult = {
  messages: Message[]
  state: WorkflowState
  remediation_plan?: string
  findings?: Record<string, any>
  error?: string
}
