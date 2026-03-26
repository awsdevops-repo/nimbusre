import { create } from "zustand"
import type { Message, WorkflowState } from "./types"

interface ChatStore {
  messages: Message[]
  workflowState: WorkflowState
  isLoading: boolean
  addMessage: (message: Message) => void
  updateWorkflowState: (state: Partial<WorkflowState>) => void
  setLoading: (loading: boolean) => void
  clearChat: () => void
  getRecentQueries: () => string[]
}

const initialWorkflowState: WorkflowState = {
  status: "idle",
  findings: {},
  plannedActions: [],
  executedActions: [],
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  workflowState: initialWorkflowState,
  isLoading: false,

  addMessage: (message: Message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateWorkflowState: (state: Partial<WorkflowState>) =>
    set((current) => ({
      workflowState: {
        ...current.workflowState,
        ...state,
      },
    })),

  setLoading: (loading: boolean) =>
    set({ isLoading: loading }),

  clearChat: () =>
    set({
      messages: [],
      workflowState: initialWorkflowState,
      isLoading: false,
    }),

  getRecentQueries: () => {
    const { messages } = get()
    return messages
      .filter((m) => m.role === "user")
      .slice(-5)
      .map((m) => m.content)
      .reverse()
  },
}))
